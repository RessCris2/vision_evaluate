"""COCO 格式转换真实标注结果的 Pydantic 模型 (Pydantic V2)
"""
from pydantic import BaseModel, Field, field_validator
from typing import List
import numpy as np

class COCOConversionResult(BaseModel):
    """COCO格式转换结果模型 (Pydantic V2)"""
    bboxes: List[List[float]] = Field(
        default_factory=list,
        exclude=True,  # 禁止自动包含在repr中
        description="边界框列表，每个元素为[x,y,width,height]",
        json_schema_extra={
            "example": [[10.5, 20.3, 30.0, 40.0], [15.0, 25.0, 50.0, 60.0]]
        }
    )
    cate: List[int] = Field(
        default_factory=list,
        description="类别ID列表",
        exclude=True,  # 禁止自动包含在repr中
        json_schema_extra={"example": [1, 3]}
    )
    masks: List[List[List[int]]] = Field(
        default_factory=list,
        description="掩码矩阵列表，每个元素为二维0/1矩阵",
        exclude=True,  # 禁止自动包含在repr中
        json_schema_extra={
            "example": [[[0, 1], [1, 0]], [[1, 1], [1, 1]]]
        }
    )
    segmentations: List[List[List[float]]] = Field(
        default_factory=list,
        description="多边形分割坐标列表",
        exclude=True,  # 禁止自动包含在repr中
        json_schema_extra={
            "example": [[[10.5, 20.3], [30.0, 40.0]], [[15.0, 25.0], [50.0, 60.0]]]
        }
    )

    # @field_validator('bboxes')
    # @classmethod
    # def validate_bboxes(cls, v: List[List[float]]) -> List[List[float]]:
    #     """验证边界框格式"""
    #     for bbox in v:
    #         if len(bbox) != 4:
    #             raise ValueError("每个bbox必须是4个数值 [x,y,width,height]")
    #         if bbox[2] <= 0 or bbox[3] <= 0:
    #             raise ValueError("bbox的宽高必须为正数")
    #     return v

    # @field_validator('masks')
    # @classmethod
    # def validate_masks(cls, v: List[List[List[int]]]) -> List[List[List[int]]]:
    #     """验证掩码格式"""
    #     for mask in v:
    #         if not all(i in (0, 1) for row in mask for i in row):
    #             raise ValueError("mask必须为0/1矩阵")
    #     return v

    model_config = {
        "json_schema_extra": {
            "description": "COCO格式数据转换结果",
            "examples": [{
                "bboxes": [[10.5, 20.3, 30.0, 40.0]],
                "cls": [1],
                "masks": [[[0, 1], [1, 0]]],
                "segmentations": [[[10.5, 20.3], [30.0, 40.0]]]
            }]
        }
    }