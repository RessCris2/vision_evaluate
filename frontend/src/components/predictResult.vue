
<template>
    <div>
        <h1>预测结果批量评估</h1>
    </div>

    <!-- 图片上传 -->
    <div class='chooseimg'>
        <el-cascader v-model="target_options" :options="options_ch" :props="props" />

        <el-upload
            ref="upload"
            class = 'upload-pic'
            :file-list = "fileList"
            multiple
            :limit = '60'
            :drag = 'true'
            :auto-upload="false"
            :thumbnail-mode="true"
            :on-change="handleChange"
            style="width: 400px"
            >
              <!-- :on-change="handleImageUpload" -->
            <!-- <template #trigger> -->
            <el-button size="small" type="primary" >1、选择需要预测的图片和相应标注json文件(小于30张图片)</el-button>
            
            <!-- </template> -->
        </el-upload>
        <!-- <el-button size="small" type="success"  @click="uploadOrigianlImageAndJson">上传</el-button> -->

        <el-button 
                    :loading="isUploading1" 
                    :disabled="isUploadDisabled1" 
                    size="small" 
                    type='success' 
                    @click="uploadOrigianlImageAndJson">
                    {{ uploadButtonText1 }}
                    </el-button>

    <div>
        共选择了 {{ imageNames.length }} 张图片
        一共  {{ fileList.length }} 个文件（图片+标注文件）
    </div>
        
        <div style="display: flex; gap: 10px;">
            <!-- <div>
            <el-button size="small" type="success" @click="submitUploadBatch">预测</el-button>
            </div> -->
            <div>

            <!-- <el-form-item label="选择预测选项">
                <el-cascader v-model="predict_option" :options="predict_options" :props="props" />
            </el-form-item> -->
            <el-button size="small" type="primary" @click="submitUploadBatchAndQueue">AI计算平台预测</el-button>

            <el-button
                size="small"
                @click="showUpload = !showUpload"
                type="primary"
            >
                上传预测结果文件(json)
            </el-button>
            <el-upload v-if="showUpload"
                ref="resultUpload"
                class="upload-pic"
                :file-list="resultFileList"
                multiple
                :limit="60"
                :drag="true"
                :auto-upload="false"
                :on-change="handleTestChange"
            >
                <el-button size="small" >上传预测结果文件 labelme json 格式</el-button>
                
            </el-upload>
            <!-- <el-button  v-if="showUpload" size="small" type='success' @click="uploadPredictResultJson">上传</el-button> -->
            <el-button 
                    v-if="showUpload" 
                    :loading="isUploading" 
                    :disabled="isUploadDisabled" 
                    size="small" 
                    type='success' 
                    @click="uploadPredictResultJson">
                    {{ uploadButtonText }}
                    </el-button>
            <div>
                <div v-if="predictCompleted">
                    <el-button size="small" type="warning">预测完成！耗时 {{takeTime}}s</el-button>
                </div>
                <div v-else-if="predictCompleted === false">
                    <el-button size="small" type="warning">预测中</el-button>
                </div>
                <div v-else>
                </div>
            </div>    
        </div>
            
            
        </div>
       
    <div v-if="unmatchedImages.length > 0">
        <strong style="color: red;">未预测成功的图片: {{ unmatchedImages }} 共 {{ unmatchedImages.length }}张</strong>
    </div>

    </div>

</template>

<script setup lang="ts">
import { options_ch, predict_options } from './option'
import { ref, reactive, onMounted, watch } from 'vue'
import type { UploadProps, UploadUserFile } from 'element-plus'
// import { fetchPredictBatch, fetchPredict, fetchOptonPredict, fetchSemVisionPredict} from '../api/predict'
// import WebSocketManager from '../api/ws'
import { fetchUploadBatchQueue, fetchUpload, fetchUploadResult, fetchUploadImageAndJson } from '../api/upload'
import { usePredictStore, PredictResult, PredictResultDict } from '../stores/predictStore'
import { useCommonStore } from '../stores/commonStore'
import { storeToRefs } from 'pinia'
import { setCanvasCreator } from 'echarts/core'

// const PredictResultDict = reactive({});
const feedback_message = ref('');
const webSocketsConn = []; // 用于存储所有的 WebSocket 连接
const predictStore = usePredictStore();
const commonStore = useCommonStore();
const {
        phraseTarget,
        modelCategory,
        predictType,
        imageNames,
        specificImageName,
        iouThreshold,
        file_key
    } = storeToRefs(commonStore)

const target_options = ref([]);
const upload = ref(null); // 定义 ref 用于绑定 <el-upload> 组件.
const fileList = ref([]); // 定义 ref 用于绑定 <el-upload> 组件.
const predict_option = ref([]);
const unmatchedImages = ref([]);
const resultUpload = ref(null);
const resultFileList = ref([]);
const showUpload = ref(false);
// const department = ref(''); # 但是暂时其实没用上，后续等semvision也上了部门再加上。

watch(target_options, (newVal) => {
    phraseTarget.value = newVal[0];
    // department.value = newVal[1];
    modelCategory.value = newVal[2];
});

watch(predict_option, (newVal) => {
    predictType.value = newVal[0];
});

const predictCompleted = ref(undefined);
const props = {
  expandTrigger: 'hover',
}
const takeTime = ref(0);
const predictState = ref(false);
const predictOptonState = ref(false);
const predictOptonCompleted = ref(false);

const handleChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles;
  imageNames.value = fileList.value.filter(file => !file.name.endsWith('.json')).map(file => file.name);
}

const handleTestChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  resultFileList.value = uploadFiles;
}

const isUploading1 = ref(false);
// isUploading.value = true;
const uploadButtonText1 = ref('上传');
const isUploadDisabled1 = ref(false);

const uploadOrigianlImageAndJson = async () => {
    if (fileList.value.length === 0) {
        console.error('请先选择文件');
        return;
    }
    
    try {
         // 上传开始，设置按钮状态
        isUploading1.value = true;
        isUploadDisabled1.value = true;
        uploadButtonText1.value = '上传中...';
        const promises = fileList.value.map(async (file) => {
            const response = await fetchUploadImageAndJson(file.raw);
            console.log('上传结果:', response);
        });
        
        await Promise.all(promises);
        uploadButtonText1.value = '上传成功';

        setTimeout(() => {
            isUploading1.value = false;
            isUploadDisabled1.value = false;
            uploadButtonText1.value = '上传';
        }, 3000);
        console.log('原始图片和json文件上传成功');
    } catch (error) {
        console.error('原始图片和json文件上传失败:', error);
        isUploading1.value = false;
        isUploadDisabled1.value = false;
        uploadButtonText1.value = '上传失败，重试';
    }
}

// 添加按钮状态变量
const isUploading = ref(false);
// isUploading.value = true;
const uploadButtonText = ref('上传');
const isUploadDisabled = ref(false);
const uploadPredictResultJson = async () => {
    if (resultFileList.value.length === 0) {
        console.error('请先选择文件');
        return;
    }

    try {
         // 上传开始，设置按钮状态
        isUploading.value = true;
        isUploadDisabled.value = true;
        uploadButtonText.value = '上传中...';

        const promises = resultFileList.value.map(async (file) => {
            const predict_result = await  fetchUploadResult(file.raw);
            const filename = predict_result['filename'];
            predictStore.predictResultDict[filename] = {
                imageName: predict_result.image,
                initialWidth: predict_result.width,
                initialHeight: predict_result.height,
                image: predict_result.image,
                predictType: predict_result.result_type,
                predictMask: predict_result.predict
            };

        });
        
        await Promise.all(promises);
        // console.log('预测结果文件json上传成功');
        // 上传成功，恢复按钮状态
        uploadButtonText.value = '上传成功';

        setTimeout(() => {
            isUploading.value = false;
            isUploadDisabled.value = false;
            uploadButtonText.value = '上传';
        }, 3000);
    } catch (error) {
        console.error('预测结果文件json上传失败:', error);
         // 上传失败，设置按钮状态
        isUploading.value = false;
        isUploadDisabled.value = false;
        uploadButtonText.value = '上传失败，重试';
    }
}

const logFileNames = () => {
   const fileNames = fileList.value;
  console.log('选择的文件:', fileNames);
}

// 提交预测
const submitUploadBatchAndQueue = async () => {
    // Add your implementation for submitUploadBatchAndWs here

    const startTime = Date.now();
    predictCompleted.value = false;
    predictState.value = true;

    // 提取出 json 文件
    const json_files = fileList.value.filter(file => file.name.endsWith('.json'));
    json_files.forEach(file => 
                    {
                        fetchUpload(file.raw)
                        console.log('file', file);
                    });  // 全部上传
    
    // 剩下的非json文件
    const img_files = fileList.value.filter(file => !file.name.endsWith('.json'));
                
    // 如果 img_files 和 json_files 长度不等，报错
    if (img_files.length !== json_files.length) {
        console.error('img_files 和 json_files 长度不等');
        return;
    }

    // 定义一个局部变量
    const count = ref(img_files.length);
    console.log('一共需要预测图片数:', count.value);
    
    const onMessageReceived = (message) => {
        const predict_result = JSON.parse(JSON.parse(message));
        // console.log("receivedData", receivedData); 

        const filename = predict_result['filename'];
        predictStore.predictResultDict[filename] = {
                imageName: predict_result.image,
                initialWidth: predict_result.width,
                initialHeight: predict_result.height,
                image: predict_result.image,
                predictType: predict_result.result_type,
                predictMask: predict_result.predict
            };
    
        count.value -= 1;
        // console.log('count 减去1:', count.value);
        if (count.value === 0) {
            console.log('All files predicted!');
            predictCompleted.value = true;
            const endTime = Date.now();
            takeTime.value = (endTime - startTime) / 1000;

            const requestedSet = new Set(img_files.map(file => file.name));
            const returnedSet = new Set(Object.keys(predictStore.predictResultDict));
            unmatchedImages.value = [...requestedSet].filter(image => !returnedSet.has(image));
        }
    };
    
    const promises = img_files.map(file => {
        const task_id = modelCategory.value + phraseTarget.value +file.name+new Date().getTime().toString(36) //#endregion+ '-' + Math.random().toString(36).substr(2);
        console.log(task_id);
        return fetchUploadBatchQueue(file, task_id, commonStore.phraseTarget, 
                    commonStore.modelCategory, commonStore.predictType, onMessageReceived);
    });

    await Promise.all(promises);
    console.log('All files uploaded and WebSocket connections established');

    };  


onMounted(() => {
    console.log('mounted');
    commonStore.phraseTarget = target_options.value[0];
    commonStore.modelCategory = target_options.value[1];
    commonStore.imageNames = fileList.value.filter(file => !file.name.endsWith('.json')).map(file => file.name);
});


</script>

<style scoped>
.active-button {
    font-weight: bold;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
}
</style>