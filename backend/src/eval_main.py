"""
将数据转换为各种希望的格式
1、对数据格式要有代码层面清晰的描述
2、形成转换路径代码工具

先手动构造  “评估指标输入格式”
coco --> evaluate_format
coco 格式的预测
coco 格式的真实值

## 真实值
gt_bboxes: Any  # torch.Tensor of shape (M, 4)
gt_cls: Any  # torch.Tensor of shape (M,)
gt_masks: Any  # torch.Tensor | None of shape (M, H, W)

## 预测值
detections: Any  # torch.Tensor of shape (N, 6)
pred_masks: Any  # torch.Tensor | None of shape (N, H, W)

定义类，从各种模式初始化为 coco 格式
再从 coco 格式 得到其他格式输出

TODO:
    关键属性的部分改为显式赋值，不要把所有逻辑都叠加再  prepare_pair 中。

"""
import json
import tempfile
from pydantic_core._pydantic_core import ValidationError
import numpy as np
import time
import logging
from typing import Any, Dict, Union, Optional
from  pycocotools.coco import COCO
from src.labelme2coco import  single_file
from src.formats import coco_format
from src.val import _process_batch, match_predictions, match_predictions_iou
import torch
from ultralytics.utils.metrics import SegmentMetrics
from src.formats.COCOConversionResult import COCOConversionResult
from src.formats.DetectionData import DetectionData
from src.formats.EvaluateResult import EvaluateResult, ShapeSchema
from src.confusionmatrix import ConfusionMatrix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def coco_to_labelme_segmentation(coco_segmentation): #, image_width, image_height, normalize=False):
    # 提取 COCO 多边形坐标（假设只有一个多边形）
    if isinstance(coco_segmentation, list) and len(coco_segmentation) > 0:
        polygon = coco_segmentation[0]  # 取第一个多边形（COCO允许多个）
    else:
        raise ValueError("Invalid COCO segmentation format")

    # 将一维数组转换为二维点列表
    points = []
    for i in range(0, len(polygon), 2):
        x = polygon[i]
        y = polygon[i + 1]
        # if normalize:
        #     x /= image_width
        #     y /= image_height
        points.append([x, y])
    return points

def numpy_to_torch_tensors(*numpy_arrays, dtype=torch.float32, device=None):
    """
    将多个NumPy数组转换为PyTorch张量。

    参数:
    - numpy_arrays: 要转换的NumPy数组，可以是任意数量。
    - dtype: 转换后的张量数据类型，默认为torch.float32。
    - device: 目标设备（如'cuda'或'cpu'），默认为None（即使用当前PyTorch的默认设备）。

    返回:
    - 转换后的PyTorch张量列表。
    """
    tensors = []
    for arr in numpy_arrays:
        # 将NumPy数组转换为PyTorch张量
        tensor = torch.from_numpy(arr).type(dtype)
        # 如果指定了设备，则将张量移至该设备
        if device is not None:
            tensor = tensor.to(device)
        tensors.append(tensor)
    return tensors


