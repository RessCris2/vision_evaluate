import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
// import ECharts from 'vue-echarts'
// import * as echarts from 'echarts'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import { createPersistedState } from 'pinia-plugin-persistedstate'

// import axios from 'axios'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()
// pinia.use(
//     createPersistedState({
//       // 所有 Store 都开启持久化存储
//       auto: true
//     })
//   )
// pinia.use(createPersistedState())
pinia.use(piniaPluginPersistedstate)
app.use(pinia)

// app.use(createPinia())
app.use(router)
app.use(ElementPlus)
// app.component('v-chart', ECharts)
// 全局挂载 echarts
// app.config.globalProperties.$echarts = ECharts

// app.use(axios)

app.mount('#app')
