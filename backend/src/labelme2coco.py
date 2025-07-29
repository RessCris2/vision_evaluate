#!/usr/bin/env python
"""
labelme 可以有文件夹，也可以有文件形式
"""

import argparse
import collections
import datetime
import glob
import json
import os
import os.path as osp
import sys
import uuid

import imgviz
import numpy as np

import labelme
from typing import Union, List, Tuple, Dict

# sys.path.append(r"X:\06_项目\04_欧波同\code\opton_eval\opton_eval")
from src.utils import write_json
from src import labelfile

try:
    import pycocotools.mask
except ImportError:
    print("Please install pycocotools:\n\n    pip install pycocotools\n")
    sys.exit(1)


def read_json(filename):
    with open(filename, 'r') as f:  
        data = json.load(f)  
        # print("读取 json 成功！")
    return data

def single_file(filename:str, labels_pathordict: Union[str, Dict],  image_id:int=0, save_or_path:Union[str, bool]=False):
    """
    :param filename:
    :param image_id:
    :param labels_pathordict :
            原class_name_to_id: 格式为
                    class_name_to_id={"secondary_particle":1,
                            "Micropowder":2,
                            "SQ": 3}
            labelme 中处理标签的逻辑是从外面导入的：
            1、labels.txt
            2、dict   class_name_to_id={"secondary_particle":1,
                            "Micropowder":2,
                            "SQ": 3}
    :return:
        coco 格式的 json
    """
    now = datetime.datetime.now()

    data = dict(
        info=dict(description=None,url=None,version=None,year=now.year,contributor=None,date_created=now.strftime("%Y-%m-%d %H:%M:%S.%f")  ),
        licenses=[ dict( url=None, id=0, name=None, )],
        images=[
            # license, url, file_name, height, width, date_captured, id
        ],
        type="instances",
        annotations=[
            # segmentation, area, iscrowd, image_id, bbox, category_id, id
        ],
        categories=[
            # supercategory, id, name
        ],
    )

    # label_file = labelme.LabelFile(filename=filename)
    label_file = labelfile.LabelFile(filename=filename)

    # TODO: 可以统一从外面传入
    # 处理 具体类别 信息
    if isinstance(labels_pathordict, str):
        class_name_to_id = {}
        for i, line in enumerate(open(labels_pathordict).readlines()):
            class_id = i - 1  # starts with -1
            class_name = line.strip()
            if class_id == -1:
                assert class_name == "__ignore__"
                continue
            class_name_to_id[class_name.lower()] = class_id

    else:
        # class_name_to_id = labels_pathordict
        # 都改成小写class_name
        class_name_to_id = {k.lower():v for k,v in labels_pathordict.items()}

    # 增加类别信息
    for class_name, class_id in class_name_to_id.items():
        data["categories"].append( dict(supercategory=None, id=class_id,  name=class_name ) )

    base = osp.splitext(osp.basename(filename))[0]
    if label_file.imageData is not None:
        img = labelme.utils.img_data_to_arr(label_file.imageData)
        h, w = img.shape[:2]
    else:
        # h, w = label_file.imageHeight, label_file.imageWidth
        file = read_json(filename)
        h, w = file['imageHeight'], file['imageWidth']

    data["images"].append(
        dict(
            license=0,
            url=None,
            file_name=label_file.imagePath, # TODO: 这里应该是图片路径
            height=h,
            width=w,
            date_captured=None,
            id=image_id,
        )
    )
    masks = {}  # for area
    segmentations = collections.defaultdict(list)  # for segmentation
    for shape in label_file.shapes:
        points = shape["points"]
        if len(points) < 3: # 避免出现只有一个point len=2, 以及 不超过2个点的情况。
            continue
        label = shape["label"]
        group_id = shape.get("group_id")
        shape_type = shape.get("shape_type", "polygon")
        mask = labelme.utils.shape_to_mask(
            (h, w), points, shape_type
        )

        if group_id is None:
            group_id = uuid.uuid1()

        instance = (label, group_id)

        if instance in masks:
            masks[instance] = masks[instance] | mask
        else:
            masks[instance] = mask

        if shape_type == "rectangle":
            (x1, y1), (x2, y2) = points
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            points = [x1, y1, x2, y1, x2, y2, x1, y2]
        if shape_type == "circle":
            (x1, y1), (x2, y2) = points
            r = np.linalg.norm([x2 - x1, y2 - y1])
            # r(1-cos(a/2))<x, a=2*pi/N => N>pi/arccos(1-x/r)
            # x: tolerance of the gap between the arc and the line segment
            n_points_circle = max(int(np.pi / np.arccos(1 - 1 / r)), 12)
            i = np.arange(n_points_circle)
            x = x1 + r * np.sin(2 * np.pi / n_points_circle * i)
            y = y1 + r * np.cos(2 * np.pi / n_points_circle * i)
            points = np.stack((x, y), axis=1).flatten().tolist()
        else:
            points = np.asarray(points).flatten().tolist()

        segmentations[instance].append(points)
    segmentations = dict(segmentations)

    for index, (instance, mask) in enumerate(masks.items()):
        cls_name, group_id = instance
        if cls_name.lower() not in class_name_to_id:
            continue
        cls_id = class_name_to_id[cls_name.lower()]

        mask = np.asfortranarray(mask.astype(np.uint8))
        mask = pycocotools.mask.encode(mask)
        area = float(pycocotools.mask.area(mask))
        bbox = pycocotools.mask.toBbox(mask).flatten().tolist()

        data["annotations"].append(
            dict(
                id=len(data["annotations"]),
                image_id=image_id,
                category_id=cls_id,
                segmentation=segmentations[instance],
                area=area,
                bbox=bbox,
                iscrowd=0,
            )
        )

        if save_or_path:
            write_json(save_or_path, data)

    return data


