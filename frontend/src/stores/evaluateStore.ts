import { defineStore } from "pinia";
import {ref, reactive, Ref} from "vue";


export const useEvaluateStore = defineStore('evaluateResultDict', () => {
    // const evaluateResultDict = reactive<Record<string, EvaluationResult>>({});
    const evaluateResultDict = reactive<Record<string, Record<string, EvaluationResult>>>({})

      /**
     * 批量添加评估结果
     */
    // const addBatchResults = (results: Record<string, Record<string, any>>) => {
    //   for (const [filename, categories] of Object.entries(results)) {
    //     if (!evaluateResultDict[filename]) {
    //       evaluateResultDict[filename] = reactive({})
    //     }
        
    //     for (const [category, result] of Object.entries(categories)) {
    //         evaluateResultDict[filename][category] = {
    //               matches: [],
    //               ious: [],
    //               whole_iou: [[]],
    //               gt_shapes: { shapes: [] },
    //               pred_shapes: { shapes: [] },
    //               cm: [[]],
    //               precision: [[]],
    //               recall: [[]],
    //               mean_results: [],
    //               ap: [],
    //               elapsed_time: 0
    //           }
    //     }
    //   }
    // }

    return {
      evaluateResultDict
      // addBatchResults
    };
})


export interface Shapes {
    shapes: Shape[]; // 一个图片可能有多个形状? 这里可能有点问题， key 是固定值 shapes
}

export interface Shape {
    cls_id: number;
    label: string;
    points: number[][];
    shape_type: 'polygon';
    id: number;
    area: number; // 面积
}

export interface EvaluationResult {
    matches: number[]; // 真实和预测的匹配结果
    ious: number[]; // Intersection Over Union (IOU) 值
    whole_iou: number[][]; // 整体 IOU 值
    gt_shapes: Shapes,
    pred_shapes: Shapes,
    cm: number[][]; // 混淆矩阵,
    precision: number[][],
    recall: number[][],
    mean_results: number[],
    ap: number[],
    elapsed_time: number,
    [key: string]: any; // 如果评估结果中可能有其他动态属性
  }


export interface ImageBatchEvaluation {
    [imageName: string]: EvaluationResult;
  }
  

/**
 * 根据面积范围计算过滤后的召回率和精确率
 * @param result 评估结果对象
 * @param area_min 最小面积
 * @param area_max 最大面积
 * @returns 包含召回率和精确率的对象
 */
export function calculateFilteredMetrics (result: Ref<EvaluationResult>, area_min: Ref<number>, area_max: Ref<number>): 
     {truePositives:number, tp2:number, recall: number, precision: number, pred_length: number, gt_length: number} {
    // 参数校验
    if (area_min.value > area_max.value) throw new Error("area_min不能大于area_max");
    
    // 1. 过滤符合条件的GT和Pred实例
    const filteredGtIndices = result.value.gt_shapes.shapes
      .map((shape, index) => ({ index, shape }))
      .filter(({ shape }) => shape.area >= area_min.value && shape.area <= area_max.value)
      .map(({ index }) => index);
  
    const filteredPredIndices = result.value.pred_shapes.shapes
      .map((shape, index) => ({ index, shape }))
      .filter(({ shape }) => shape.area >= area_min.value && shape.area <= area_max.value)
      .map(({ index }) => index);
  
    // 2. 创建快速查找表
    const validGtSet = new Set(filteredGtIndices);
    const validPredSet = new Set(filteredPredIndices);
  
    // 3. 统计有效匹配数
    let truePositives = 0;
    // filteredGtIndices.forEach(gtIndex => {
    //   const predIndex = result.value.matches[gtIndex][1];
    //   if (predIndex !== -1 && validPredSet.has(predIndex)) {
    //     truePositives++;
    //   }
    // });
  
    // filteredPredIndices.forEach(predIndex => {
    //     const gtIndex = result.value.matches[predIndex][1];
    //     if (gtIndex !== -1 && validGtSet.has(gtIndex)) {
    //       truePositives++;
    //     }
    //   });
    result.value.matches.forEach((match, index) => {
        const gtIndex = match[0];
        const predIndex = match[1];
        const isGtValid = gtIndex !== -1 && validGtSet.has(gtIndex);
        const isPredValid = predIndex !== -1 && validPredSet.has(predIndex);
        // if (isGtValid && isPredValid) {
        if (isGtValid ) {
          truePositives++; 
        }
    });

    let tp2 = 0;
    result.value.matches.forEach((match, index) => {
        const gtIndex = match[0];
        const predIndex = match[1];
        // const isGtValid = gtIndex !== -1 && validGtSet.has(gtIndex);
        const isPredValid = predIndex !== -1 && validPredSet.has(predIndex);
        // if (isGtValid && isPredValid) {
        if (isPredValid ) {
            tp2++; 
        }
    });

    // 4. 计算指标（处理除零情况）
    const recall = filteredGtIndices.length > 0 
      ? Number((truePositives / filteredGtIndices.length).toFixed(4))
      : 0;
  
    const precision = filteredPredIndices.length > 0
      ? Number((tp2 / filteredPredIndices.length).toFixed(4))
      : 0;
    
    const gt_length = filteredGtIndices.length;
    const pred_length = filteredPredIndices.length;
    return { truePositives, tp2, recall, precision, pred_length, gt_length };
  }