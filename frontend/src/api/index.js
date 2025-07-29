
import axios from '../axios';
// import {base64ToBlob}  from '@/utils/utils';


// 上传文件
export const fetchUpload = async (labelme_file ) => {
    const formData = new FormData();
    // const blob =  base64ToBlob(predict);
    // const fileName = 'predict_mask.png';

    // 将文件对象和 Base64 数据添加到 FormData 中
    // formData.append('pred_mask', blob, fileName);  // 这里假设 file.raw 是一个 File 对象
    formData.append('labelme_json', labelme_file);  // 这里假设 predictImage.value 是你需要上传的另一部分数据
    // 通过 axios 或其他方式发送请求
    axios.post('/upload_file', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })
    .then(response => {
        console.log('response:', response);
        
        console.log('文件上传成功！', response);
    })
    .catch(error => {
        console.error('文件上传失败:', error);
    });
}

// 预测
export const fetchPredict =  (phrase_target, model_category, file) => {
    const formData = new FormData();
    formData.append('phrase_target', phrase_target);
    formData.append('model_category', model_category);
    formData.append('file', file.raw);
    const res =  axios({
        method: 'post',
        url: '/infer',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return res;
}


export const fetchOptonPredict =  (phrase_target, model_category, file) => {
    const formData = new FormData();
    formData.append('phrase_target', phrase_target);
    formData.append('model_category', model_category);
    formData.append('file', file.raw);
    const res =  axios({
        // baseURL: "http://10.110.10.131:7002",
        method: 'post',
        url: 'http://10.110.10.131:7002/opton_infer',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return res;
}



export const fetchSemVisionPredict =  (phrase_target, model_category, file) => {
    const formData = new FormData();
    formData.append('phrase_target', phrase_target);
    formData.append('model_category', model_category);
    formData.append('file', file.raw);
    const res =  axios({
        // baseURL: "http://10.110.10.131:7002",
        method: 'post',
        url: 'http://10.110.10.131:6002/infer',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return res;
}


// 评估
// 建立在预测结果和标注json文件已经上传的基础上
export const fetchData = async (conf, iou_thres, phrase_target, fileName) => {
    console.log('请求评估接口:', fileName);
    const response = await axios({
        method: 'get',
        url: '/evaluate',
        params: {
            conf: conf,
            iou_thres: iou_thres,
            phrase_target: phrase_target,
            filename: fileName
        }
    });
    // console.log('请求成功, matches 值为:', response.matches);
    return response;
}


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