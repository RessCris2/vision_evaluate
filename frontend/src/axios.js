import axios from 'axios'

const apiUrl = import.meta.env.VITE_API_URL
const apiPrefix = import.meta.env.VITE_API_PREFIX

// 创建一个默认的 Axios 实例
const axiosInstance = axios.create({
  baseURL: `${apiUrl}${apiPrefix}`, // 从环境变量获取 API 基础路径并加上前缀
  timeout: 600000,
});

// const axiosOptonInstance = axios.create({
//   baseURL: `${import.meta.env.VITE_API_OPTON_URL}${apiPrefix}`, // 从环境变量获取 API 基础路径
//   timeout: 600000,
// });

// export {axiosOptonInstance};
export default axiosInstance;

