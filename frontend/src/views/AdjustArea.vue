<template>


</template>

<script setup>
// 调整实例的面积阈值，计算不同段面积实例的指标情况，计算的依据是 matches 的数据。

// 数据预处理函数
// 核心计算函数
function calculateRecallByRange(areas, matches, minArea, maxArea) {
  // 参数校验
  if (typeof minArea !== 'number' || typeof maxArea !== 'number' || minArea > maxArea) {
    throw new Error('Invalid area range');
  }

  // 创建匹配实例的快速查找表
  const matchedGtIndices = new Set(
    matches.flatMap(match => 
      Array.isArray(match.gtIndex) ? match.gtIndex : [match.gtIndex]
    )
  );

  // 统计区间内实例
  let total = 0;
  let matched = 0;

  areas.forEach((area, gtIndex) => {
    if (area >= minArea && area <= maxArea) {
      total++;
      if (matchedGtIndices.has(gtIndex)) {
        matched++;
      }
    }
  });

  return {
    total,
    matched,
    recall: total > 0 ? Number((matched / total).toFixed(4)) : 0,
    minArea,
    maxArea
  };
}



</script>