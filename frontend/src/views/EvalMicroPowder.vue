<template>
    <div>
        <h1>预测结果评估</h1>
    </div>

    <!-- 图片上传 -->
    <div class='chooseimg'>
        <el-upload
            ref="upload"
            class = 'upload-pic'
            :limit = "1"
            :auto-upload="false"
            :on-exceed="handleExceed"
            :on-change="handleImageUpload"
            >
            <template #trigger>
                <el-button size="small" type="primary">1、选择需要预测的图片</el-button>
            </template>
        </el-upload>
        
        
        <el-cascader v-model="value" :options="options" :props="props" />
        <div>
            <el-button size="small" type="success" @click="submitUpload">预测</el-button>
        </div>
        <div>
            <el-button size="small" type="success" @click="submitOptonUpload">预测（欧波同测试用）</el-button>
        </div>
        <!-- <div>
            <el-button size="small" type="success" @click="submitSemVisionUpload">预测（一体化测试用）</el-button>
        </div> -->
    </div>

    
    
    <div  class='chooselabel'>
      <el-upload
          ref="labelUpload"
          class = 'upload-pic'
          :limit = "1"
          :auto-upload="false"
          :on-exceed="handleLabelExceed"
          :on-change="handleLabelUpload"
          >
        <template #trigger>
          <el-button size="small" type="primary">2、选择并上传标注 json 文件</el-button>
        </template>
      </el-upload>
    </div>

     <!-- 显示预测和标注结果 -->

     <div class="eval">
      <!-- <h3>评估结果：匹配结果...</h3> -->
      <!-- <el-button size="small" type="primary">2、选择并上传标注 json 文件</el-button> -->
        <el-button size="small" type="primary" @click="handleEvaluation">3、评估结果</el-button>
    <!-- </div>  -->

    <!-- <div v-if="predictionLoaded && annotationsLoaded"> -->
    <div>
    <el-select
        v-model="select_value"
        clearable
        placeholder="Select"
        style="width: 240px"
        @change="handleSelectChange"
         >
            <el-option
            v-for="item in select_options"
            :key="item.value"
            :label="item.label"
            :value="item.value"
            />
        </el-select>
    </div>
    </div>


    <!-- 图片显示 -->
    <div>
        <canvas ref="canvas" width="640px" height="480px"></canvas>
    </div>

    

    <!-- 预测结果和标注 JSON 文件上传 -->
    <!-- <div v-if="imageUploaded">
      <label for="json-upload">上传标注 JSON 文件:</label>
      <input type="file" id="json-upload" @change="handleJsonUpload" />
    </div> -->
    


    <div class="metrics">
        <h3>评估指标</h3>
        <!-- <el-select
        v-model="selectMetric"
        clearable
        placeholder="Select"
        style="width: 240px"
        @change="handleSelectMetricChange"
         >
            <el-option
            v-for="item in selectMetricOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
            />
        </el-select> -->
        

        <div>
        <h4>混淆矩阵</h4>
        <el-table :data="cmMetricTable" style="width: 100%">
            <el-table-column
            v-for="(column, index) in columnNames"
            :key="index"
            :label="column"
            :prop="'col' + index"
            >
            <template #default="{ row }">
                {{ row['col' + index] }}
            </template>
            </el-table-column>
        </el-table>
    </div>

    <div>
        <h4>精确率</h4>
        <el-table :data="precisionMetricTable" >
            <el-table-column
            v-for="(column, index) in columnNames"
            :key="index"
            :label="column"
            :prop="'col' + index"
            >
            <template #default="{ row }">
                {{ row['col' + index] }}
            </template>
            </el-table-column>
        </el-table>
