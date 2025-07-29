"""
尝试使用队列模式来处理图片预测任务
TODO:unet 以及 yolo 这种事前就加载的行为，不太合理
"""
import os
import json

import threading
import asyncio
import redis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path as PathLibPath
from eval_server.routers import upload 
from eval_server.routers import evaluate 
from eval_server.routers.websocket_handler import router as websocket_router
from eval_server.routers.logger import create_logger
from eval_server.eval_config import UPLOAD_FOLDER, logger_dir, redis_client, RABBITMQ_URL, QUEUE_NAME, OPTON_QUEUE_NAME


API_PREFIX = os.getenv("API_PREFIX")
# 配置日志
logger = create_logger(logger_dir,"main")

# 设置上传文件保存目录  
# UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")  
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  

# 创建 FastAPI 实例
app = FastAPI(title="eval",
              version="1.0.0",
              openapi_version="3.0.0",)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.110.10.131:6622","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(websocket_router)

# 增加心跳测试路由
@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(upload.router, prefix=API_PREFIX)
# app.include_router(predict.router)
app.include_router(evaluate.router,prefix=API_PREFIX)


if __name__ == "__main__":
    import uvicorn
    env_file_path ="/home/zwuser/app/vision/vision_eval/backend/eval_server/.env.development"
    uvicorn.run("main:app", host="0.0.0.0", port=8019, reload=False, env_file=env_file_path)
