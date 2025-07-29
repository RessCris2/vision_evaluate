"""
    使用 ultralytics 的接口进行指标计算时需要使用的数据类型

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
"""

from pydantic import BaseModel, validator, Any
import torch

class DetectionPredData(BaseModel):
    detections: Any  # torch.Tensor of shape (N, 6)
    # gt_bboxes: Any  # torch.Tensor of shape (M, 4)
    # gt_cls: Any  # torch.Tensor of shape (M,)
    pred_masks: Any  # torch.Tensor | None of shape (N, H, W)
    # gt_masks: Any  # torch.Tensor | None of shape (M, H, W)
    # overlap: bool
    # masks: bool

    class DetectionTrueData(BaseModel):
        # detections: Any  # torch.Tensor of shape (N, 6)
        gt_bboxes: Any  # torch.Tensor of shape (M, 4)
        gt_cls: Any  # torch.Tensor of shape (M,)
        # pred_masks: Any  # torch.Tensor | None of shape (N, H, W)
        gt_masks: Any  # torch.Tensor | None of shape (M, H, W)
        # overlap: bool
        # masks: bool

    class DetectionData(BaseModel):
        detections: Any  # torch.Tensor of shape (N, 6)
        gt_bboxes: Any  # torch.Tensor of shape (M, 4)
        gt_cls: Any  # torch.Tensor of shape (M,)
        pred_masks: Any  # torch.Tensor | None of shape (N, H, W)
        gt_masks: Any  # torch.Tensor | None of shape (M, H, W)
        overlap: bool
        masks: bool

    # # 验证器示例：检查detections是否为torch.Tensor且形状正确（可选）
    # @validator('detections')
    # def check_detections_tensor(cls, v):
    #     if not isinstance(v, torch.Tensor) or v.shape[1] != 6:
    #         raise ValueError("detections must be a torch.Tensor of shape (N, 6)")
    #     return v
    #
    # @validator('gt_bboxes')
    # def check_gt_bboxes_tensor(cls, v):
    #     if not isinstance(v, torch.Tensor) or v.shape[1] != 4:
    #         raise ValueError("gt_bboxes must be a torch.Tensor of shape (N, 6)")
    #     return v
    #
    # @validator('gt_bboxes')
    # def check_gt_bboxes_tensor(cls, v):
    #     if not isinstance(v, torch.Tensor) or v.shape[1] != 4:
    #         raise ValueError("gt_bboxes must be a torch.Tensor of shape (N, 6)")
    #     return v
    #
    #     # 类似地，你可以为其他张量添加验证器

# 使用示例
# 注意：在实际应用中，你需要确保在实例化DetectionData之前已经导入了torch并创建了相应的张量
# 这里只是演示如何定义模型