</div>  

    <div>
        <h4>召回率</h4>
        <el-table :data="recallMetricTable" >
            <el-table-column
            v-for="(column, index) in columnNames"
            :key="index"
            :label="column"
            :prop="'col' + index"
            >
            <template #default="{ row }">
                {{ row['col' + index] }}
            </template>
            </el-table-column>
        </el-table>
    </div>  
    </div>

    

   
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { ElSelect, ElOption, genFileId } from 'element-plus';
import axios from '../axios';
import {   base64ToBlob} from '@/utils/utils';
import {fetchPredict, fetchData, fetchUpload ,convertResult} from '@/api/index';
import {fetchOptonPredict, fetchSemVisionPredict } from '@/api/index';
import {CreateDraw, switchSelect, createPolygon,
    drawImageOnCanvas, drawImageAndPolygons, isPointInPolygon,resizeCanvas,
    getScale,
} from '@/utils/draw';

const initialWidth = ref(1280);
const initialHeight = ref(960);
// const canvas = ref(null);
// 设计交互的时候用
const imgSrc = ref(null);
const highlightedPolygonIndex  = ref(1);

const evalState = reactive({
    pred_ids: [],
    true_ids: [],
    pairs: [],
    matchedPredIds: [],
    unmatchedPredIds: [],
    matchedTrueIds: [],
    unmatchedTrueIds: [],
    jsonPred: null,
    jsonTrue: null,
    }
    )


const canvas = ref(null);
// const canvas1 = ref(null);
const upload = ref(null);
const labelUpload = ref(null);
const imageOriginal = ref(null);
const imageDrawed = ref(false);
const imageUploaded = ref(false);
const predictionLoaded = ref(false);
const annotationsLoaded = ref(false);
const imageData = ref(null); // 用于存储原图数据
const predictionResult = ref(null); // 存储后端预测结果
const annotationData = ref(null); // 存储标注 JSON 数据
const fileName = ref("");  // 上传的文件的文件名

const config = ref(null);
const drawInst = ref(null);
let tableData = ref([]);

const metricData = ref([
    [1, 2]
    [4, 5]
    ]);

const cmMetricData = ref([]);
const precisioMetricData = ref([]);
const recallMetricData = ref([]);

// const columnNames = ref(['二次颗粒', '背景']); // 可以自定义列标题
const columnNames = computed(() => {
    if (value.value[0] == "secondary_particle") {return ['二次颗粒', '背景']}
    else if (value.value[0] == "primary_particle") {return ['一次颗粒', '背景']}
    else if (value.value[0] == "cracking_ball") {return ['开裂球', '背景']}
    else if (value.value[0] == "micro_powder") {return ["二次颗粒",'微粉', "碎球", '背景']}
    else {return ['预测', '背景']}
    });

const fillColorArray = computed(() => {
    const n = columnNames.value.length - 1;
    if ( n == 1) {return ['rgba(0, 0, 255, 0.5)']}
    else if (n ==2) {return ['rgba(0, 0, 255, 0.5)', 'rgba(0, 255, 0, 0.5)']}
    else if (n ==3) {return ['rgba(0, 0, 255, 0.5)','rgba(0, 255, 0, 0.5)', 'rgba(255, 0, 0, 0.5)', ]} // 蓝，绿，红
    else {
        return Array(n).fill('rgba(0, 0, 255, 0.5)'); 
    }
    });
   
    
// const tableData1 = ref([]);
const cmMetricTable = computed(() =>
        cmMetricData.value.map(row => {
        const obj = {};
        row.forEach((cell, index) => {
        obj[`col${index}`] = cell;
        });
        return obj;
    })
);

const precisionMetricTable = computed(() =>
        precisioMetricData.value.map(row => {
        const obj = {};
        row.forEach((cell, index) => {
        obj[`col${index}`] = cell.toFixed(2);
        });
        return obj;
    })
);

const recallMetricTable = computed(() =>
        recallMetricData.value.map(row => {
        const obj = {};
        row.forEach((cell, index) => {
        obj[`col${index}`] = cell.toFixed(2);
        });
        return obj;
    })
);


