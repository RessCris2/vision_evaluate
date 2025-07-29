
import  axiosInstance  from '../axios';
import { WebSocketManager } from './ws';

// 上传labelme 标注文件
export const fetchUpload = async (labelme_file ) => {
    const formData = new FormData();
    formData.append('labelme_json', labelme_file);  // 这里假设 predictImage.value 是你需要上传的另一部分数据
    // 通过 axios 或其他方式发送请求
    axiosInstance.post('/upload/labelme_json', formData, {
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


export const fetchUploadImageAndJson = async (file) => {
    const formData = new FormData();
    formData.append('file', file);  // 假设 file 是一个 File 对象
    try {
        const response = await axiosInstance.post('/upload/original_image_and_json', formData,
            {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
        console.log('文件上传成功！', response.data);
        return response.data; // 返回服务器响应的数据
    } catch (error) {
        console.error('文件上传失败:', error);
        throw error; // 抛出错误，让外部 catch 捕获
    }
};

export const fetchUploadResult = async (result_labelme_json) => {
    const formData = new FormData();
    formData.append('result_labelme_json', result_labelme_json);

    try {
        const response = await axiosInstance.post('/upload/result_labelme_json', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        console.log('文件上传成功！', response.data);
        return response.data; // 直接返回数据
    } catch (error) {
        console.error('文件上传失败:', error);
        throw error; // 抛出错误，让外部 catch 捕获
    }
};

// 上传文件
export const fetchUploadBatch = async (file ) => {
    const formData = new FormData();
    // const blob =  base64ToBlob(predict);
    // const fileName = 'predict_mask.png';

    // 将文件对象和 Base64 数据添加到 FormData 中
    // formData.append('pred_mask', blob, fileName);  // 这里假设 file.raw 是一个 File 对象
    formData.append('file', file);  // 这里假设 predictImage.value 是你需要上传的另一部分数据
    // 通过 axios 或其他方式发送请求
    axiosInstance.post('/upload_all_file', formData, {
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

// 上传图片文件
// 上传文件
export const fetchUploadBatchQueue = async (file, task_id, phrase_target, model_category, predict_type,onMessageReceived ) => {
    const formData = new FormData();
    // formData.append('pred_mask', blob, fileName);  // 这里假设 file.raw 是一个 File 对象
    formData.append('file', file.raw);  // 这里假设 predictImage.value 是你需要上传的另一部分数据
    formData.append('phrase_target', phrase_target);
    formData.append('model_category', model_category);
    formData.append('task_id', task_id);
    formData.append('predict_type', predict_type);
    // 通过 axios 或其他方式发送请求
    // console.log('formData:', formData);
    const res =  axiosInstance({
            url: '/upload/queue',
            method: 'post',
            data: formData,
            headers: {
                'Content-Type': 'multipart/form-data',
            },
    })
    .then(response => {
        // console.log('response:', response);
        console.log('图片文件上传成功！', response);
        // const task_id = response.data.task_id;
        const wsManager = new WebSocketManager(`${import.meta.env.VITE_WS_URL}/websocket_conn`, 
                                task_id, file.name, onMessageReceived)
            // feedback_message.value = message;
            // count.value -= 1;
            // console.log('count 减去1:', count.value);
            // if (count.value === 0) {
            //     console.log('All files predicted!');
            // }
        // });
        // webSocketsConn.push(wsManager);
        
    })
    .catch(error => {
        console.error('文件上传失败:', error);
    });
}