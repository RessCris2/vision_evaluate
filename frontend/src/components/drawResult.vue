<template>
    <div>
        <div class="header" >
            <h3 style="font-weight: bold;">指定图片评估结果</h3>
            <h4 style="color: orange; font-weight: bold;">(点击上面表格中的图片行)</h4>
        </div>
        <!-- 增加是否显示chart 选项 -->
        <el-checkbox v-model="isChartVisible">显示图表</el-checkbox>
        <Suspense>
            <template #default>
                <Chart v-if="isChartVisible" />
            </template>
            <template #fallback>
                <div>Loading chart...</div>
            </template>
        </Suspense>
        <!-- <div>面积过滤后的精确率{{ metrics.precision }}</div>
        <div>面积过滤后的召回率为{{ metrics.recall }}</div>
        <div>面积过滤后的tp为{{ metrics.truePositives }}</div>
        <div>面积过滤后的tp2为{{ metrics.tp2 }}</div>
        <div>面积过滤后的pred_len为{{ metrics.pred_length }}</div>
        <div>面积过滤后的true_len为{{ metrics.gt_length }}</div> -->
        <el-checkbox v-model="isMetricsVisible">显示面积分段指标</el-checkbox>
        <div class="metrics-table">
        <!-- 增加是否显示chart 选项 -->
        <table v-if="isMetricsVisible">
            <thead>
            <tr>
                <th colspan="2">面积过滤后指标统计</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td class="label">精确率 (Precision)</td>
                <td class="value">{{ metrics.precision.toFixed(4) }} ({{ (metrics.precision * 100).toFixed(2) }}%)</td>
            </tr>
            <tr>
                <td class="label">召回率 (Recall)</td>
                <td class="value">{{ metrics.recall.toFixed(4) }} ({{ (metrics.recall * 100).toFixed(2) }}%)</td>
            </tr>
            <tr class="highlight">
                <td class="label">标注实例中面积段内匹配数  </td>
                <td class="value">{{ metrics.truePositives }} </td>
            </tr>
            <tr class="highlight">
                <td class="label">预测实例中面积段内匹配数  </td>
                <td class="value"> {{ metrics.tp2 }}</td>
            </tr>
            <tr>
                <td class="label">预测总数</td>
                <td class="value">{{ metrics.pred_length }}</td>
            </tr>
            <tr>
                <td class="label">真实总数</td>
                <td class="value">{{ metrics.gt_length }}</td>
            </tr>
            </tbody>
        </table>
        </div>
    </div>
    <div class="area-container">
        <label>面积范围</label>
        <el-input-number v-model="area_min" :min="0" :max="10000000"  :step="1000" />
        <el-input-number v-model="area_max" :min="1" :max="10000000" :step="1000"  />
        <!-- 显示 metrics变量 的值 -->

        
        <!-- 组件模板部分 -->
        <!-- <div v-if="metrics"> 
            <div>面积过滤后的精确率召回率为{{ metrics }}</div>
        </div>
        <div v-else>
           <div></div>
        </div> -->

         
    </div>

    <div class="canvas-container">

        <div>
            <el-select
            v-model="selectedValue"
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
            <canvas ref="canvas" width="640px" height="480px"></canvas>
        </div>

        <div>
            <el-select
            v-model="selectedValueRepeat"
            placeholder="Select"
            style="width: 240px"
            @change="handleSelectChangeRepeat"
            >
                <el-option
                v-for="item in select_options"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                />
            </el-select>
            <canvas ref="canvas_repeat" width="640px" height="480px"></canvas>
        </div>
    </div> 

    
    <div class="metrics" style="margin-top: 20px;">
        <h3 style=" font-weight: bold;">评估指标</h3>

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

<script setup lang="ts">
import { CreateDraw, switchSelect } from '../utils/draw';
import { convertResult } from '../api/evaluate';
import { ref, reactive, computed, watch, onMounted } from 'vue';
import { select_options }  from './option';
import { useCommonStore } from '../stores/commonStore';
import { useEvaluateStore, calculateFilteredMetrics } from '../stores/evaluateStore';
import { usePredictStore } from '../stores/predictStore';
import { storeToRefs } from 'pinia';
import Chart from './Charts.vue';

const isChartVisible = ref(false);
const isMetricsVisible = ref(false);
const evaluateStore = useEvaluateStore();
const predictStore = usePredictStore();
const commonStore = useCommonStore();
const { phraseTarget,
    modelCategory,
    imageNames,
    specificImageName,
    iouThreshold,
    selectedImage,
selectedCate, file_key } = storeToRefs(commonStore);


