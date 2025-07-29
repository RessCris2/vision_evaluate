import os
import json
from typing import List, Union,Set
import numpy as np
import time 
import torch
from concurrent.futures import ProcessPoolExecutor,as_completed
from fastapi import APIRouter
from fastapi import Query
import pandas as pd
from src.eval_main import Evaluator
from eval_server.routers.logger import create_logger
from eval_server.eval_config import UPLOAD_FOLDER, logger_dir, redis_client

logger = create_logger(logger_dir,"evaluate")

router = APIRouter(
    prefix="/evaluate",
    tags=["evaluate"],
)

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

def get_labelme_labels(labelme_path: str) -> Set[str]:
    """
    获取 LabelMe 文件中的所有唯一标签名
    
    Args:
        labelme_path: LabelMe JSON 文件路径
        
    Returns:
        所有唯一标签名的集合（自动去重）
        
    Raises:
        FileNotFoundError: 文件不存在时抛出
        json.JSONDecodeError: JSON 格式错误时抛出
    """
    with open(labelme_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 从 shapes 中提取所有 label 字段
    return {shape['label'].lower() for shape in data.get('shapes', [])}

def filter_labels_by_name(labelme_file, label_name):
    """
    过滤 LabelMe 标注文件，只保留指定标签名的标注
    
    :param labelme_file: labelme 标注文件路径（.json）
    :param label_name: 要保留的标签名称（只支持单个字符串）
    :return: 过滤后的 LabelMe 格式字典
    """
    import json

    with open(labelme_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 过滤 shapes
    filtered_shapes = [
        shape for shape in data.get('shapes', [])
        if shape['label'].lower() == label_name.lower()
    ]
    
    # 构建新数据（保留原文件其他字段）
    new_data = {**data, 'shapes': filtered_shapes}
    valid_nums = len(new_data['shapes'])
    if valid_nums == 0:
        logger.warning(f"过滤后没有找到标签 {label_name} 的标注, 文件: {labelme_file}")
        raise ValueError(f"没有找到标签 {label_name} 的标注, 文件: {labelme_file}")

    save_path = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(os.path.basename(labelme_file))[0]}_filtered.json")
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

    return save_path

def evaluate(conf:float=0.3, iou_thres:float=0.45, phrase_target:str="primary_particle", 
             filename:str="mask.json", file_key: str="", label_name: Union[str, None] = None):
    """
    file_key: 由前端传入, 用于存储结果
    label_name: 由前端传入, 如果指定了label_name, 则需要过滤label_name的类别去做评估
    """
    start_time = time.time()

    logger.info(f"开始评估: 目标-{phrase_target}, 文件 {filename}")
    # 接收一个列表
    # 多进程来处理

    if phrase_target == "一次颗粒":
        cate_mapping = {"coco": {"Primary_Particle":0},
            "pred": {"Primary_Particle": 255}}
    elif phrase_target == "二次颗粒":
        cate_mapping = {"coco": {"secondary_particle":0},
                "pred": {"secondary_particle": 255}}
    elif phrase_target == "微粉":
        if label_name is not None and label_name != "":
            cate_mapping = {"coco": {f"{label_name}":0},
            "pred": {f"{label_name}": 255}}
        else:
            cate_mapping = {"coco": {"Secondary_Particle":0},
            "pred": {"Secondary_Particle": 255}}
    else:
        raise ValueError("阶段错误")
    
    logger.debug(f"cate_mapping: {cate_mapping}")
    
    filename_base = os.path.splitext(filename)[0]
    logger.info(f"filename: {filename}")
    predmask_path = os.path.join(UPLOAD_FOLDER, f"{filename_base}_mask.json")
    labelme_path = os.path.join(UPLOAD_FOLDER, f"{filename_base}_labelme.json")

    # 获取 labelme_path 和 predmask_path 中shapes的label_name名, 生成 cate_mapping
    real_labels = get_labelme_labels(labelme_path)
    pred_labels = get_labelme_labels(predmask_path)
    logger.debug(f"LabelMe labels: {real_labels}")
    logger.debug(f"Predicted labels: {pred_labels}")

   
    item_result = {}
    for label_name in real_labels:
        try:
            label_name = label_name.lower()
            cate_mapping = {"coco": {f"{label_name}":0},
                "pred": {f"{label_name}": 255}}
            
            evaluator = Evaluator(labelme_path, cate_mapping=cate_mapping)
            eval_result = evaluator.evaluate_pair(labelme_path, predmask_path)
            
            elapsed_time = time.time() - start_time
            logger.info(f"{label_name}-{filename}评估函数耗时: {elapsed_time:.3f} s")

            result =  {**eval_result,
                    'elapsed_time': elapsed_time,
                    'filename': filename
                    }
            
            result_key = file_key + filename + label_name.lower()
            redis_client.set(result_key, json.dumps(result))

            item_result[label_name.lower()] = result
        except Exception as e:
            logger.error(f"评估 {label_name} 时出错: {e}")
    return item_result


@router.get(f"/download-excel")  # noqa: F541
def write_excel(phrase_target: str, file_key: str,filelist: List[str] = Query(...), label_name: Union[str, None] = None):
    logger.debug(f"开始写入: 目标-{phrase_target}")
    if phrase_target == "一次颗粒":
        cate_mapping = {"coco": {"Primary_Particle":0},
            "pred": {"Primary_Particle": 255}}
    elif phrase_target == "二次颗粒":
        cate_mapping = {"coco": {"secondary_particle":0},
                "pred": {"secondary_particle": 255}}
    elif phrase_target == "开裂球":
        cate_mapping = {"coco": {"secondary_particle":0, "cracking_ball":1},
                "pred": {"secondary_particle":0, "cracking_ball": 255}}
    elif phrase_target == "微粉":
        cate_mapping ={"coco":{"Secondary_Particle": 0, "Micro_powder": 1,"Broken_Ball": 2},
            "pred": {"Secondary_Particle": 255, "Micro_powder": 200,"Broken_Ball": 100} }
    else:
        raise ValueError("阶段错误")
    cates = list(cate_mapping['coco'].keys())
    rows = []
    ind = 0
    for _, file in enumerate(filelist):
        for label_name in cates:
            label_name = label_name.lower()
            if not file.endswith(".json"):
                # filename = file.split(".")[0]
                result_key = file_key + file + label_name
                res = redis_client.get(result_key) 
                if res is None:
                    continue
                res = json.loads(res)

                row = []
                ind += 1
                row.append(ind)
                row.append(file)

                # n = len(res['cm'] )-1 
                n=1  # 目前只考虑一个类别

                # 需要特殊处理 p, r, cm 都为空的情况
                if len(res['p']) == 0:
                    res['p'] = np.zeros((2, 2))
                    res['r'] = np.zeros((2, 2))
                    # res['cm'] = np.zeros((2, 2))

                cm_array = np.array(res['cm'])
                for i in range(n):
                    row.append(label_name)
                    row.append(np.round(np.sum(cm_array[:, i]), 3))
                    row.append(np.round(np.sum(cm_array[i]), 3))
                    row.append(np.round(cm_array[i, i], 3))
                    row.append(np.round(res['p'][i][i], 3))
                    row.append(np.round(res['r'][i][i], 3))
                    row.append(np.round(res['elapsed_time'], 3))
                rows.append(row)


    df = pd.DataFrame(rows, columns=["index","picname", "cate", 'whole_true', 'whole_pred', 'true_pred' , 'precision', 'recall', 'elapsed_time'])
    result = df.to_dict(orient='records')
    return result


@router.get(f"/batch")  # noqa: F541
async def evaluate_batch(conf:float=0.3, iou_thres:float=0.5, phrase_target:str="primary_particle",  label_name: Union[str, None] = None,
                         file_key: str="",
                         filelist: List[str] = Query(...)):
    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(evaluate, conf, iou_thres, phrase_target, filename, file_key, label_name): filename for filename in filelist}
        
        results = {}
        for future in as_completed(futures):
            filename = futures[future]
            try:
                result = future.result()
                results[filename] = result

            except json.JSONDecodeError as e:
                logger.error(f"JSON decoding error for file {filename}: {e}")
                # raise HTTPException(status_code=500, detail=f"Task raised an exception for file {filename}: {e}")
            except Exception as e:
                logger.error(f"Task raised an exception for file {filename}: {e}")
                results[filename+'error'] = {"error": str(e)}
                # 返回HTTP状态码500
                # raise HTTPException(status_code=500, detail=f"Task raised an exception for file {filename}: {e}")
    return results