"""
"""
import torch
import numpy as np
from ultralytics.utils.metrics import SegmentMetrics, box_iou, mask_iou
from ultralytics.models.yolo.segment import SegmentationValidator
import torch.nn.functional as F


class Val(SegmentationValidator):
    def __init__(self):
        self.iouv = torch.linspace(0.5, 0.95, 10)  # IoU vector for mAP@0.5:0.95
        self.niou = self.iouv.numel()
        self.stats = dict(tp=[], conf=[], pred_cls=[], target_cls=[], target_img=[])
        self.seen = 0
        self.metrics = SegmentMetrics(on_plot=None) # save_dir 可调整

    def update_metrics(self, preds, batch):
        """Metrics."""
        for si, pred in enumerate(preds):
            self.seen += 1
            npr = len(pred)
            stat = dict(
                conf=torch.zeros(0, device=self.device),
                pred_cls=torch.zeros(0, device=self.device),
                tp=torch.zeros(npr, self.niou, dtype=torch.bool, device=self.device),
            )
            pbatch = self._prepare_batch(si, batch)
            cls, bbox = pbatch.pop("cls"), pbatch.pop("bbox")
            nl = len(cls)
            stat["target_cls"] = cls
            stat["target_img"] = cls.unique()
            if npr == 0:
                if nl:
                    for k in self.stats.keys():
                        self.stats[k].append(stat[k])
                    if self.args.plots:
                        self.confusion_matrix.process_batch(detections=None, gt_bboxes=bbox, gt_cls=cls)
                continue

            # Predictions
            if self.args.single_cls:
                pred[:, 5] = 0
            predn = self._prepare_pred(pred, pbatch)
            stat["conf"] = predn[:, 4]
            stat["pred_cls"] = predn[:, 5]

            # Evaluate
            if nl:
                stat["tp"] = self._process_batch(predn, bbox, cls)
                # if self.args.plots:
                #     self.confusion_matrix.process_batch(predn, bbox, cls)
            for k in self.stats.keys():
                self.stats[k].append(stat[k])


    def get_stats(self):
        """Returns metrics statistics and results dictionary."""
        stats = {k: torch.cat(v, 0).cpu().numpy() for k, v in self.stats.items()}  # to numpy
        self.nt_per_class = np.bincount(stats["target_cls"].astype(int), minlength=self.nc)
        self.nt_per_image = np.bincount(stats["target_img"].astype(int), minlength=self.nc)
        stats.pop("target_img", None)
        if len(stats) and stats["tp"].any():
            self.metrics.process(**stats)
        return self.metrics.results_dict

"""
Processes the detection and segmentation metrics over the given set of predictions.

    Args:
        tp (list): List of True Positive boxes.
        tp_m (list): List of True Positive masks.
        conf (list): List of confidence scores.
        pred_cls (list): List of predicted classes.
        target_cls (list): List of target classes.
"""
    # 这是一幅图维度的结果