const value = ref([]);
const options = ref([  
    {value: 'secondary_particle', label: '二次颗粒', children: [{value: 'big', label: '大颗粒'}, {value: 'small', label: '小颗粒'}, {value: 'cont', label: '连续式'},
            {value: 'cyto', label: 'cyto'}, {value: 'nuclei', label: 'nuclei'}, {value: 'tissue', label: 'tissue'},
            {value: 'live', label: 'live'}, {value: 'cyto2', label: 'cyto2'}, {value: 'CP', label: 'CP'},
            {value: 'CPx', label: 'CPx'}, {value: 'TN1', label: 'TN1'}, {value: 'TN2', label: 'TN2'},
            {value: 'LC1', label: 'LC1'}, {value: 'LC2', label: 'LC2'}, {value: 'LC3', label: 'LC3'},{value: 'LC4', label: 'LC4'}
            ]},  
    {value: 'primary_particle', label: '一次颗粒', children: [{value: 'needle', label: '针状'}, {value: 'strip', label: '条状'}, {value: 'plate', label: '板状'}]},  
    {value: 'cracking_ball', label: '开裂球', children: [{value: 'big', label: '大颗粒'}, {value: 'cont', label: '连续式'}]},  
    {value: 'micro_powder', label: '微粉', children: [{value: 'big', label: '大颗粒'}, {value: 'small', label: '小颗粒'},]}  
]);
const props = {
  expandTrigger: 'hover',
}


// 使用选择模式变量
const select_value = ref('');
const select_options = ref([
  { value: 'wholePreds', label: '所有预测实例' },
  { value: 'wholeTrue', label: '所有真实实例' },
  { value: 'matchedPairs', label: '配对的实例' },
  { value: 'unmatchedPreds', label: '未匹配的预测实例' },
  { value: 'unmatchedTrues', label: '未匹配的真实实例' }
]);


// // 图片上传
// const handleImageUpload = (file, fileList)=>{
//     console.log("开始", file);
//     imageOriginal.value = file;
//     const reader = new FileReader();
//     reader.onload = (e) => {
//         imageData.value = e.target.result;
//         imageDrawed.value = true;
//         drawImageOnCanvas(canvas.value, imageData.value); // 绘制原图
//   };
//   reader.readAsDataURL(file.raw);
// }

const handleImageUpload = (file, fileList) => {
    console.log("开始", file);
    imageOriginal.value = file;
    fileName.value = file.name;
    console.log("fileName", fileName.value);
    const reader = new FileReader();
    reader.onload = (e) => {
        imageData.value = e.target.result;
        const img = new Image();
        img.onload = () => {
            initialWidth.value = img.width;
            initialHeight.value = img.height;
            // console.log('initialWidth', initialWidth.value);
            // console.log('initialHeight', initialHeight.value);
            drawImageOnCanvas(canvas.value, imageData.value); // 绘制原图
        };
        img.src = e.target.result;
        imageDrawed.value = true;
    };
    reader.readAsDataURL(file.raw);
};

const handleExceed = (files, fileList) => {
    // 清空当前选择，重新选择
    //
    // 限制选择 1 个文件
    upload.value.clearFiles();
    const file = files[0];
    file.uid = genFileId();
    upload.value.handleStart(file);

    // console.log('handleExceed', files, fileList);
    // this.$message.warning(`当前限制选择 1 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
}


const handleLabelExceed = (files, fileList) => {
    // 清空当前选择，重新选择
    //
    // 限制选择 1 个文件
    labelUpload.value.clearFiles();
    const file = files[0];
    file.uid = genFileId();
    labelUpload.value.handleStart(file);

    // console.log('handleExceed', files, fileList);
    // this.$message.warning(`当前限制选择 1 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
}

// 提交预测
const submitUpload = (files, fileList) => {
    const response = fetchPredict(value.value[0], value.value[1], imageOriginal.value);
    
    response.then((response) => {
        console.log('请求 infer 成功:');
        // 存储到 Pinia store 中

        
        predictionResult.value = response.predict; 
        const img = new Image();
        img.src = predictionResult.value;
        img.onload = () => {
            const ctx = canvas.value.getContext('2d');
            ctx.drawImage(img, 0, 0, canvas.value.width, canvas.value.height);
        };
        predictionLoaded.value = true;       
        console.log('response_infer', response.predict_png);
    });

}

