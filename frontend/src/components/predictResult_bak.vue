
<template>
    <div>
        <h1>预测结果批量评估</h1>
    </div>

    <!-- 图片上传 -->
    <div class='chooseimg'>
        <el-cascader v-model="target_options" :options="options" :props="props" />

        <!-- list-type="picture-card" -->
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
            >
              <!-- :on-change="handleImageUpload" -->
            <!-- <template #trigger> -->
            <el-button size="small" type="primary">1、选择需要预测的图片和相应标注json文件(小于30张图片)</el-button>
            <!-- </template> -->
        </el-upload>
    <div>
        共选择了 {{ imageNames.length }} 张图片
        一共  {{ fileList.length }} 个文件（图片+标注文件）
    </div>

        
    <!-- <div>
        <el-button size="small" type="success" @click="logFileNames">查看选择的文件名</el-button>
        </div> -->
        

        <div style="display: flex; gap: 10px;">
            <div>
            <el-button size="small" type="success" @click="submitUploadBatch">预测</el-button>
            </div>
            <div v-if="predictCompleted">
                <el-button size="small" type="warning">预测完成！耗时 {{takeTime}}s</el-button>
            </div>
            <div v-if="predictState">
                <el-button size="small" type="warning">预测中</el-button>
            </div>
        </div>

        <div style="display: flex; gap: 10px;">
            <div>
            <el-button size="small" type="success" @click="submitOptonUpload">预测（欧波同测试用）</el-button>
            </div>
            <div v-if="predictOptonCompleted">
                <el-button size="small" type="warning">预测完成！耗时 {{takeTime}}s</el-button>
            </div>
            <div v-if="predictOptonState">
                <el-button size="small" type="warning">预测中</el-button>
            </div>
        </div>
        
         <!--  <div>
            <el-button size="small" type="success" @click="submitSemVisionUpload">预测（一体化测试用）</el-button>
        </div> -->
    </div>

</template>

<script setup lang="ts">
import { options } from './option'
import { ref, reactive, onMounted } from 'vue'
import type { UploadProps, UploadUserFile } from 'element-plus'
import { fetchPredictBatch, fetchPredict, fetchOptonPredict, fetchSemVisionPredict, fetchUpload, fetchUploadBatch } from '../api/predict'
import { usePredictStore, PredictResult, PredictResultDict } from '../stores/predictStore'
import { useCommonStore } from '../stores/commonStore'
import { storeToRefs } from 'pinia'

// const PredictResultDict = reactive({});
const predictStore = usePredictStore();
const commonStore = useCommonStore();
const {
        phraseTarget,
        modelCategory,
        imageNames,
        specificImageName,
        iouThreshold,
    } = storeToRefs(commonStore)

const target_options = ref([]);
const upload = ref(null); // 定义 ref 用于绑定 <el-upload> 组件.
const fileList = ref([]); // 定义 ref 用于绑定 <el-upload> 组件.

const predictCompleted = ref(false);

const props = {
  expandTrigger: 'hover',
}
const takeTime = ref(0);
const predictState = ref(false);
const predictOptonState = ref(false);
const predictOptonCompleted = ref(false);

const handleChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles;
//   commonStore.phraseTarget = target_options.value[0];
//   commonStore.modelCategory = target_options.value[1];
//   commonStore.imageNames = fileList.value.filter(file => !file.name.endsWith('.json')).map(file => file.name);
  phraseTarget.value = target_options.value[0];
  modelCategory.value = target_options.value[1];
  imageNames.value = fileList.value.filter(file => !file.name.endsWith('.json')).map(file => file.name);

}

const logFileNames = () => {
   const fileNames = fileList.value;
  console.log('选择的文件:', fileNames);
}


const submitUploadBatch = async () => {
    // const PredictResultDictTemp: Record<string, PredictResult> = {};
    console.log(fileList.value)
    const startTime = Date.now();
    predictCompleted.value = false;
    predictState.value = true;
    

    
    fileList.value.forEach(file => 
                    {
                        fetchUploadBatch(file.raw)
                        console.log('file', file);

                    });  // 全部上传

    
    const predict_result = await fetchPredictBatch(commonStore.phraseTarget, commonStore.modelCategory, commonStore.imageNames);
    // predictStore.predictResultDict = predict_result.data;

    for (const [file, data] of Object.entries(predict_result.data)) {
        predictStore.predictResultDict[file] = {
            imageName: data.image,
            initialWidth: data.width,
            initialHeight: data.height,
            image: data.image,
            predictType: data.result_type,
            predictMask: data.predict
        };
    }

    console.log('predictResultDict', predictStore.predictResultDict);
    const endTime = Date.now();
    takeTime.value = (endTime - startTime) / 1000;
    // console.log(`Total time for promises execution: ${takeTime} ms`);
    console.log('PredictResultDict new', predictStore.predictResultDict);
    predictState.value = false;
    predictCompleted.value = true;
}

