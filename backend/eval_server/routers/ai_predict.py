import cv2
import numpy as np
import time 
import json
import torch
import sys
from semvision.characteristic.common import get_image_data_with_ai_recognition
from src.utils import img2base64, labelme_to_mask
from eval_server.eval_config import  logger_dir
from eval_server.routers.logger import create_logger

# 配置日志
logger = create_logger(logger_dir,"predict")

def ai_predict_image(phrase_target,
                model_category, 
                filepath_or_buffer, 
                save_path_bmp,
                save_path_json, 
                filename, 
                img_base64,
                # task_id,
                ):
    """
    模型预测图像
    改为和semvision中的调用完全一致。
    """
    start_time = time.time()
    zw_result = get_image_data_with_ai_recognition(
            origin_path = filepath_or_buffer,
            phrase_target=phrase_target,
            model_category=model_category,
            diameter=0,
            remove_ruler_watermark=1)
    
    mask = labelme_to_mask(zw_result)  # 当前只考虑二次颗粒和一次颗粒的情况，只支持一个类别label，否则就要直接改原来的函数了，增加各个模型处理的mask返回。
    return_type = 'json'
    save_path = save_path_json
    with open(save_path,'w',encoding='utf-8') as file:
            json.dump(zw_result, file)

    h,w = mask.shape
    result =  {
        'predict': 'data:image/png;base64,' + img2base64(mask),
        'result_type': return_type,
        'image': 'data:image/png;base64,' +img_base64,
        'width': w,
        'height': h,
        'filename': filename
    }
    torch.cuda.empty_cache()
    elapsed_time = time.time() - start_time
    logger.info(f"预测结束，函数耗时: {elapsed_time:.3f} s")
    return result