def _process_batch(detections, gt_bboxes, gt_cls, pred_masks=None, gt_masks=None, overlap=False, masks=False):
        """
        Compute correct prediction matrix for a batch based on bounding boxes and optional masks.

        Args:
            detections (torch.Tensor): Tensor of shape (N, 6) representing detected bounding boxes and
                associated confidence scores and class indices. Each row is of the format [x1, y1, x2, y2, conf, class].
            gt_bboxes (torch.Tensor): Tensor of shape (M, 4) representing ground truth bounding box coordinates.
                Each row is of the format [x1, y1, x2, y2].
            gt_cls (torch.Tensor): Tensor of shape (M,) representing ground truth class indices.
            pred_masks (torch.Tensor | None): Tensor representing predicted masks, if available. The shape should
                match the ground truth masks. (N, H, W)
            gt_masks (torch.Tensor | None): Tensor of shape (M, H, W) representing ground truth masks, if available.
            overlap (bool): Flag indicating if overlapping masks should be considered.
            masks (bool): Flag indicating if the batch contains mask data.

        Returns:
            (torch.Tensor): A correct prediction matrix of shape (N, 10), where 10 represents different IoU levels.

        Note:
            - If `masks` is True, the function computes IoU between predicted and ground truth masks.
            - If `overlap` is True and `masks` is True, overlapping masks are taken into account when computing IoU.

        Example:
            ```python
            detections = torch.tensor([[25, 30, 200, 300, 0.8, 1], [50, 60, 180, 290, 0.75, 0]])
            gt_bboxes = torch.tensor([[24, 29, 199, 299], [55, 65, 185, 295]])
            gt_cls = torch.tensor([1, 0])
            correct_preds = validator._process_batch(detections, gt_bboxes, gt_cls)
            ```
        """
        if masks:
            if overlap:
                nl = len(gt_cls)
                index = torch.arange(nl, device=gt_masks.device).view(nl, 1, 1) + 1
                gt_masks = gt_masks.repeat(nl, 1, 1)  # shape(1,640,640) -> (n,640,640)
                gt_masks = torch.where(gt_masks == index, 1.0, 0.0)
            if gt_masks.shape[1:] != pred_masks.shape[1:]:
                gt_masks = F.interpolate(gt_masks[None], pred_masks.shape[1:], mode="bilinear", align_corners=False)[0]
                gt_masks = gt_masks.gt_(0.5)
            iou = mask_iou(gt_masks.reshape(gt_masks.shape[0], -1), pred_masks.reshape(pred_masks.shape[0], -1))
        else:  #
            iou = box_iou(gt_bboxes, detections[:, :4])

        # return self.match_predictions(detections[:, 5], gt_cls, iou)
        return iou


def match_predictions(pred_classes, true_classes, iou, use_scipy=False):
    """
    Matches predictions to ground truth objects (pred_classes, true_classes) using IoU.

    Args:
        pred_classes (torch.Tensor): Predicted class indices of shape(N,).
        true_classes (torch.Tensor): Target class indices of shape(M,).
        iou (torch.Tensor): An NxM tensor containing the pairwise IoU values for predictions and ground of truth
        use_scipy (bool): Whether to use scipy for matching (more precise).

    Returns:
        (torch.Tensor): Correct tensor of shape(N,10) for 10 IoU thresholds.
        result: ndarray
    """
    iouv = torch.linspace(0.5, 0.95, 10)
    # Dx10 matrix, where D - detections, 10 - IoU thresholds
    correct = np.zeros((pred_classes.shape[0], iouv.shape[0])).astype(bool)
    # LxD matrix where L - labels (rows), D - detections (columns)
    correct_class = true_classes[:, None] == pred_classes
    iou = iou * correct_class  # zero out the wrong classes
    iou = iou.cpu().numpy()

    for i, threshold in enumerate(iouv.cpu().tolist()):
        if use_scipy:
            # WARNING: known issue that reduces mAP in https://github.com/ultralytics/ultralytics/pull/4708
            import scipy  # scope import to avoid importing for all commands

            cost_matrix = iou * (iou >= threshold)
            if cost_matrix.any():
                labels_idx, detections_idx = scipy.optimize.linear_sum_assignment(cost_matrix, maximize=True)
                valid = cost_matrix[labels_idx, detections_idx] > 0
                if valid.any():
                    correct[detections_idx[valid], i] = True
        else:
            matches = np.nonzero(iou >= threshold)  # IoU > threshold and classes match
            matches = np.array(matches).T
            if matches.shape[0]:
                if matches.shape[0] > 1:
                    # iou 大于阈值的pair 按照 iou 从大到小排序
                    matches = matches[iou[matches[:, 0], matches[:, 1]].argsort()[::-1]]
                    # 选出真实 id 第一次出现的位置（index)，作为真实id对应的预测
                    matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
                    # matches = matches[matches[:, 2].argsort()[::-1]]
                    # 选出真实 id 第一次出现的位置（index)，作为真实id对应的预测；再选出预测值中第一次出现的位置。作为最终的 pair
                    matches = matches[np.unique(matches[:, 0], return_index=True)[1]]
                correct[matches[:, 1].astype(int), i] = True
        if i==0:
            match_result = matches
            iou_result = iou[matches[:, 0], matches[:, 1]]
    #     match_result.append(matches)
    # result =np.vstack(match_result)
    return torch.tensor(correct, dtype=torch.bool, device=pred_classes.device), match_result, iou_result



