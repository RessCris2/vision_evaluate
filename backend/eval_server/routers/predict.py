import cv2
import os
import numpy as np
import time 
import json
import torch

# from src.vision.tasks.predict.secondary_particle import SecondaryParticlePredictor
# # from opton_eval.vision.tasks.predict.crack_ball import CrackBallPredictor
# from src.vision.tasks.predict.micro_powder import MicroPowderPredictor
# from src.vision.tasks.predict.primary_particle import PrimaryParticlePredictor
from src.utils import img2base64, labelme_to_mask
from eval_server.eval_config import UPLOAD_FOLDER, logger_dir, QUEUE_NAME, OPTON_QUEUE_NAME, AI_QUEUE_NAME

from eval_server.routers.logger import create_logger
from eval_server.routers.ai_predict import ai_predict_image
# from server.routers.opton_predict import opton_predict_image
from fastapi import APIRouter
router = APIRouter(
    prefix="/predict",
    tags=["predict"],
)

# 配置日志
logger = create_logger(logger_dir,"predict")

def process_image(body, queue_name):
    # 解码任务数据
    task_body = json.loads(body.decode('utf-8'))
    filename = task_body["filename"]
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    phrase_target = task_body['phrase_target']
    model_category = task_body['model_category']

    
    if queue_name == AI_QUEUE_NAME:
            result = ai_predict_image(
                phrase_target=phrase_target,
                model_category=model_category,
                filepath_or_buffer=filepath,
                save_path_bmp=os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(filename)[0]}_mask.bmp"),
                save_path_json=os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(filename)[0]}_mask.json"),
                filename=filename,
                img_base64=img2base64(filepath),
                # task_id=task_id,
            )
    else:
        raise ValueError("Queue name error.")
    
    logger.info(f"File {filename} processed and saved.") # 打印日志
    return result

@router.get(f"/process_result_json")  # noqa: F541
def process_result_json(imgpath, result_json):
    """不需要预测，直接处理结果 json 文件
    imgpath: 图片路径
    result_json: 结果 json 文件路径
    """
    filename = os.path.basename(imgpath)
    start_time = time.time()
    with open(result_json, 'r', encoding='utf-8') as file:
        zw_result = json.load(file)
    mask = labelme_to_mask(zw_result)
    return_type = 'json'
    h,w = mask.shape
    result =  {
        'predict': 'data:image/png;base64,' + img2base64(mask),
        'result_type': return_type,
        'image': 'data:image/png;base64,' +img2base64(imgpath),
        'width': w,
        'height': h,
        'filename': filename
    }
    elapsed_time = time.time() - start_time
    logger.info(f"上传文件结束，耗时: {elapsed_time:.3f} s")
    return result