<template>
  <div>
    <h3>WebSocket 轮询示例</h3>
    <div>
      <p>任务状态: {{ taskStatus }}</p>
      <button @click="startPolling">开始轮询</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const taskStatus = ref('等待任务开始...');  // 存储任务状态
let ws = null;  // WebSocket 实例
let pollingInterval = null;  // 轮询定时器

// 1. 连接 WebSocket
const connectWebSocket = () => {
  ws = new WebSocket('ws://10.110.10.131:6119/ws');
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };

  ws.onmessage = (event) => {
    console.log('Received from server:', event.data);
    taskStatus.value = event.data;  // 更新任务状态
  };

  ws.onclose = () => {
    console.log('WebSocket closed');
  };
};

// 2. 开始轮询
const startPolling = () => {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    alert('WebSocket 连接未成功建立');
    return;
  }

  // 轮询请求任务状态
  pollingInterval = setInterval(() => {
    console.log('发送轮询请求');
    // 模拟轮询任务状态
    // 你可以用 Axios 或 Fetch 发起请求到后端获取任务状态
    ws.send('GET_TASK_STATUS');  // 向 WebSocket 服务发送轮询请求
  }, 5000);  // 每 5 秒发送一次请求
};

// 3. 关闭轮询
const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
};

// 清理工作
onUnmounted(() => {
  if (ws) {
    ws.close();
  }
  stopPolling();
});

onMounted(() => {
  connectWebSocket();  // 在组件加载时连接 WebSocket
});
</script>