def match_predictions_iou(pred_classes, true_classes, iou, iou_threshold=0.5):
    """
    Matches predictions to ground truth objects (pred_classes, true_classes) using  a  Given IoU.

    Args:
        pred_classes (torch.Tensor): Predicted class indices of shape(N,).
        true_classes (torch.Tensor): Target class indices of shape(M,).
        iou (torch.Tensor): An NxM tensor containing the pairwise IoU values for predictions and ground of truth
        iou_threshold: Given IoU threshold
        # use_scipy (bool): Whether to use scipy for matching (more precise).

    Returns:
        (torch.Tensor): Correct tensor of shape(N,10) for 10 IoU thresholds.
        result: ndarray
    """
    # iouv = torch.linspace(0.5, 0.95, 10)
    # Dx10 matrix, where D - detections, 10 - IoU thresholds
    # correct = np.zeros((pred_classes.shape[0], iouv.shape[0])).astype(bool)
    # LxD matrix where L - labels (rows), D - detections (columns)
    correct_class = true_classes[:, None] == pred_classes
    iou = iou * correct_class  # zero out the wrong classes
    iou = iou.cpu().numpy()
    threshold = iou_threshold

    # for i, threshold in enumerate(iouv.cpu().tolist()):
        # if use_scipy:
        #     # WARNING: known issue that reduces mAP in https://github.com/ultralytics/ultralytics/pull/4708
        #     import scipy  # scope import to avoid importing for all commands

        #     cost_matrix = iou * (iou >= threshold)
        #     if cost_matrix.any():
        #         labels_idx, detections_idx = scipy.optimize.linear_sum_assignment(cost_matrix, maximize=True)
        #         valid = cost_matrix[labels_idx, detections_idx] > 0
        #         if valid.any():
        #             correct[detections_idx[valid], i] = True
        # else:
    matches = np.nonzero(iou >= threshold)  # IoU > threshold and classes match
    matches = np.array(matches).T
    if matches.shape[0]:
        if matches.shape[0] > 1:
            # iou 大于阈值的pair 按照 iou 从大到小排序
            matches = matches[iou[matches[:, 0], matches[:, 1]].argsort()[::-1]]
            # 选出真实 id 第一次出现的位置（index)，作为真实id对应的预测
            matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
            # matches = matches[matches[:, 2].argsort()[::-1]]
            # 选出真实 id 第一次出现的位置（index)，作为真实id对应的预测；再选出预测值中第一次出现的位置。作为最终的 pair
            matches = matches[np.unique(matches[:, 0], return_index=True)[1]]
        # correct[matches[:, 1].astype(int), i] = True
    # if i==0:
    match_result = matches
    iou_result = iou[matches[:, 0], matches[:, 1]]
    #     match_result.append(matches)
    # result =np.vstack(match_result)
    return  match_result, iou_result


if __name__ == '__main__':
    """确定二者的格式
    """
    detections = torch.load("predn.pt", map_location=torch.device('cpu'))
    gt_bboxes = torch.load("bbox.pt", map_location=torch.device('cpu'))
    gt_cls = torch.load("cls.pt", map_location=torch.device('cpu'))
    pred_masks = torch.load("pred_masks.pt", map_location=torch.device('cpu'))
    gt_masks = torch.load("gt_masks.pt", map_location=torch.device('cpu'))
    
    iou = _process_batch(detections, gt_bboxes, gt_cls, pred_masks=pred_masks, gt_masks=gt_masks, masks=True)
    # val.get_stats()
    res = match_predictions(detections[:, 5], gt_cls, iou)
    stats = dict(tp_m=[], tp=[], conf=[], pred_cls=[], target_cls=[]) #, target_img=[])
    names = torch.load("names.pt", map_location=torch.device('cpu'))
    metric = SegmentMetrics(names=names)
    stats['tp_m'] = res
    stats['tp'] = res
    stats['conf'] =  detections[:, 4]
    stats["pred_cls"] = detections[:, 5]
    stats["target_cls"] = gt_cls
    # stats["target_img"] = gt_cls.unique()

    metric.process(**stats)
    print("xxx")
