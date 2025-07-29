"""
    与前端交互的数据格式
"""
from pydantic import BaseModel, validator, conint, confloat
from typing import List, Optional, Tuple, Union


# 定义点的类型
class Point(BaseModel):
    x: Union[int, float]
    y: Union[int, float]

    class Config:
        # 确保x和y都作为一个元组（尽管在这里是分开定义的，但可以视作元组的模拟）
        # 或者可以考虑直接使用Tuple[Union[int, float], Union[int, float]]并重新实现to_dict等，但这将失去Pydantic的验证特性
        arbitrary_types_allowed = True
class Shape(BaseModel):
    label: str
    points: List[Point]
    shape_type: str

    # TODO:一次颗粒需要增加 conf


# 使用Pydantic模型定义ImageData的类型
class ImageData(BaseModel):
    shapes: List[Shape]
    imageHeight: conint(ge=1)  # 确保imageHeight是整数且大于等于1
    imageWidth: conint(ge=1)  # 确保imageWidth是整数且大于等于1
    imageData: Optional[str]  # 可选的ImageData字段; base64编码的图像数据
    imagePath: Optional[str]  # 可选的image_path字段; 图像路径