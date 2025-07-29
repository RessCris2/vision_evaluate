<template>
  <!-- <div class="chart-container"> -->
    <!-- 分箱数量控制 -->
    <div class="controls">
      <div class="control-group">
        <label>分箱数量:</label>
        <input 
          type="number" 
          v-model.number="binNumber" 
          min="1" 
          max="50" 
          class="bin-input"
        >
      </div>
    </div>

    <!-- 直方图容器 -->
    <div ref="histogramChart" class="chart"></div>
    
    <!-- 滑动条 -->
    <!-- <div class="slider-container">
      <input 
        type="range" 
        v-model="sliderValue"
        :min="0"
        :max="bins.length - 1"
        step="1"
        @input="updateHighlight"
      />
      <div>当前区间：{{ currentRange }}</div>
      <div>频数：{{ currentCount }}</div> -->
    <!-- </div> -->
  <!-- </div> -->
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import * as echarts from 'echarts';
import { useEvaluateStore } from '@/stores/evaluateStore';
import { useCommonStore } from '@/stores/commonStore';
import { storeToRefs } from 'pinia';

// 示例面积数据
// const areas = ref([120, 200, 150, 80, 70, 110, 130, 90, 160, 140]);

// 使用 pinia 获取变量
const evaluateStore = useEvaluateStore();
const commonStore = useCommonStore();
const { phraseTarget,
    modelCategory,
    imageNames,
    specificImageName,
    iouThreshold,
    selectedImage } = storeToRefs(commonStore);
  
const evaluateResultDict = evaluateStore.evaluateResultDict;
const specificResult = computed(() => evaluateResultDict[selectedImage.value]);
const areas = computed(() => specificResult.value.gt_shapes.shapes.map(item => item.area));

const sliderValue = ref(0);

// 直方图配置
const histogramChart = ref(null);
let chartInstance = null;

const binNumber = ref(5); // 可绑定到界面控件

// 计算直方图分箱
const bins = computed(() => {
  const values = areas.value;
  if(values.length === 0) return [];
  
  const min = Math.min(...values);
  const max = Math.max(...values);
  const binSize = (max - min) / binNumber.value;
  
  // 处理相等值的情况
  const adjustedBinSize = binSize === 0 ? 1 : binSize;
  
  return Array.from({ length: binNumber.value }, (_, i) => {
    const lower = min + i * adjustedBinSize;
    const upper = min + (i + 1) * adjustedBinSize;
    return {
      binsize: adjustedBinSize,
      range: [lower, upper],
      count: values.filter(x => x >= lower && (i === binNumber.value - 1 ? x <= upper : x < upper)).length
    };
  });
});

// 当前高亮区间信息
const currentRange = computed(() => {
  const bin = bins.value[sliderValue.value];
  return `${bin.range[0].toFixed(1)} - ${bin.range[1].toFixed(1)}`;
});

const currentCount = computed(() => bins.value[sliderValue.value].count);

// 初始化图表
onMounted(() => {
  chartInstance = echarts.init(histogramChart.value);
  updateChart();
});

// 更新图表
const updateChart = () => {
  const option = {
    // title: {
    //   text: '面积值分布直方图',
    //   left: 'center'
    // },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}'
    },
    xAxis: {
      type: 'category',
      data: bins.value.map((_, i) =>  `${ bins.value[i].range[0].toFixed(0) }-${ bins.value[i].range[1].toFixed(0) }`),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '频数'
    },
    series: [{
      data: bins.value.map(bin => bin.count),
      type: 'bar',
      barWidth: '40%',
      itemStyle: {
        color: '#5470C6'
      },
      emphasis: {
        itemStyle: {
          color: '#EE6666'
        }
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '5%',
      containLabel: true
    }
  };
  chartInstance.setOption(option);
};

// 高亮对应区间
const updateHighlight = () => {
  chartInstance.dispatchAction({
    type: 'downplay',
    seriesIndex: 0
  });
  chartInstance.dispatchAction({
    type: 'highlight',
    seriesIndex: 0,
    dataIndex: sliderValue.value
  });
};

// 响应数据变化
watch(areas, () => {
  updateChart();
});

// 监听分箱数量变化
watch(binNumber, (newVal, oldVal) => {
  if(newVal !== oldVal) {
    sliderValue.value = 0; // 重置滑动条位置
    updateChart();
  }
});
</script>

<style scoped>
/* .chart-container { */
  /* width: 100%; */
  /* padding: 20px; */
/* } */
.chart {
  width: 300px;
  height: 300px; 
  /* min-width: 200px;  */
}

/* .bin-input {
  width: 80px;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
} */


/* 
.slider-container {
  margin-top: 30px;
  padding: 0 20px;
} */

/* .slider {
  width: 100%;
  margin: 15px 0;
} */
</style>