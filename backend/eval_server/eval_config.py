import os
import json
import redis
from dotenv import load_dotenv
from eval_server.routers.logger import create_logger
from pathlib import Path as PathLibPath
# 加载环境变量
# dotenv_path = PathLibPath(__file__).resolve().parents[2] / "server/.env"
# load_dotenv(dotenv_path)

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
# redis_config = os.getenv("REDIS_CONFIG")
redis_config =json.loads( os.getenv("REDIS_CONFIG"))
redis_client = redis.Redis(**redis_config)

QUEUE_NAME = os.getenv("QUEUE_NAME")
OPTON_QUEUE_NAME = os.getenv("OPTON_QUEUE_NAME")
AI_QUEUE_NAME = os.getenv("AI_QUEUE_NAME")

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

# 配置日志
logger_dir = os.getenv("LOG_DIR")