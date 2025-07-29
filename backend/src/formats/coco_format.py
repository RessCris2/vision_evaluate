"""
coco 格式的数据集

"""
from pydantic import BaseModel, conint, confloat, validator, Field, Extra
from typing import List, Optional, Dict, Any, Union


class BBox(BaseModel):
    xmin: Union[float, int]
    ymin: Union[float, int]
    xmax: Union[float, int]
    ymax: Union[float, int]


# 边界框的模型
class Annotation(BaseModel):
    id: conint(ge=0)
    image_id: conint(ge=0)
    category_id: conint(ge=0)
    bbox: Optional[List[float]] # 改成可选的，mask可以没有bbox吧？
    segmentation: Optional[List[List[confloat(ge=0)]]] = None  # 可以是RLE或polygon格式 "segmentation": [[x1, y1, x2, y2, ..., xn, yn]]
    area: Optional[confloat(ge=0)] = None
    iscrowd: Optional[int] = 0
    ignore: Optional[bool] = None

# 如何表达还可以有其他字段？
class Image(BaseModel):
    id: conint(ge=0)
    file_name: Optional[Union[str, int]] = None
    width: int
    height: int

class Category(BaseModel):
    id: conint(ge=0)
    name: str
    supercategory: Union[str, None] = None


# 包含多个标注的图像模型
class COCOImage(BaseModel, extra=Extra.allow):
    info: Optional[Dict[str, Any]]
    licenses: List[Dict[str, Any]]
    images: List[Image]
    categories: List[Category]
    type: str="instance"
    annotations: List[Annotation]
    # 可以根据需要添加更多图像相关的字段，如license等



# 示例使用
if __name__ == "__main__":
    annotation = COCOAnnotation(
        id=1,
        image_id=123,
        category_id=1,
        bbox=BBox(xmin=10, ymin=20, xmax=150, ymax=100),
        segmentation=[[10, 20, 150, 100]],  # 示例，实际应为更复杂的polygon或RLE
        area=1300,
        iscrowd=False,
        ignore=False
    )

    image = COCOImage(
        id=123,
        file_name='example.jpg',
        height=480,
        width=640,
        annotations=[annotation]
    )

    print(annotation)
    print(image)