const evaluateResultDict = evaluateStore.evaluateResultDict;
const predictResultDict = predictStore.predictResultDict;
const specificPredict =computed(() => predictResultDict[selectedImage.value]);
// const specificResult = computed(() => evaluateResultDict[selectedImage.value][useCommonStore().selectedCate]);//.?[selectedCate.value]);
const specificResult = computed(() => {
  // 使用可选链操作符安全访问
  return evaluateResultDict[selectedImage.value]?.[selectedCate.value] ?? null
});
// const imgOriginal = computed(() => {
//   const selected = selectedImage.value;
//   return selected && predictResultDict[selected] ? predictResultDict[selected].predictMask : null;
// });

// const columnNames = ref(['c1']);
// const columnNames = ref(['二次颗粒', '背景']); // 可以自定义列标题
const columnNames = computed(() => {
    if (phraseTarget.value == "secondary_particle") {return ['二次颗粒', '背景']}
    else if (phraseTarget.value == "primary_particle") {return ['一次颗粒', '背景']}
    else if (phraseTarget.value == "cracking_ball") {return ['开裂球', '背景']}
    else if (phraseTarget.value == "micro_powder") {return ["二次颗粒",'微粉', "碎球", '背景']}
    else {return ['预测', '背景']}
    });

// 模块1 展示图片
const fillColorArray = computed(() => {
    const n = columnNames.value.length - 1;
    console.log('n', n);
    if (n == 1) { return ['rgba(0, 0, 255, 0.5)'] }
    else if (n == 2) { return ['rgba(0, 0, 255, 0.5)', 'rgba(0, 255, 0, 0.5)'] }
    else if (n == 3) { return ['rgba(0, 0, 255, 0.5)', 'rgba(0, 255, 0, 0.5)', 'rgba(255, 0, 0, 0.5)'] } // 蓝，绿，红
    else {
    return Array(n).fill('rgba(0, 0, 255, 0.5)');
    }
});
const selectedValue = ref('wholeTrue');
const selectedValueRepeat = ref('wholePreds');
const canvas = ref(null);
const canvas_repeat = ref(null);
const drawInst = ref(null); // Add this line to define drawInst
const area_min = ref(0);
const area_max = ref(1000000000);

interface Result {
    predIds: number[];
    trueIds: number[];
    pairs: any[];
    matchedPredIds: number[];
    unmatchedPredIds: number[];
    matchedTrueIds: number[];
    unmatchedTrueIds: number[];
    jsonPred: any;
    jsonTrue: any;
}

const result = reactive<Result>({
    predIds: [],
    trueIds: [],
    pairs: [],
    matchedPredIds: [],
    unmatchedPredIds: [],
    matchedTrueIds: [],
    unmatchedTrueIds: [],
    jsonPred: null,
    jsonTrue: null
})

const handleSelectChange = (newValue) => {
    const convertedResult = convertResult(specificResult.value);
    Object.assign(result, convertedResult);
    const config = reactive({
        canvas: canvas.value,
        // imgSrc: imgOriginal, // Add .value to imgOrginal
        imgSrc: specificPredict.value.image, // Add this line to define imgSrc
        initialWidth: specificPredict.value.initialWidth, // Add this line to define initialWidth
        initialHeight: specificPredict.value.initialHeight, // Add this line to define initialHeight
        jsonPred: result.jsonPred,
        jsonTrue: result.jsonTrue,
        predShowIndexList: result.predIds,
        trueShowIndexList: result.trueIds,
        unmatchedPredIds: result.unmatchedPredIds,
        unmatchedTrueIds: result.unmatchedTrueIds,
        matchedPredIds: result.matchedPredIds,
        matchedTrueIds: result.matchedTrueIds,
        fillColor: fillColorArray.value,  // 由原来的单独颜色改为了颜色数组
        area_min: area_min.value,
        area_max: area_max.value
        });

    config.canvas = canvas.value;
    drawInst.value = new CreateDraw(config);
    console.log('drawInst', drawInst.value);
    switchSelect(drawInst.value, newValue);
}