// 提交预测
// const submitOptonUpload = (files, fileList) => {
//     const response = fetchOptonPredict(value.value[0], value.value[1], imageOriginal.value);
    
//     response.then((response) => {
//         console.log('请求 infer 成功:');        
//         predictionResult.value = response.predict; 
//         const img = new Image();
//         img.src = predictionResult.value;
//         img.onload = () => {
//             const ctx = canvas.value.getContext('2d');
//             ctx.drawImage(img, 0, 0, canvas.value.width, canvas.value.height);
//         };
//         predictionLoaded.value = true;       
//         console.log('response_infer', response.predict_png);
//     });

// }


// 提交预测
const submitOptonUpload = async () => {
    // const PredictResultDictTemp: Record<string, PredictResult> = {};
    console.log(fileList.value)
    const startTime = Date.now();
    predictOptonCompleted.value = false;
    predictOptonState.value = true;
    
    // 使用 Promise.all() 来等待所有的异步请求完成
    const promises = fileList.value.map(file => {
        return new Promise<void>((resolve) => {
            if (file.name.endsWith('.json')) {
                console.log('file', file);
                // fetchUpload(file.raw);  // 如果是 .json 文件，直接上传，不处理预测结果
                fetchUploadBatch(file.raw);  // 如果不是 .json 文件，也上传
                resolve();  // 立即完成该文件的处理
            } else {
                console.log('file', file);
                fetchUploadBatch(file.raw);  // 如果不是 .json 文件，也上传
                const response = fetchOptonPredict(target_options.value[0], target_options.value[1], file);

                response.then((response) => {
                    console.log('请求 infer 成功: file', file.name);

                    const predictResultTemp: PredictResult = {
                        imageName: file.name,
                        // image: file.raw,
                        predictMask: undefined,
                        predictType: 'mask',
                        initialWidth: 0,
                        initialHeight: 0,
                        image: undefined
                    };

                    predictResultTemp['predictMask'] = response.data.predict;
                    predictResultTemp['predictType'] = response.data.result_type;
                    predictResultTemp['initialWidth'] = response.data.width;
                    predictResultTemp['initialHeight'] = response.data.height;
                    predictResultTemp['image'] = response.data.image;

                    // 将当前文件的结果添加到临时字典中
                    // PredictResultDictTemp[file.name] = predictResultTemp;
                    predictStore.predictResultDict[file.name] = predictResultTemp;

                    // 处理完成，调用 resolve()
                    resolve();
                }).catch((error) => {
                    console.error('预测请求失败', error);
                    resolve();  // 即使请求失败，也要调用 resolve()
                });
            }
        });
    });
    // 等待所有异步操作完成
    await Promise.all(promises);

    console.log('PredictResultDict new', predictStore.predictResultDict);
    predictOptonState.value = false;
    predictOptonCompleted.value = true;
    const endTime = Date.now();
    
    takeTime.value = (endTime - startTime) / 1000;
}
//     console.log('PredictResultDict new', predictStore.predictResultDict);
// }

// 提交预测
const submitUpload = async () => {
    // const PredictResultDictTemp: Record<string, PredictResult> = {};
    console.log(fileList.value)
    predictCompleted.value = false;
    
    // 使用 Promise.all() 来等待所有的异步请求完成
    const promises = fileList.value.map(file => {
        return new Promise<void>((resolve) => {
            if (file.name.endsWith('.json')) {
                console.log('file', file);
                fetchUploadBatch(file.raw);  // 如果是 .json 文件，直接上传，不处理预测结果
                resolve();  // 立即完成该文件的处理
            } else {
                fetchUploadBatch(file.raw);  // 如果不是 .json 文件，也上传
                console.log('file', file);
                const response = fetchPredict(target_options.value[0], target_options.value[1], file);

                response.then((response) => {
                    console.log('请求 infer 成功: file', file.name);

                    const predictResultTemp: PredictResult = {
                        imageName: file.name,
                        // image: file.raw,
                        predictMask: undefined,
                        predictType: 'mask',
                        initialWidth: 0,
                        initialHeight: 0,
                        image: undefined
                    };

                    predictResultTemp['predictMask'] = response.data.predict;
                    predictResultTemp['predictType'] = response.data.result_type;
                    predictResultTemp['initialWidth'] = response.data.width;
                    predictResultTemp['initialHeight'] = response.data.height;
                    predictResultTemp['image'] = response.data.image;

                    // 将当前文件的结果添加到临时字典中
                    // PredictResultDictTemp[file.name] = predictResultTemp;
                    predictStore.predictResultDict[file.name] = predictResultTemp;

                    // 处理完成，调用 resolve()
                    resolve();
                }).catch((error) => {
                    console.error('预测请求失败', error);
                    resolve();  // 即使请求失败，也要调用 resolve()
                });
            }
        });
    });

    // 等待所有异步操作完成
    await Promise.all(promises);

    console.log('PredictResultDict new', predictStore.predictResultDict);
    predictCompleted.value = true;
}
//     console.log('PredictResultDict new', predictStore.predictResultDict);
// }


