# consumer.py
import os
import io
import json
import numpy as np
from PIL import Image
import base64


import argparse
from dotenv import load_dotenv
import redis
import pika

import sys
from pathlib import Path as PathLibPath
sys.path.append(str(PathLibPath(__file__).resolve().parents[2] ))
from eval_server.routers.logger import create_logger


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

class Consumer:
    

    def __init__(self, queue_name="opton-dev",
                 rabbitmq_url="amqp://guest:guest@localhost:5672/",
                 redis_client=redis.Redis(host="localhost", port=6379, db=0),
                 logger=None,
                 ):
        self.connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        self.channel = self.connection.channel()
        self.channel.queue_purge(queue=queue_name)  # 删除队列
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)  # 限制每次最多处理 1 个任务
        self.queue_name = queue_name
        self.redis_client = redis_client
        self.logger = logger

    def publish_to_websocket_channel(self, task_id, result):
        self.redis_client.publish(task_id, result)  # 发布任务结果

    def callback(self, ch, method, properties, body):
        from eval_server.routers.predict import process_image
        try:
            task_id = json.loads(body.decode('utf-8'))['task_id']
            filename = json.loads(body.decode('utf-8'))["filename"]
            result = process_image(body, self.queue_name)
            ch.basic_ack(delivery_tag=method.delivery_tag)  # 确认消息
            self.logger.info(f"Task {task_id}-{filename} completed.")
            if isinstance(result, dict):
                result = json.dumps(result)
            self.publish_to_websocket_channel(task_id, result)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        self.logger.info(f"Consumer  {self.queue_name } started. Waiting for messages...")
        self.channel.start_consuming()


# 配一个 cli，传入不同 queue_name
def main():
    # parser = argparse.ArgumentParser(description="Start a consumer for a specific queue.")
    # parser.add_argument("--queue_name", type=str, default="opton-dev", help="The name of the queue to consume from.")
    # parser.add_argument("--env_file", type=str, help="env file path")
    # args = parser.parse_args()

    # 加载环境变量
    # dotenv_path = PathLibPath(__file__).resolve().parents[2] / "server/.env"
    # 因为 2025年6月16日发现，该项目的 args 与 semvision 总的argsparser冲突，这里改为手动传入
    # load_dotenv(args.env_file)
    # load_dotenv("/home/zwuser/app/vision/vision_eval/backend/eval_server/.env.test")
    load_dotenv("/home/zwuser/app/vision/vision_eval/backend/eval_server/.env.development")


    redis_config =json.loads( os.getenv("REDIS_CONFIG"))
    redis_client = redis.Redis(**redis_config)
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    AI_QUEUE_NAME = os.getenv("AI_QUEUE_NAME")

    # 配置日志
    log_dir = os.getenv("LOG_DIR")
    logger = create_logger(log_dir, f"consumer_{AI_QUEUE_NAME}")

    consumer = Consumer(queue_name=AI_QUEUE_NAME,
                        rabbitmq_url=RABBITMQ_URL,
                        redis_client=redis_client,
                        logger=logger)
    consumer.start()

# if __name__ == "__main__":
    # consumer = Consumer("opton")
    # consumer.start()

if __name__ == "__main__":
    # 模拟终端传参数跑 main, cli
    # sys.argv = [
    #     'consumer.py',  # 脚本的名称（通常可以随便设置，主要是用于 main 函数中的处理）
    #     '--queue_name', 'ai-test',  # 参数1：指定队列名称
    #     '--env_file', "/home/zwuser/app/vision/vision_eval/backend/server/.env.test" # 参数1：指定环境变量文件
    # ]
    main()
