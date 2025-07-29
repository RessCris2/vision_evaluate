import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'


const defaultConfig = {
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // outDir: VITE_OUT_DIR,
    sourcemap: true,
    chunkSizeWarningLimit: 1000,
    minify: 'terser', //压缩方式
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
}


// 根据不同环境返回不同配置
export default defineConfig(({ mode }) => {
  // 获取环境变量
  const apiPrefix = process.env.VITE_API_PREFIX || '/eval';
  const baseUrl = process.env.VITE_BASE_URL //|| 'http://10.110.10.131:8002';

  const customConfig = {
    // 设置发布路径
    base: mode === 'prod' ? '/prod/' : mode === 'opton' ? '/opton/' : '/', // 根据环境设置发布路径

    // 设置服务器代理（用于开发环境的 API 转发）
    server: {
      proxy: {
        [apiPrefix]: {
          target: baseUrl, // 根据环境选择请求的前缀
          changeOrigin: true,
          // rewrite: (path) => path.replace(apiPrefix, '/api'),
        },
      },
    },

    //全局变量替换，使用环境变量（前端代码中可以直接使用）/
    define: {
      'process.env': process.env,
    },

    // 其他配置
    build: {
      // 这里设置打包时的发布路径
      outDir: mode === 'prod' ? 'dist/prod' :  mode === 'test' ? 'dist/test' :'dist/dev',
    },
  };
  return { ...defaultConfig, ...customConfig };
});


// // 引入三个环境配置文件
// import ViteBaseConfig from './enviroment/vite.base.config.js'
// import ViteProdConfig from './enviroment/vite.prod.config.js' 
// import ViteDevConfig from './enviroment/vite.dev.config.js'
// import { config } from 'node:process'

// // 策略模式做一个动态的配置
// const envResolver = {
//   "build": () => {
//     console.log("生产环境")
//         // 解构的语法
//         return ({...ViteBaseConfig, ...ViteProdConfig})
//   },
//   "serve":()=>{
//         console.log("开发环境")
//         // 另一种写法
//         return Object.assign({}, ViteBaseConfig, ViteDevConfig)
//     }
// }

// // 根据 参数 command 的值，使用不同的环境配置文件
// export default defineConfig(({command})=>{
//   console.log("command : ",command)
//   // 根据不同的环境使用不同的配置文件,注意这个地方的写法，非常的奇特
//   // 根据命令获取特定的环境配置，如果没有则使用空对象
//   const envConfig = envResolver[command] ? envResolver[command]() : {};
 
//   // 合并默认配置和环境配置
//   return {
//     ...defaultConfig,
//     ...envConfig,
//   };
// });

// export default defineConfig({
//   plugins: [
//     vue(),
//     vueDevTools(),
//   ],
//   resolve: {
//     alias: {
//       '@': fileURLToPath(new URL('./src', import.meta.url))
//     },
//   },
//   build: {
//     // outDir: VITE_OUT_DIR,
//     sourcemap: true,
//     chunkSizeWarningLimit: 1000,
//     minify: 'terser', //压缩方式
//     terserOptions: {
//       compress: {
//         drop_console: true,
//         drop_debugger: true,
//       },
//     },
//   },
// })