def dir_file(labelme_dir: str, labels_pathordict: Union[str, Dict], output_dir: Union[str, None]=None,  save:bool=False):
    """
    TODO: 可以增加是否要保存原图和visualization的选择
    
    imageData 标注文件中不一定与 imageData


    :param labelme_dir:
    :param output_dir:
    :param labels_pathordict:
    :return:
    """
    # 处理 具体类别 信息
    if isinstance(labels_pathordict, str):
        class_name_to_id = {}
        for i, line in enumerate(open(labels_pathordict).readlines()):
            class_id = i - 1  # starts with -1
            class_name = line.strip()
            if class_id == -1:
                assert class_name == "__ignore__"
                continue
            class_name_to_id[class_name] = class_id

    else:
        class_name_to_id = labels_pathordict

    if save == True:
        # 当前路径
        if output_dir is None:
            os.makedirs("JPEGImages", exist_ok=True)
            out_ann_file =  "annotations.json"

        # 或指定路径
        else:
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(osp.join(output_dir, "JPEGImages"),  exist_ok=True)
            out_ann_file = osp.join(output_dir, "annotations.json")

    now = datetime.datetime.now()

    # # 增加基础信息
    data = dict(
        info=dict(description=None, url=None, version=None, year=now.year,contributor=None,
            date_created=now.strftime("%Y-%m-%d %H:%M:%S.%f"),
        ),
        licenses=[ dict( url=None, id=0, name=None,) ],
        images=[
            # license, url, file_name, height, width, date_captured, id
        ],
        type="instances",
        annotations=[
            # segmentation, area, iscrowd, image_id, bbox, category_id, id
        ],
        categories=[
            # supercategory, id, name
        ],
    )

    # 增加类别信息
    for class_id, class_name in class_name_to_id.items():
        data["categories"].append(
            dict(
                supercategory=None,
                id=class_id,
                name=class_name,
            )
        )

    # 获取输入文件夹中的所有 labelme json文件
    label_files = glob.glob(osp.join(labelme_dir, "*.json"))
    for image_id, filename in enumerate(label_files):
        print("Generating dataset from:", filename)
        # label_file = labelme.LabelFile(filename=filename)
        label_file = labelfile.LabelFile(filename=filename)
        base = osp.splitext(osp.basename(filename))[0]

        out_img_file = osp.join(output_dir, "JPEGImages", base + ".jpg")
        img = labelme.utils.img_data_to_arr(label_file.imageData)
        imgviz.io.imsave(out_img_file, img)

        data["images"].append(
            dict(
                license=0,
                url=None,
                file_name=osp.relpath(out_img_file, osp.dirname(out_ann_file)),
                height=img.shape[0],
                width=img.shape[1],
                date_captured=None,
                id=image_id,
            )
        )

        masks = {}  # for area
        segmentations = collections.defaultdict(list)  # for segmentation
        for shape in label_file.shapes:
            points = shape["points"]
            label = shape["label"]
            group_id = shape.get("group_id")
            shape_type = shape.get("shape_type", "polygon")
            mask = labelme.utils.shape_to_mask(
                img.shape[:2], points, shape_type
            )

            if group_id is None:
                group_id = uuid.uuid1()

            instance = (label, group_id)

            if instance in masks:
                masks[instance] = masks[instance] | mask
            else:
                masks[instance] = mask

            if shape_type == "rectangle":
                (x1, y1), (x2, y2) = points
                x1, x2 = sorted([x1, x2])
                y1, y2 = sorted([y1, y2])
                points = [x1, y1, x2, y1, x2, y2, x1, y2]
            if shape_type == "circle":
                (x1, y1), (x2, y2) = points
                r = np.linalg.norm([x2 - x1, y2 - y1])
                # r(1-cos(a/2))<x, a=2*pi/N => N>pi/arccos(1-x/r)
                # x: tolerance of the gap between the arc and the line segment
                n_points_circle = max(int(np.pi / np.arccos(1 - 1 / r)), 12)
                i = np.arange(n_points_circle)
                x = x1 + r * np.sin(2 * np.pi / n_points_circle * i)
                y = y1 + r * np.cos(2 * np.pi / n_points_circle * i)
                points = np.stack((x, y), axis=1).flatten().tolist()
            else:
                points = np.asarray(points).flatten().tolist()

            segmentations[instance].append(points)
        segmentations = dict(segmentations)

        for instance, mask in masks.items():
            cls_name, group_id = instance
            if cls_name.replace(" ", "_") == 'secondary_particle':
                cls_name = 'secondary_particle'
            if cls_name not in class_name_to_id:
                continue
            cls_id = class_name_to_id[cls_name]

            mask = np.asfortranarray(mask.astype(np.uint8))
            mask = pycocotools.mask.encode(mask)
            area = float(pycocotools.mask.area(mask))
            bbox = pycocotools.mask.toBbox(mask).flatten().tolist()

            data["annotations"].append(
                dict(
                    id=len(data["annotations"]),
                    image_id=image_id,
                    category_id=cls_id,
                    segmentation=segmentations[instance],
                    area=area,
                    bbox=bbox,
                    iscrowd=0,
                )
            )

        if not noviz:
            viz = img
            if masks:
                labels, captions, masks = zip(
                    *[
                        (class_name_to_id[cnm], cnm, msk)
                        for (cnm, gid), msk in masks.items()
                        if cnm in class_name_to_id
                    ]
                )
                viz = imgviz.instances2rgb(
                    image=img,
                    labels=labels,
                    masks=masks,
                    captions=captions,
                    font_size=15,
                    line_width=2,
                )
            out_viz_file = osp.join(
                output_dir, "Visualization", base + ".jpg"
            )
            imgviz.io.imsave(out_viz_file, viz)

    with open(out_ann_file, "w") as f:
        json.dump(data, f)

    return data

