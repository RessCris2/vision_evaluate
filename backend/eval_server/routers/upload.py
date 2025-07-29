
import os
import uuid
import shutil  
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Form,  File, UploadFile

from eval_server.routers.logger import create_logger
from eval_server.rq.producer import send_to_queue
from eval_server.eval_config import UPLOAD_FOLDER, logger_dir

# 配置日志
logger = create_logger(logger_dir,"upload")
router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)


# @app.post(f"/{API_PREFIX}/upload_file_and_queue")
@router.post("/queue")
async def upload_file_and_queue(phrase_target:str = Form(...),
                                 model_category:str = Form(...), 
                                 task_id:str = Form(...),
                                 predict_type:str = Form(...),
                                 file: UploadFile = File(...)):
    """只上传图片文件
    """
    if file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="请上传图片文件，不要上传 json 文件")
    else:
        # 非json的图片文件
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        try:
            task = {
                "id": str(uuid.uuid4()),
                "phrase_target": phrase_target,
                "model_category": model_category,
                "filename": file.filename,
                "filepath": path,
                "task_id": task_id,
                # "websocket_connections": websocket_connections
            }
            if os.path.exists(path):
                os.remove(path)
            
            with open(path, "wb") as buffer:  
                shutil.copyfileobj(file.file, buffer)  

            send_to_queue(data =task, queue_name=predict_type)
            logger.info(f"任务已发送到队列: {file.filename}")
        except Exception as e:
            logger.error(f"Failed to send task to queue: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {e}")

    return f'图片上传 {file.filename} ok'

@router.post("/labelme_json")
async def upload_json_file(labelme_json: UploadFile = File(...)):
    filename_without_extension = os.path.splitext(labelme_json.filename)[0]
    labelme_path = os.path.join(UPLOAD_FOLDER, f"{filename_without_extension}_labelme.json")
    if os.path.exists(labelme_path):
        os.remove(labelme_path)
    
    logger.info(f"labelme_path {labelme_path}")
    # 将文件写入到指定目录  
    with open(labelme_path, "wb") as buffer:  
        shutil.copyfileobj(labelme_json.file, buffer)  
    return f"json {filename_without_extension} ok"


@router.post("/original_image_and_json")
async def upload_original_image_and_json(file: UploadFile = File(...)):
    # filename_without_extension = os.path.splitext(file.filename)[0]
    # 如果是 json 则增加 _labelme 后缀
    if file.filename.endswith(".json"):
        filename_without_extension = os.path.splitext(file.filename)[0]
        filename = f"{filename_without_extension}_labelme.json"
    else:
        filename = file.filename
    upload_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(upload_path):
        os.remove(upload_path)
    
    logger.info(f"upload_path {upload_path}")
    # 将文件写入到指定目录  
    with open(upload_path, "wb") as buffer:  
        shutil.copyfileobj(file.file, buffer)  
    return f"file {file.filename} ok"


@router.post("/result_labelme_json")
async def upload_result_json_file(result_labelme_json: UploadFile = File(...)):
    filename_without_extension = os.path.splitext(result_labelme_json.filename)[0]
    labelme_path = os.path.join(UPLOAD_FOLDER, f"{filename_without_extension}_mask.json")
    if os.path.exists(labelme_path):
        os.remove(labelme_path)
    
    logger.info(f"labelme_path {labelme_path}")
    # 将文件写入到指定目录  
    with open(labelme_path, "wb") as buffer:  
        shutil.copyfileobj(result_labelme_json.file, buffer)  
    
    from eval_server.routers.predict import process_result_json
    import glob
    # 处理结果 json 文件
    # pattern = os.path.join(UPLOAD_FOLDER, filename_without_extension)
    imgpath = os.path.join(UPLOAD_FOLDER, f"{filename_without_extension}.jpg")
    result = process_result_json(imgpath, labelme_path)
    
    logger.info( f"json {filename_without_extension} ok")
    return result