const handleSelectChangeRepeat = (newValue) => {
    const convertedResult = convertResult(specificResult.value);
    Object.assign(result, convertedResult);
    const config = reactive({
        canvas: canvas_repeat.value,
        // imgSrc: imgOriginal, // Add .value to imgOrginal
        imgSrc: specificPredict.value.image, // Add this line to define imgSrc
        initialWidth: specificPredict.value.initialWidth, // Add this line to define initialWidth
        initialHeight: specificPredict.value.initialHeight, // Add this line to define initialHeight
        jsonPred: result.jsonPred,
        jsonTrue: result.jsonTrue,
        predShowIndexList: result.predIds,
        trueShowIndexList: result.trueIds,
        unmatchedPredIds: result.unmatchedPredIds,
        unmatchedTrueIds: result.unmatchedTrueIds,
        matchedPredIds: result.matchedPredIds,
        matchedTrueIds: result.matchedTrueIds,
        fillColor: fillColorArray.value,  // 由原来的单独颜色改为了颜色数组
        area_min: area_min.value,
        area_max: area_max.value
        });

    config.canvas = canvas_repeat.value;
    drawInst.value = new CreateDraw(config);
    console.log('drawInst', drawInst.value);
    switchSelect(drawInst.value, newValue);
}

const cmMetricData = ref([]);
const precisionMetricData = ref([]);
const recallMetricData = ref([]);

cmMetricData.value = specificResult.value?.cm || [];
precisionMetricData.value = specificResult.value?.p || [];
recallMetricData.value = specificResult.value?.r || [];

    
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
        precisionMetricData.value.map(row => {  
        const obj = {};
        row.forEach((cell, index) => {
        obj[`col${index}`] = cell.toFixed(3);
        });
        return obj;
    })
);

const recallMetricTable = computed(() =>
        recallMetricData.value.map(row => {
        const obj = {};
        row.forEach((cell, index) => {
        obj[`col${index}`] = cell.toFixed(3);
        });
        return obj;
    })
);

// 计算面积过滤后的混淆矩阵
// const metrics = computed(() => calculateFilteredMetrics(specificResult.value, area_min.value, area_max.value));

// 确保计算属性显式依赖 .value
const metrics = computed(() => {
  // 显式访问所有 ref 的 .value 属性
  const result = specificResult.value
  const min = area_min.value
  const max = area_max.value

  if (!result || typeof min !== 'number' || typeof max !== 'number') {
    return { truePositives: 0, tp2:0, precision: 0, recall: 0 , pred_length: 0, gt_length: 0}
  }

  // ✅ 现在 min/max 的每次访问都会被追踪为依赖
  return calculateFilteredMetrics(specificResult, area_min, area_max)
})

// 验证 calculateFilteredMetrics 是否被正确调用
console.log(metrics.value) // 当 area_min/area_max 变化时观察此处输出



watch(
  () => specificResult.value,
  (newValue) => {
    cmMetricData.value = specificResult.value?.cm || [];
    precisionMetricData.value = specificResult.value?.p || [];
    recallMetricData.value = specificResult.value?.r || [];
  },
  { immediate: true } // 确保首次也会触发
);


// watch(
//     () => specificResult.value,
//     (newValue) => {
//         if (canvas.value && specificPredict.value?.image) {
//                 const ctx = canvas.value.getContext('2d');
//                 const img = new Image();
//                 img.src = specificPredict.value.image;
//                 img.onload = () => {
//                         ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
//                         ctx.drawImage(img, 0, 0, canvas.value.width, canvas.value.height);
//                 };
//         }
//         selectedValue.value = '原图';
//     },
//     { immediate: true }
// );

watch(
    [() => selectedImage.value, () => selectedCate.value],
    ([newImage, newCate]) => {
        if (newImage && newCate && canvas.value && specificPredict.value?.image) {
            selectedValue.value = 'wholeTrue';
            selectedValueRepeat.value = 'wholePreds';
            handleSelectChange( selectedValue.value || 'wholeTrue');
            handleSelectChangeRepeat( selectedValueRepeat.value || 'wholePreds');
        }
    },
    { immediate: true }
);


</script> 
<!-- 添加 CSS 实现并排布局 -->
<style scoped>
    .canvas-container {
        display: flex;
        /* justify-content: space-between; */
        gap: 20px;
    }
    .metrics {
        margin-top: 20px;
    }

    .metrics-table {
  max-width: 500px;
  margin: 20px auto;
  font-family: Arial, sans-serif;
}

table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

th {
  background: #f8f9fa;
  padding: 12px;
  border-bottom: 2px solid #dee2e6;
  font-size: 16px;
}

td {
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
}

.label {
  font-weight: 500;
  color: #495057;
  width: 45%;
}

.value {
  color: #2b2d42;
  text-align: right;
}

.highlight td {
  background-color: #f8f9fa;
  font-weight: 600;
}

tr:last-child td {
  border-bottom: none;
}
</style>