onMounted(() => {
    console.log('mounted');
    commonStore.phraseTarget = target_options.value[0];
    commonStore.modelCategory = target_options.value[1];
    commonStore.imageNames = fileList.value.filter(file => !file.name.endsWith('.json')).map(file => file.name);
});

// // 提交预测
// const submitUpload_v0 = (files, fileList) => {
//     const response = fetchPredict(target_options.value[0], target_options.value[1], imageOriginal.value);
    
//     response.then((response) => {
//         console.log('请求 infer 成功:');
//         // 存储到 Pinia store 中

        
//         predictionResult.value = response.predict; 
//         const img = new Image();
//         img.src = predictionResult.value;
//         img.onload = () => {
//             const ctx = canvas.value.getContext('2d');
//             ctx.drawImage(img, 0, 0, canvas.value.width, canvas.value.height);
//         };
//         predictionLoaded.value = true;       
//         console.log('response_infer', response.predict_png);
//     });
// }


// 提交预测
// const submitUpload2 = (file, fileList) => {
//     // fileUplodList.value.push(file); // 会太敏感了吗？而且删除的时候也要处理吗？
    
//     // console.log(" before upload", file.name);
//     // console.log('document.getElementsByClassName("el-upload__input")[0].value', document.getElementsByClassName("el-upload__input")[0].value);
//     // const relatedJsonFileName = file.name.replace(/\.[^.]+$/, ".json");

//     // const relatedJsonFilePath = `${file.webkitRelativePath.replace(file.name,"")}${relatedJsonFileName}`;
//     // const relatedJsonFile = Array.from(upload.value.uploadFiles).find(
//     // (f) => f.raw.webkitRelativePath === relatedJsonFilePath
//     // );

//     // if (relatedJsonFile) {
//     // console.log(`找到关联的 JSON 文件: ${relatedJsonFileName}`);
//     // } else {
//     // console.warn(`未找到关联的 JSON 文件: ${relatedJsonFileName}`);
//     // }

    
//     fileUplodList.value = fileList;


//     fileList.forEach(file => {
//         if (file.name.endsWith('.json')) {
//             console.log('file', file);
//             fetchUpload(file.raw);
//             return;
//         }
//         else{
//         console.log('file', file);
//         const response = fetchPredict2(target_options.value[0], target_options.value[1], file);
        
//         response.then((response) => {
//             console.log('请求 infer 成功: file', file.name);
//             console.log('response', response.predict);
//             PredictResultDict[file.name] = response.data.predict; // Adjust this based on the actual structure of the response
//             console.log('PredictResultDict', PredictResultDict);
//         });
//     }
//     });
    
// }


// // 提交预测
// const submitOptonUpload = (files, fileList) => {
//     const response = fetchOptonPredict(target_options.value[0], target_options.value[1], imageOriginal.value);
    
//     response.then((response) => {
//         console.log('请求 infer 成功:');        
//         predictionResult.value = response.predict; 
//         const img = new Image();
//         img.src = predictionResult.value;
//         img.onload = () => {
//             const ctx = canvas.value.getContext('2d');
//             ctx.drawImage(img, 0, 0, canvas.value.width, canvas.value.height);
//         };
//         predictionLoaded.value = true;       
//         console.log('response_infer', response.predict_png);
//     });

// }


// // 提交预测
// const submitSemVisionUpload = (files, fileList) => {
//     const response = fetchSemVisionPredict(target_options.value[0], target_options.value[1], imageOriginal.value);
    
//     response.then((response) => {
//         console.log('请求 infer 成功:');        
//         predictionResult.value = response.predict; 
//         const img = new Image();
//         img.src = predictionResult.value;
//         img.onload = () => {
//             const ctx = canvas.value.getContext('2d');
//             ctx.drawImage(img, 0, 0, canvas.value.width, canvas.value.height);
//         };
//         predictionLoaded.value = true;       
//         console.log('response_infer', response.predict_png);
//     });

// }

// 是否预览图片？ :on-preview="handlePreview"
// const handlePreview = async file => {
//     console.log("选定图片：", file);
//     const reader = new FileReader();
//     reader.onload = e => {
//         imgSrc.value = e.target.result;
//     };
//     reader.readAsDataURL(file.raw);
// }


// const handleExceed = (files, fileList) => {
// // 清空当前选择，重新选择
// //
// // 限制选择 1 个文件
// upload.value.clearFiles();
// const file = files[0];
// file.uid = genFileId();
// upload.value.handleStart(file);

// // console.log('handleExceed', files, fileList);
// // this.$message.warning(`当前限制选择 1 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
// }

// :on-change="submitUpload2"

</script>