class Evaluator:
    def __init__(self, labelme_file, cate_mapping: Dict[str,Dict[str,int]], type="labelme"):
        self.filename = labelme_file
        self.type = type
        if cate_mapping is None:
            cate_mapping = {"coco":{"secondary_particle": 1, "micro_powder": 2,"broken_ball": 3},
                                        "pred": {"secondary_particle": 255, "micro_powder": 200,"broken_ball": 100} }
        self.cate_mapping = cate_mapping # 统一的 cate id
        self.img = [] # 统一的 img id

        self.catename_2_id = cate_mapping["coco"]
        self.id_2_cate =  {value: key for key, value in cate_mapping["coco"].items()}
        # self.cate_id_cocos = { cate_mapping["pred"][key]: coco_id for key, coco_id in cate_mapping["coco"].items() }


        self.stats = dict(tp_m=[], tp=[], conf=[], pred_cls=[], target_cls=[])  # , target_img=[])

        # 为一些需要使用的属性预留位
        self.detections = None
        self.pred_masks = None
        self.gt_masks = None
        self.gt_cls = None
        self.pred_cls = None


    def labelme2coco(self,  labels_pathordict: Optional[Union[str, Dict]]=None, image_id: int=0, filename: Optional[str]=None):
        """
        将labelme格式标注的文件转换为coco 格式

        :param labels_pathordict:
        :param image_id:
        :return:
        """
        if labels_pathordict    is None:
            labels_pathordict = self.catename_2_id
        if filename is None:
            filename = self.filename
        data = single_file(filename, image_id=image_id,  labels_pathordict=labels_pathordict)
        return data

    def coco2true(self, file_or_data: Union[str, dict]) -> COCOConversionResult:
        """
        将COCO格式数据转换为结构化验证结果
        
        Args:
            file_or_data: COCO格式的JSON文件路径或已解析的字典数据
            
        Returns:
            COCOConversionResult: 已验证的转换结果
            
        Raises:
            ValidationError: 当数据不符合规范时
        """
        # 1. 加载COCO数据
        if isinstance(file_or_data, str):
            coco = COCO(file_or_data)
        else:
            with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
                temp_file.write(json.dumps(file_or_data).encode())
                temp_file.flush()
                coco = COCO(temp_file.name)

        # 2. 数据校验（可选）
        try:
            # 假设有COCO格式验证器
            coco_format.COCOImage(**coco.dataset)
        except ValidationError as e:
            logger.error(f"COCO数据校验失败: {e}")
            # raise

        # 3. 提取数据
        bboxes, cls, masks, segmentations = [], [], [], []
        for img_id in coco.getImgIds():
            for ann in coco.loadAnns(coco.getAnnIds(imgIds=img_id)):
                bboxes.append(ann['bbox'])
                cls.append(ann['category_id'])
                masks.append(coco.annToMask(ann))
                segmentations.append(coco_to_labelme_segmentation(ann["segmentation"]))

        # 4. 转换为NumPy数组
        try:
            bboxes_arr = np.stack(bboxes, axis=0) if bboxes else np.empty((0, 4))
            cls_arr = np.array(cls, dtype=np.int64) if cls else np.empty(0, dtype=np.int64)
            masks_arr = np.stack(masks, axis=0) if masks else np.empty((0, 1, 1), dtype=np.uint8)
        except ValueError as e:
            logger.error(f"数据堆叠失败: {e}")
            raise ValueError("数据格式不一致，无法堆叠") from e

        # 5. 返回已验证的结构化数据
        # return COCOConversionResult(
        #     bboxes=bboxes_arr,
        #     cls=cls_arr,
        #     masks=masks_arr,
        #     segmentations=segmentations
        # )
        data = {
            "cate": cls_arr,  # 字段名保持为cls
            "bboxes": bboxes_arr,
            "masks": masks_arr,
            "segmentations": segmentations
        }
        return COCOConversionResult.model_construct(**data)

        
    def coco2pred(self, file_or_data: Union[str, dict]) -> DetectionData:
        """
        将COCO格式转换为预测数据格式
        
        Args:
            file_or_data: COCO格式的JSON文件路径或字典数据
            
        Returns:
            DetectionData: 已验证的预测数据
            
        Raises:
            ValueError: 当数据转换失败时
            ValidationError: 当数据不符合规范时
        """
        # 1. 加载COCO数据
        try:
            if isinstance(file_or_data, str):
                coco = COCO(file_or_data)
            else:
                with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
                    temp_file.write(json.dumps(file_or_data).encode())
                    temp_file.flush()
                    coco = COCO(temp_file.name)
        except Exception as e:
            logger.error(f"COCO数据加载失败: {e}")
            raise ValueError("COCO数据加载失败") from e

        # 2. 数据校验（可选）
        try:
            coco_format.COCOImage(**coco.dataset)
        except ValidationError as e:
            logger.warning(f"COCO数据校验警告: {e}")

        # 3. 提取数据
        detections, pred_masks, segmentations = [], [], []
        for img_id in coco.getImgIds():
            for ann in coco.loadAnns(coco.getAnnIds(imgIds=img_id)):
                # 构建检测项 [x1,y1,x2,y2,conf,cls_id]
                bbox = ann['bbox']
                detection = [
                    bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3],  # xywh → xyxy
                    1.0,  # 默认置信度
                    ann['category_id']
                ]
                detections.append(detection)
                pred_masks.append(coco.annToMask(ann))
                segmentations.append(coco_to_labelme_segmentation(ann["segmentation"]))

        # 4. 转换为NumPy数组
        try:
            detections_arr = np.stack(detections, axis=0) if detections else np.empty((0, 6))
            masks_arr = np.stack(pred_masks, axis=0) if pred_masks else np.empty((0, 1, 1), dtype=np.uint8)
        except ValueError as e:
            logger.error(f"数据堆叠失败: {e}")
            raise ValueError("数据格式不一致，无法堆叠") from e

        # 5. 返回已验证数据
        return DetectionData.model_construct(**{'detections':detections_arr,'masks':masks_arr,'segmentations':segmentations, 'cate': detections_arr[:, 5].astype(np.int64).tolist()})
    
    def convert_format(self, path: str, cate_mapping: Dict, to_format: str = 'true') -> Union[COCOConversionResult, DetectionData]:
        """
        将输入数据转换为指定格式
        
        Args:
            file_or_data: 输入数据，可以是文件路径或字典
            to_format: 目标格式，支持 'true' 或 'pred'
            
        Returns:
            转换后的数据对象
            
        Raises:
            ValueError: 当目标格式不支持时
        """
        data = Evaluator(path, type='labelme', cate_mapping=cate_mapping)
        coco_data = data.labelme2coco()
        if to_format == 'true':
            return self.coco2true(coco_data)
        elif to_format == 'pred':
            return self.coco2pred(coco_data)
        else:
            raise ValueError(f"不支持的目标格式: {to_format}")


    def evaluate_core(self, gt:COCOConversionResult, pred:DetectionData, iou_threshold=0.45, conf=0.3):

        detections, pred_masks, gt_bboxes, gt_cls, gt_masks = numpy_to_torch_tensors(
            pred.detections, pred.masks, gt.bboxes, gt.cate, gt.masks, dtype=torch.float32,
            device='cpu'
        )

        iou = _process_batch(detections, gt_bboxes, gt_cls, pred_masks=pred_masks, gt_masks=gt_masks, masks=True)
        matches, ious = match_predictions_iou(detections[:, 5], gt_cls, iou, iou_threshold=iou_threshold)
        res, _, _ = match_predictions(detections[:, 5], gt_cls, iou)

  
        stats = dict(tp_m=[], tp=[], conf=[], pred_cls=[], target_cls=[])  # , target_img=[])
        metric = SegmentMetrics(names=self.id_2_cate)

        stats['tp_m'] = res.int()
        stats['tp'] = res.int()
        stats['conf'] = detections[:, 4]
        stats["pred_cls"] = detections[:, 5]
        stats["target_cls"] = gt_cls

        metric.process(**stats)

        nc =1
        logger.debug(f"IOU阈值: {iou_threshold}, 置信度: {conf}")
        cm = ConfusionMatrix(nc, conf, iou_threshold, task="segment")
        cm.process_batch_masks(detections, gt_masks.reshape(gt_masks.shape[0],-1), pred_masks.reshape(pred_masks.shape[0],-1), gt_cls)
        p = cm.matrix / ((cm.matrix.sum(1).reshape(-1, 1) + 1e-9))  # normalize columns
        r = cm.matrix / ((cm.matrix.sum(0).reshape(1, -1) + 1e-9))  # normalize columns

        # 有一种特殊情况，预测和标注没有匹配，但是给出的 cm 也是空，就和后面使用cm计算真实和预测的实例数冲突。
        if len(matches) == 0:
            cm.matrix = np.array([[0,len(pred_masks)],[len(gt_masks), 0]])


        result =  {
            "matches": matches.tolist(),
            "ious": ious.tolist(),
            "whole_iou": iou.numpy().tolist(),
            "cm": cm.matrix.tolist(),
            "p": p.tolist(),
            "r": r.tolist(),
            "mean_results": metric.seg.mean_results(),
            "ap": metric.seg.ap.tolist(),
            # 'elapsed_time': elapsed_time, # 调用后补充上
            # 'filename': filename  # 调用后补充上
            }
        return  result
    def evaluate_pair(self, labelme_path, predmask_path, iou_threshold=0.45, conf=0.3):
        """
        :params:
            1、支持labelme json格式的预测
        Returns:
            包含评估结果的字典（结构见 EvaluateResult）
        """

        # 1. 数据转换
        gt = self.convert_format(labelme_path, self.cate_mapping, to_format='true')
        pred = self.convert_format(predmask_path, self.cate_mapping, to_format='pred')
        logger.info(f"数据转换完成 | GT实例数: {len(gt.bboxes)}, Pred实例数: {len(pred.masks)}")

        # pred_cls = np.array(pred.detections[:, 5], dtype=np.int64).tolist()
        # gt_cls = np.array(gt.cate).tolist()

        # 2. 初始化默认结果
        result = {
                "matches": [],
                "ious": [],
                "whole_iou": [],
                "gt_shapes": {"shapes": []},
                "pred_shapes": {"shapes": []},
                "cm": [],
                "p": [],
                "r": [],
                "mean_results": {},
                "ap": []
            }
        

        # 3. 分场景处理
        gt_nums = len(gt.bboxes)
        pred_nums = len(pred.masks)

        if not gt_nums and not pred_nums:
            logger.warning("真实标注和预测数据中都没有实例，无法进行评估")
            return result

        # 填充存在的形状数据
        if gt_nums:
            result["gt_shapes"]["shapes"] = self._build_shapes(
                gt.segmentations, 
                gt.cate, 
                gt.masks, 
                self.id_2_cate
            )
            result['cm'] = [[0, 0],[gt_nums, 0]]
        if pred_nums:
            result["pred_shapes"]["shapes"] = self._build_shapes(
                pred.segmentations,
                pred.cate,
                pred.masks,
                self.id_2_cate
            )
            result['cm'] = [[0, pred_nums],[0, 0]]

        # 4. 仅当双方都有数据时执行评估
        if gt_nums and pred_nums:
            try:
                eval_result = self.evaluate_core(gt, pred, iou_threshold, conf)
                final_result = {**result, **eval_result}  # 合并结果, 在 gt_shapes 和 pred_shapes 之外补充其他数据
                logger.info("评估核心计算完成")
                return final_result
            except Exception as e:
                logger.error(f"评估失败: {str(e)}", exc_info=True)
                return result

        logger.warning(f"评估跳过 | {'GT为空' if not gt_nums else 'Pred为空'}")
        return result

    def _build_shapes(
        self,
        segmentations: list[list[list[float]]],
        cate_ids: list[int],
        masks: list[np.ndarray],
        id_to_cate: Dict[int, str]
    ) -> list[Dict[str, Any]]:
        """统一构建形状数据（减少重复代码）"""
        return [
            ShapeSchema(
                cls_id=cate_id,
                label=id_to_cate[cate_id],
                points=points,
                shape_type="polygon",
                id=i,
                area=int(np.where(mask > 0, 1, 0).sum())
            ).model_dump()
            for i, (points, cate_id, mask) in enumerate(zip(segmentations, cate_ids, masks))
        ]

if __name__ == '__main__':
    # 先测试labelme2coco 的转换
    labelme_path = "/home/zwuser/app/vision/vision_eval/backend/eval_server/uploads/test/001_labelme.json"
    predmask_path = "/home/zwuser/app/vision/vision_eval/backend/eval_server/uploads/test/001_mask.json"
    # labelme_path, predmask_path = predmask_path, labelme_path
    # cate_mapping = {"coco":{"secondary_particle": 1, "micro_powder": 2,"broken_ball": 3},
    #                 "pred": {"secondary_particle": 255, "micro_powder": 200,"broken_ball": 100} }

    # cate_mapping = {"coco":{"secondary_particle": 1}}
    cate_mapping = {"coco":{"broken_ball": 0}}
    data = Evaluator(labelme_path, cate_mapping=cate_mapping)
    result = data.evaluate_pair(labelme_path, predmask_path)
    print(result)