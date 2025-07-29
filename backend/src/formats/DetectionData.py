from pydantic import BaseModel, Field, field_validator, ValidationError
import numpy as np
import torch
from typing import Optional, List, Union
import tempfile
import logging
from pycocotools.coco import COCO

logger = logging.getLogger(__name__)

class DetectionData(BaseModel):
    """预测数据验证模型 (Pydantic V2)"""
    detections: List[List[float]] = Field(
        ...,
        description="检测框列表，每个元素为[x1,y1,x2,y2,conf,cls_id]",
        exclude=True,  # 禁止自动包含在repr中
        min_items=6,
        max_items=6
    )
    masks: List[List[List[int]]] = Field(
        default_factory=list,
        exclude=True,  # 禁止自动包含在repr中
        description="预测掩码列表，每个元素为二维0/1矩阵"
    )
    segmentations: List[List[List[float]]] = Field(
        default_factory=list,
        exclude=True,  # 禁止自动包含在repr中
        description="多边形分割坐标列表"
    )
    
    cate: Optional[List[int]] = Field(
        default=None,
        description="类别ID列表",
        exclude=True  # 禁止自动包含在repr中
    )

    @field_validator('detections', mode='before')
    @classmethod
    def validate_detections(cls, v: Union[List[List[float]], np.ndarray]) -> List[List[float]]:
        """验证检测框格式"""
        if isinstance(v, np.ndarray):
            v = v.tolist()
        for det in v:
            if len(det) != 6:
                raise ValueError("每个检测项必须包含6个值 [x1,y1,x2,y2,conf,cls_id]")
            if det[4] < 0 or det[4] > 1:  # 置信度检查
                raise ValueError("置信度必须在0-1范围内")
        return v

    @field_validator('masks', mode='before')
    @classmethod
    def validate_masks(cls, v: Union[List[List[List[int]]], np.ndarray]) -> List[List[List[int]]]:
        """验证掩码格式"""
        if isinstance(v, np.ndarray):
            v = v.tolist()
        for mask in v:
            if not all(i in (0, 1) for row in mask for i in row):
                raise ValueError("mask必须为0/1矩阵")
        return v

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "detections": [[10, 20, 30, 40, 0.9, 1]],
                "pred_masks": [[[0, 1], [1, 0]]],
                "segmentations": [[[10, 20], [30, 40]]]
            }
        }
    }