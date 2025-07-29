<template>
    <el-button size="small" type="primary" @click="handleEvaluationBatch">2、批量评估结果</el-button>
    <div v-if="evaluateCompleted">
                <el-button size="small" type="warning">评估完成！耗时 {{takeTime}}s</el-button>

    </div>
    <div v-if="evaluateState">
                <el-button size="small" type="warning">评估中</el-button>
            </div>

    <div class="iou-container">
      <div class="iou-control">
        <label> IoU </label>
        <el-input-number v-model="iou_thres" :min="0.3" :max="0.95" :step="0.05" @change="handleIoUChange"/>
      </div>
      <!-- <div class="filter-control">
        <label> 过滤标签 </label>
        <el-input
          v-model="searchText"
          placeholder="微粉需要填过滤的标签名"
          clearable
          style="width: 200px"
        />
      </div> -->
    </div>


    <div class="batch_metrics">
        <h3>批量评估结果</h3>
        
        <el-table :data="batchMetricData" style="width: 100%; max-height: 400px; overflow-y: auto;" @row-click="handleRowClick" :row-class-name="tableRowClassName">
            <el-table-column prop="index" label="序号"></el-table-column>
            <el-table-column prop="picname" label="图片名"></el-table-column>
            <el-table-column prop="cate" label="类名"></el-table-column>
            <el-table-column prop="whole_true" label="真实实例数"></el-table-column>
            <el-table-column prop="whole_pred" label="预测实例数"></el-table-column>
            <el-table-column prop="true_pred" label="预测正确数"></el-table-column>
            <el-table-column prop="precision" label="精确率"></el-table-column>
            <el-table-column prop="recall" label="召回率"></el-table-column>
            <el-table-column prop="elapsed_time" label="评估耗时"></el-table-column>
        </el-table>
        <el-button size="small" type="success" @click="exportTableData">导出数据</el-button>
    </div>
    <div v-if="unmatchedImages.length > 0">
        <strong style="color: red;">未评估成功的图片: {{ unmatchedImages }} 共 {{ unmatchedImages.length }}张</strong>
    </div>

</template>

<script setup>
import { ref, reactive } from 'vue';
import { fetchDataBatch, fetchData, convertResult } from '@/api/evaluate';
import { useEvaluateStore } from '@/stores/evaluateStore';
import { useCommonStore } from '@/stores/commonStore';
import axios from '@/axios';
import { storeToRefs } from 'pinia';


const evaluateStore = useEvaluateStore();
const commonStore = useCommonStore();
const {phraseTarget,
        modelCategory,
        predictType,
        imageNames,
        specificImageName,
        iouThreshold,
        selectedImage,
        selectedCate,
        file_key} = storeToRefs(commonStore);

const iou_thres = ref(0.45);
const batchMetricData = ref([]);// 用于存储批量评估结果
const evaluateCompleted = ref(false);
const takeTime = ref(0);
const evaluateState = ref(false);
const searchText = ref(''); // 用于过滤表格数据

// Property "unmatchedImages" was accessed during render but is not defined on instance. 
const unmatchedImages = ref([]);

const handleEvaluationBatch = async () => {
    if (commonStore.phraseTarget=== null) {
        console.log('请先选择模型预测目标');
        return;
    }
    

    evaluateState.value = true;
    evaluateCompleted.value = false;
    console.log('评估的文件列表', commonStore.imageNames);
    // const imgFileList = commonStore.imageNames;

    const startTime = Date.now();

    // file_key 拼接了phraseTarget和modelCategory, 还有时刻戳
    file_key.value = `${commonStore.phraseTarget}_${commonStore.modelCategory}_${Date.now()}`;

    const eval_result = await fetchDataBatch(
      0.3, 
      iou_thres.value, 
      commonStore.phraseTarget,
      file_key.value,
      commonStore.imageNames, 
      searchText.value
    )
 
     for (const [filename, result] of Object.entries(eval_result.data)) {
        if (!evaluateStore.evaluateResultDict[filename]) {
          evaluateStore.evaluateResultDict[filename] = reactive({})
        }
        
        for (const [category, item_result] of Object.entries(result)) {
            evaluateStore.evaluateResultDict[filename][category] = item_result;
        }
      }
    
    console.log('Updated evaluateResultDict:', evaluateStore.evaluateResultDict);

    const endTime = Date.now();
    takeTime.value = (endTime - startTime) / 1000;
    // console.log(`Total time for promises execution: ${takeTime} ms`);
    evaluateState.value = false;
    evaluateCompleted.value = true;

    // 比较请求图片数和返回结果数的差异，提醒有多少未评估成功，具体列出来是哪些图片没成功
    const requestedSet = new Set(commonStore.imageNames);
    const returnedSet = new Set(Object.keys(eval_result.data));
    unmatchedImages.value = [...requestedSet].filter(image => !returnedSet.has(image));
    

    // 计算 batchMetricData
    const response = await axios({
        method: 'get',
        url: '/evaluate/download-excel',
        params: {
            phrase_target: commonStore.phraseTarget,
            filelist: commonStore.imageNames,
            file_key: file_key.value,
            label_name: searchText.value,
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
    });
    // response 是一个二维数组，每一行是一个文件的评估结果，想绘制在前端表格中
    

    
    // syncNestedToTable( response.data);
    batchMetricData.value = response.data;
    console.log('batchMetricData', batchMetricData.value);


};

// 改为批量评估
const handleIoUChange = () => {
    commonStore.iouThres = iou_thres.value;
}

const exportTableData = () => {
    const data = batchMetricData.value;
    // 获取表头
    const headers = Object.keys(data[0]).join(","); 
    // 获取每行数据 
    const rows = data.map(row => Object.values(row).map(value => `"${value}"`).join(",") ).join("\n"); 
    const csvContent = "data:text/csv;charset=utf-8," + headers + "\n" + rows;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "batch_metrics.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
        
const handleRowClick = (row) => {
    selectedImage.value = row.picname;
    selectedCate.value = row.cate;
}

// 动态设置行的类名
const tableRowClassName = ({ row }) => {
    // 如果当前行是选中的行，返回高亮类名
    return row.picname === selectedImage.value && row.cate==selectedCate.value ? "highlight-row" : "";
}

</script>

<style>
.iou-container {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 15px;
}

.iou-control, .filter-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 定义高亮行的样式 */
.highlight-row {
  background-color: pink !important; /* 设置为粉色 */
}
</style>