from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Literal
from pydantic.functional_validators import field_validator
import numpy as np

class ShapeSchema(BaseModel):
    """标注/预测的多边形形状定义"""
    cls_id: int = Field(..., ge=0, description="类别ID")
    label: str = Field(..., min_length=1, description="类别名称")
    points: List[List[float]] = Field(
        ...,
        min_length=3,
        description="多边形顶点坐标 [[x1,y1], [x2,y2], ...]",
        json_schema_extra={"example": [[10.5, 20.3], [30.0, 40.0]]}
    )
    shape_type: Literal["polygon"] = Field(
        default="polygon",
        description="形状类型（固定为polygon）"
    )
    id: int = Field(..., ge=0, description="唯一标识符")
    area: int = Field(..., gt=0, description="像素面积")

    @field_validator('points')
    @classmethod
    def validate_points(cls, v: List[List[float]]) -> List[List[float]]:
        """验证每个点必须包含xy两个坐标"""
        for point in v:
            if len(point) != 2:
                raise ValueError("每个点必须包含[x,y]两个坐标")
        return v

class ShapesCollection(BaseModel):
    """形状集合容器"""
    shapes: List[ShapeSchema] = Field(
        default_factory=list,
        description="形状对象列表",
        min_length=0
    )

class EvaluateResult(BaseModel):
    """评估结果的核心数据结构"""
    matches: List[List[int]] = Field(
        default_factory=list,
        description="匹配矩阵 [[gt_idx, pred_idx], ...]",
        min_length=0,
        json_schema_extra={"example": [[0, 1], [2, 3]]}
    )
    ious: List[float] = Field(
        default_factory=list,
        description="每个匹配对的IoU值",
        ge=0.0,
        le=1.0,
        json_schema_extra={"example": [0.8, 0.6]}
    )
    whole_iou: List[List[float]] = Field(
        default_factory=list,
        description="全量IoU矩阵",
        json_schema_extra={"example": [[0.1, 0.8], [0.3, 0.2]]}
    )
    gt_shapes: ShapesCollection = Field(
        ...,
        description="真实标注的形状数据"
    )
    pred_shapes: ShapesCollection = Field(
        ...,
        description="预测结果的形状数据"
    )
    cm: List[List[int]] = Field(
        ...,
        description="混淆矩阵",
        min_length=1,
        json_schema_extra={"example": [[50, 2], [3, 45]]}
    )
    p: List[List[float]] = Field(
        ...,
        description="精度矩阵",
        min_length=1,
        json_schema_extra={"example": [[0.96, 0.04], [0.06, 0.94]]}
    )
    r: List[List[float]] = Field(
        ...,
        description="召回率矩阵",
        min_length=1,
        json_schema_extra={"example": [[0.93, 0.07], [0.04, 0.96]]}
    )
    mean_results: List[float] = Field(
        ...,
        description="平均指标 [mAP, mRecall, ...]",
        min_length=1,
        json_schema_extra={"example": [0.85, 0.75, 0.90]}
    )
    ap: List[float] = Field(
        ...,
        description="各类别AP值",
        min_length=1,
        json_schema_extra={"example": [0.82, 0.78]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "description": "目标检测/分割评估结果",
            "examples": [{
                "matches": [[0,1]],
                "ious": [0.8],
                "whole_iou": [[0.8]],
                "gt_shapes": {"shapes": [{
                    "cls_id": 1,
                    "label": "cat",
                    "points": [[10,20], [30,40]],
                    "shape_type": "polygon",
                    "id": 0,
                    "area": 200
                }]},
                "pred_shapes": {"shapes": [{
                    "cls_id": 1,
                    "label": "cat",
                    "points": [[12,22], [32,42]],
                    "shape_type": "polygon",
                    "id": 1,
                    "area": 210
                }]},
                "cm": [[1,0], [0,1]],
                "p": [[1.0,0.0], [0.0,1.0]],
                "r": [[1.0,0.0], [0.0,1.0]],
                "mean_results": [1.0, 1.0],
                "ap": [1.0, 1.0]
            }]
        }
    )

    @field_validator('cm', 'p', 'r')
    @classmethod
    def validate_matrix_shape(cls, v: List[List]) -> List[List]:
        """确保矩阵为方阵"""
        if len(v) != len(v[0]):
            raise ValueError("矩阵必须是方阵")
        return v

# 使用示例
if __name__ == "__main__":
    # 从原始数据构造（自动校验）
    result = EvaluateResult.model_validate({
        "matches": [[0,1]],
        "ious": [0.8],
        "whole_iou": [[0.8]],
        "gt_shapes": {"shapes": [{
            "cls_id": 1,
            "label": "cat",
            "points": [[10,20], [30,40]],
            "shape_type": "polygon",
            "id": 0,
            "area": 200
        }]},
        "pred_shapes": {"shapes": [{
            "cls_id": 1,
            "label": "cat",
            "points": [[12,22], [32,42]],
            "shape_type": "polygon",
            "id": 1,
            "area": 210
        }]},
        "cm": [[1,0], [0,1]],
        "p": [[1.0,0.0], [0.0,1.0]],
        "r": [[1.0,0.0], [0.0,1.0]],
        "mean_results": [1.0, 1.0],
        "ap": [1.0, 1.0]
    })

    # 转换为字典（可序列化为JSON）
    print(result.model_dump())