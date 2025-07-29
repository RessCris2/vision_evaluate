# 用于将任务推送到队列
import os
import pika
import json
import pika.exceptions

from dotenv import load_dotenv
from eval_server.routers.logger import create_logger
from pathlib import Path as PathLibPath
import redis
from eval_server.eval_config import UPLOAD_FOLDER, logger_dir, redis_client, QUEUE_NAME, OPTON_QUEUE_NAME,RABBITMQ_URL

# 加载环境变量
# dotenv_path = PathLibPath(__file__).resolve().parents[2] / "server/.env"
# load_dotenv(dotenv_path)


# 配置日志
logger = create_logger(logger_dir, "producer")

# UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
# redis_config =json.loads( os.getenv("REDIS_CONFIG"))
# redis_client = redis.Redis(**redis_config)
# QUEUE_NAME = os.getenv("QUEUE_NAME")
# OPTON_QUEUE_NAME = os.getenv("OPTON_QUEUE_NAME")
# RABBITMQ_URL = os.getenv("RABBITMQ_URL")

class RabbitManager:
    # _instance = None

    # def __new__(cls, *args, **kwargs):
    #     if not cls._instance:
    #         cls._instance = super(RabbitManager, cls).__new__(cls, *args, **kwargs)
    #     return cls._instance

    def __init__(self, queue_name):
        # if not hasattr(self, 'initialized'):
        self.connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)  # 限制每次最多处理 1 个任务
        # self.initialized = True
        self.queue_name = queue_name

    def send(self, message):
        # 将任务推送到队列
        try:
            self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(message))
            print(f" [x] Sent {message}")
        except pika.exceptions.AMQPChannelError:
            self.connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.channel.basic_qos(prefetch_count=1)  # 限制每次最多处理 1 个任务
            self.initialized = True
            self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(message))
            print(f" [x] Sent {message}")
        except Exception as e:
            print(f" [x] Error: {e}")

    def close(self):
        self.connection.close()

    def purge_queue(self):
        # 清空队列中的任务
        self.channel.queue_purge(queue=self.queue_name)
        print(f" [x] Purged queue {self.queue_name}")


def clear_queue(queue_name):
    rabbit_manager = RabbitManager(queue_name)
    rabbit_manager.purge_queue()
    # rabbit_manager.close()

def send_to_queue(data, queue_name):
    rabbit_manager = RabbitManager(queue_name)
    rabbit_manager.send(data)
    rabbit_manager.close()
