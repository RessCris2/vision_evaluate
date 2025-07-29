import time
import json
import numpy as np
from PIL import Image
import base64
import io
import cv2

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        print(f"{func.__name__} finished in {end_time - start_time:.6f} seconds.")

        return result

    return wrapper


def read_json(filename):
    with open(filename, 'r') as f:  
        # 读取文件内容，并将其解析为Python字典  
        data = json.load(f)  
        print("读取 json 成功！")
    return data


def  write_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)


def img2base64(img_or_path):
    """将图片读成 base64 格式
    """
    if isinstance(img_or_path, str):
        img  = Image.open(img_or_path)
    elif isinstance(img_or_path, np.ndarray):
        img = Image.fromarray(img_or_path)
    else:
        raise "只支持图片路径和 numpy array!"

    img_byte_arr =  io.BytesIO()  
    img.save(img_byte_arr, format='PNG')  
    
    # 转换为Base64  
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')  
    return img_base64


def labelme_to_mask(labelme_result):
    """
    将 labelme 的结果转换为 mask
    :param labelme_result: labelme 的结果
    :return: mask
    """
    if not isinstance(labelme_result, dict):
        raise ValueError("labelme_result must be a dict")
    
    if 'shapes' not in labelme_result:
        raise ValueError("labelme_result must contain 'shapes' key")
    
    shapes = labelme_result['shapes']
    if not shapes:
        return np.zeros((labelme_result['imageHeight'], labelme_result['imageWidth']), dtype=np.uint8)
    
    mask = np.zeros((labelme_result['imageHeight'], labelme_result['imageWidth']), dtype=np.uint8)
    
    for shape in shapes:
        points = np.array(shape['points'], dtype=np.int32)
        cv2.fillPoly(mask, [points], 1)
    
    return mask