// 提交预测
const submitOptonUpload = (files, fileList) => {
    const response = fetchOptonPredict(value.value[0], value.value[1], imageOriginal.value);
    
    response.then((response) => {
        console.log('请求 infer 成功:');        
        predictionResult.value = response.predict; 
        const img = new Image();
        img.src = predictionResult.value;
        img.onload = () => {
            const ctx = canvas.value.getContext('2d');
            ctx.drawImage(img, 0, 0, canvas.value.width, canvas.value.height);
        };
        predictionLoaded.value = true;       
        console.log('response_infer', response.predict_png);
    });

}

// 提交预测
const submitSemVisionUpload = (files, fileList) => {
    const response = fetchSemVisionPredict(value.value[0], value.value[1], imageOriginal.value);
    
    response.then((response) => {
        console.log('请求 infer 成功:');        
        predictionResult.value = response.predict; 
        const img = new Image();
        img.src = predictionResult.value;
        img.onload = () => {
            const ctx = canvas.value.getContext('2d');
            ctx.drawImage(img, 0, 0, canvas.value.width, canvas.value.height);
        };
        predictionLoaded.value = true;       
        console.log('response_infer', response.predict_png);
    });

}




// 上传标注 JSON 文件 和 预测结果并保存在服务器上
const handleLabelUpload = (file, fileList) =>{
    // fetchUpload(predictionResult.value, file.raw); 
    fetchUpload(file.raw);
    annotationsLoaded.value = true;
}


const handleEvaluation = () => {
    if (value.value[0] === null) {
        console.log('请先选择模型预测目标');
        return;
    }
    const res = fetchData(0.3, 0.45, value.value[0], fileName.value);

    res.then((response) => {
        // console.log('response', response);
        const result = convertResult(response);
        Object.assign(evalState, result);
        // console.log('evalState', evalState);

        // 创建绘制对象
        console.log('canvas.value.width', canvas.value.width);
        canvas.value.width = canvas.value.clientWidth;
        canvas.value.height = canvas.value.clientHeight;
        const configSet = {
            canvas: canvas.value,
            imgSrc: imageData,
            initialWidth: initialWidth.value,
            initialHeight: initialHeight.value,
            jsonPred: evalState.jsonPred,
            jsonTrue: evalState.jsonTrue,
            predShowIndexList: evalState.predIds,
            trueShowIndexList: evalState.trueIds,
            unmatchedPredIds: evalState.unmatchedPredIds,
            unmatchedTrueIds: evalState.unmatchedTrueIds,
            matchedPredIds: evalState.matchedPredIds,
            matchedTrueIds: evalState.matchedTrueIds,
            // fillColor: 'rgba(0, 0, 255, 0.5)'
            fillColor: fillColorArray.value  // 由原来的单独颜色改为了颜色数组
            }
        
        cmMetricData.value = response.cm;
        precisioMetricData.value = response.p;
        recallMetricData.value = response.r;

        Object.assign(config, configSet);
        drawInst.value = new CreateDraw(config);    
        console.log('drawInst', drawInst.value); 
        tableData = drawInst.value.drawWholePreds();  
        });
    }



const handleSelectChange = (newValue) => {
    // console.log('drawInst.value', drawInst.value.drawWholePreds());
    switchSelect(drawInst.value, newValue);
  }


const selectMetric = ref('');
const selectMetricOptions = [
    { value: 'cm', label: '混淆矩阵' },
    { value: 'precision', label: '精确率' },
    { value: 'recall', label: '召回率' },
];

const handleSelectMetricChange = (newValue) => {
    console.log('newValue', newValue);
    switch (newValue) {
        case 'cm':
            break;
        case 'precision':
            break;
        case 'recall':
            break;
        default:
            break;
    }
}


// onMounted(() => {
//     const data = [
    // [1, 2, 3],
    // [4, 5, 6],
    // [7, 8, 9]
    // ];
//     // const columnNames = ['Column 1', 'Column 2', 'Column 3']; // 可以自定义列标题
// });


</script>


<style>
.chooseimg{
    margin-top: 20px;
}

.chooselabel{
    margin-top: 20px;
}

.eval{
    margin-top: 20px;
}

canvas {
    border: 1px solid #000;
    background-color: #f0f0f0;
    cursor: pointer;
    margin-top: 20px;
}
</style>