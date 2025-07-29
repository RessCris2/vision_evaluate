import { defineStore } from "pinia";
import { ref } from 'vue';
// import piniaPersist from 'pinia-plugin-persistedstate';

export const useCommonStore = defineStore('commonVar', () => {

    // const phraseTarget = ref('secondary_particle');
    // const modelCategory = ref('big');
    const phraseTarget = ref('');
    const modelCategory = ref('');
    const predictType = ref('common');
    const imageNames = ref<string[]>([]);
    const iouThreshold = ref(0.45);
    const specificImageName = ref('');
    const selectedImage = ref('');
    const selectedCate = ref('');
    const file_key = ref('');

    
    // 导出状态和操作
    return {
        phraseTarget,
        modelCategory,
        predictType,
        imageNames,
        specificImageName,
        iouThreshold,
        selectedImage,
        selectedCate,
        file_key,
    }
},{
    persist: {
      // CONFIG OPTIONS HERE
    }
})