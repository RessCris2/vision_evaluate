from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any, Union
from typing_extensions import Annotated

# 类型别名
PositiveInt = Annotated[int, Field(ge=0)]
PositiveFloat = Annotated[float, Field(ge=0)]
BBoxCoord = Annotated[Union[float, int], Field()]

class BBox(BaseModel):
    """边界框模型 (xyxy格式)"""
    xmin: BBoxCoord
    ymin: BBoxCoord
    xmax: BBoxCoord
    ymax: BBoxCoord

    @field_validator('xmax', 'ymax')
    @classmethod
    def validate_coords(cls, v: float, values: Dict[str, Any]) -> float:
        """确保max坐标大于min坐标"""
        field_name = cls.__fields__[values['field_name']].name
        min_field = field_name.replace('max', 'min')
        if v <= values.data.get(min_field, v + 1):
            raise ValueError(f"{field_name}必须大于{min_field}")
        return v

class Annotation(BaseModel):
    """标注模型 (兼容COCO格式)"""
    id: PositiveInt
    image_id: PositiveInt
    category_id: PositiveInt
    bbox: Optional[List[PositiveFloat]] = Field(
        None, 
        min_length=4,
        max_length=4,
        description="COCO格式 [x,y,width,height]"
    )
    segmentation: Optional[List[List[PositiveFloat]]] = Field(
        None,
        description="多边形坐标 [[x1,y1,x2,y2,...]] 或 RLE"
    )
    area: Optional[PositiveFloat] = None
    iscrowd: Optional[Annotated[int, Field(ge=0, le=1)]] = 0
    ignore: Optional[bool] = None

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "id": 1,
                "image_id": 123,
                "category_id": 1,
                "bbox": [10, 20, 100, 150],
                "segmentation": [[10, 20, 100, 150]],
                "area": 1300.0,
                "iscrowd": 0
            }
        }
    )

class Image(BaseModel):
    """图像元数据模型"""
    id: PositiveInt
    file_name: Optional[str] = Field(
        None,
        pattern=r'^[a-zA-Z0-9_\-\.]+$',
        description="文件名（不含路径）"
    )
    width: PositiveInt
    height: PositiveInt
    license: Optional[PositiveInt] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 123,
                "file_name": "example.jpg",
                "width": 640,
                "height": 480
            }
        }
    )

class Category(BaseModel):
    """类别模型"""
    id: PositiveInt
    name: str = Field(min_length=1)
    supercategory: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "person",
                "supercategory": "living"
            }
        }
    )

class COCODataset(BaseModel):
    """完整的COCO数据集模型"""
    info: Optional[Dict[str, Any]] = Field(
        None,
        description="数据集元信息"
    )
    licenses: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="许可证信息"
    )
    images: List[Image]
    annotations: List[Annotation]
    categories: List[Category]
    type: str = Field(
        default="instance",
        pattern="^(instance|stuff|keypoint)$"
    )

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "info": {"description": "Example dataset"},
                "licenses": [{"name": "CC-BY"}],
                "images": [Image.model_config["json_schema_extra"]["example"]],
                "annotations": [Annotation.model_config["json_schema_extra"]["example"]],
                "categories": [Category.model_config["json_schema_extra"]["example"]]
            }
        }
    )

# 使用示例
if __name__ == "__main__":
    # 构建完整数据集
    dataset = COCODataset(
        info={"description": "Test dataset"},
        licenses=[{"name": "MIT"}],
        images=[Image(id=1, file_name="test.jpg", width=640, height=480)],
        categories=[Category(id=1, name="cat")],
        annotations=[
            Annotation(
                id=1,
                image_id=1,
                category_id=1,
                bbox=[10, 20, 100, 150],
                segmentation=[[10, 20, 100, 150]],
                area=1300.0
            )
        ]
    )

    # 序列化输出
    print(dataset.model_dump_json(indent=2))