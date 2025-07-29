
import  axiosInstance  from '../axios';

export const fetchPredictBatch =  (phrase_target, model_category, filelist) => {
    console.log('filelist:', filelist);
    const res = axiosInstance({
        method: 'get',
        url: '/infer_batch_file',
        params: {
            phrase_target: phrase_target,
            model_category: model_category,
            filelist: filelist
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
}

// 预测
export const fetchPredict =  (phrase_target, model_category, file) => {
    const formData = new FormData();
    formData.append('phrase_target', phrase_target);
    formData.append('model_category', model_category);
    formData.append('file', file.raw);
    const res =  axiosInstance({
        method: 'post',
        url: '/infer',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return res;
}


// export const fetchSemVisionPredict =  (phrase_target, model_category, file) => {
//     const formData = new FormData();
//     formData.append('phrase_target', phrase_target);
//     formData.append('model_category', model_category);
//     formData.append('file', file.raw);
//     const res =  axios({
//         // baseURL: "http://10.110.10.131:7002",
//         method: 'post',
//         url: 'http://10.110.10.131:6002/infer',
//         data: formData,
//         headers: {
//             'Content-Type': 'multipart/form-data'
//         }
//     });
//     return res;
// }


