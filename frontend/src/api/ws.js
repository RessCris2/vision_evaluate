export class WebSocketManager {
  constructor(url, task_id, file_name, onMessageCallback) {
      this.url = url;
      this.task_id = task_id;
      this.file_name = file_name;
      this.onMessageCallback = onMessageCallback;
      this.ws = null;
      this.connect();
  }

  connect() {
      this.ws = new WebSocket(`${this.url}/${this.task_id}`);
      this.ws.onopen = () => {
          console.log(`WebSocket ${this.task_id} ${this.file_name} connection opened`);
      };
      this.ws.onmessage = (event) => {
        //   console.log('event:', event);
          const message = event.data;
          this.onMessageCallback(message);
      };
      this.ws.onclose = (event) => {
          console.log(`WebSocket ${this.task_id} ${this.file_name} connection closed`);
          console.log('关闭代码:', event.code);
          console.log('关闭原因:', event.reason);
          setTimeout(() => {
              console.log(`Reconnecting WebSocket...${this.task_id} ${this.file_name}`);
              this.connect();
          }, 1000); // 1秒后重新连接
      };
      this.ws.onerror = (event) => {
          console.error('WebSocket error:', event);
      };
  }

  close() {
      if (this.ws) {
          this.ws.close();
      }
  }
}