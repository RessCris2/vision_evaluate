import { defineStore } from "pinia";
import { ref, reactive } from "vue";

export const usePredictStore = defineStore('predictResultDict', () => {
    // const predictResultDict = ref<PredictResultDict>(); // 还是放 image name 作为 key, 重复多地方放。。
    const predictResultDict = reactive<Record<string, PredictResult>>({});

    // 导出状态和操作
    return {
        predictResultDict,
    };
    
})


export interface PredictResult {
    imageName: string;
    initialWidth: number,
    initialHeight: number,
    // image: Blob; // raw 文件数据
    image: string; // base64 编码的图片
    predictType: 'mask' | 'json';
    predictMask?: string; // base64 编码的 mask 图片类型是 string
}

export interface PredictResultDict {
    [imageName: string]: PredictResult;
}