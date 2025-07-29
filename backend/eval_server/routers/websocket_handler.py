# import aioredis
from redis import asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from eval_server.routers.logger import create_logger
from eval_server.eval_config import logger_dir, redis_client


# # 配置日志
logger = create_logger(logger_dir,"websocket_handler")

websocket_connections = {}  # 全局变量保存 websocket 连接

def publish_to_websocket_channel(task_id, result):
    redis_client.publish(f"task_updates:{task_id}", result)  # 发布任务结果

async def listen_for_task_updates(websocket: WebSocket, task_id: str):
    redis = await aioredis.from_url('redis://10.110.10.131:6379')  # 创建异步 Redis 客户端
    # redis = await aioredis.from_url('redis://localhost:6379')  # 创建异步 Redis 客户端
    pubsub = redis.pubsub()
    await pubsub.subscribe(task_id)  # 订阅对应的任务频道

    async for message in pubsub.listen():
        if message["type"] == "message":
            # 当接收到消息时，发送到前端
            # data = str(json.loads(message['data']))
            data = message['data'].decode('utf-8')
            await websocket.send_json(data)
            # await websocket.send_text({ message['data']})

router = APIRouter(
    prefix="/websocket_conn",
    tags=["websocket_conn"],
)

@router.websocket("/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    websocket_connections[task_id] = websocket  # 保存连接
    await listen_for_task_updates(websocket, task_id)
    try:
        while True:
            data = await websocket.receive_text()  # 接收信息保持连接活跃
            print(f"Received message: {data}")
            # 处理接收到的信息
            await websocket.send_text(f"Message received: {data}")  # 发送回执
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        websocket_connections.pop(task_id, None)  # 移除连接

@router.websocket("/{task_id}/status")
async def websocket_status(websocket: WebSocket, task_id: str):
    await websocket.accept()
    status = redis_client.get(task_id)
    await websocket.send_text(str("test"))
    return status