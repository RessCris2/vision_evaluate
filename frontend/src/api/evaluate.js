import axios from '../axios';
import axiosTestInstance from '../axios';


export const fetchData = (conf, iou_thres, phrase_target, filename) => {
    const formData = new FormData();
    const res = axiosTestInstance({
        method: 'get',
        url: '/evaluate',
        params: {
            conf: conf,
            iou_thres: iou_thres,
            phrase_target: phrase_target,
            filename: filename
        },
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return res;
}

// export const fetchDataBatch = async (params) => {
//   try {
//     const res = await axiosTestInstance({
//       method: 'get',
//       url: '/evaluate/batch',
//       params,
//       paramsSerializer: (params) => {
//         return Object.keys(params)
//           .map((key) =>
//             [].concat(params[key])
//               .map((item) => `${key}=${encodeURIComponent(item)}`)
//               .join('&')
//           )
//           .join('&');
//       },
//       headers: { 'Content-Type': 'multipart/form-data' }
//     });

//     // 检查业务逻辑错误
//     if (res.data?.error) {
//       throw new Error(res.data.error);
//     }

//     return res.data;
//   } catch (error) {
//     // 分类处理错误
//     let errorMessage = '请求失败';
//     if (error.response) {
//       errorMessage = error.response.data?.message || `服务器错误: ${error.response.status}`;
//     } else if (error.request) {
//       errorMessage = '网络无响应';
//     }

//     console.error('fetchDataBatch 错误:', errorMessage, error);
//     throw new Error(errorMessage);
//   }
// };


export const fetchDataBatch = (conf, iou_thres, phrase_target, file_key, filelist, label_name) => {
  // const formData = new FormData();
  try{
        const res = axiosTestInstance({
            method: 'get',
            url: '/evaluate/batch',
            params: {
                conf: conf,
                iou_thres: iou_thres,
                phrase_target: phrase_target,
                file_key: file_key,
                filelist: filelist,
                label_name: label_name
            },
            paramsSerializer: (params) => {
              // 自定义序列化，确保参数格式为 filelist=item1&filelist=item2
              return Object.keys(params)
                  .map((key) =>
                  [].concat(params[key]).map((item) => `${key}=${encodeURIComponent(item)}`).join('&')
                  )
                  .join('&');
              },
          // responseType: 'blob', // 确保返回二进制数据
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return res;
      }catch (error) {
    // 分类处理错误
    let errorMessage = '请求失败';
    if (error.response) {
      // 服务器返回了 4xx/5xx 错误
      errorMessage = error.response.data?.message || `服务器错误: ${error.response.status}`;
    } else if (error.request) {
      // 请求已发送但无响应（如网络断开）
      errorMessage = '网络无响应';
    } else {
      // 其他错误（如代码配置问题）
      errorMessage = error.message || '未知错误';
    }

    console.error('fetchDataBatch 错误:', errorMessage, error);
    throw new Error(errorMessage); // 抛出统一错误
  }
};


/**
 * 
 * @param response 请求评估接口后返回的对象
 * 包括 keys: [
    "matches",
    "ious",
    "gt_shapes",
    "pred_shapes",
    "pred_points",
    "gt_points",
    "gt_cls",
    "pred_cls",
    "gt_cls2",
    "pred_cls2",
    "cm",
    "p",
    "r",
    "mean_results",
    "ap"
]
  @returns 返回一个对象，转换和计算需要的 evalState 的 keys  
 */
  export  function convertResult(response){
    const jsonPred = response.pred_shapes;
    const jsonTrue = response.gt_shapes;
  
    const predIds =[...Array(jsonPred.shapes.length).keys()];
    const trueIds = [...Array(jsonTrue.shapes.length).keys()];
  
    const mathedPairs = response.matches;
    // console.log('mathedPairs:', mathedPairs);
    const match_pred = new Set(mathedPairs.map(pair => pair[1]));
    // console.log('mathedPairs:', mathedPairs);
    const match_true = new Set(mathedPairs.map(pair => pair[0]));
  
    const matchedPredIds = Array.from(match_pred);
    const matchedTrueIds = Array.from(match_true);
  
    const unmatchedPredIds = predIds.filter(predId => !match_pred.has(predId));
    const unmatchedTrueIds = trueIds.filter(trueId => !match_true.has(trueId));
  
    return {
      jsonPred,
      jsonTrue,
      predIds,
      trueIds,
      matchedPredIds,
      matchedTrueIds,
      unmatchedPredIds,
      unmatchedTrueIds,
      mathedPairs,
    }
  
  }