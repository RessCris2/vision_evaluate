<template>
    <div class="range-manager">
      <!-- 添加范围表单 -->
      <el-form :model="form" label-width="60px" class="add-form">
        <el-form-item label="下限">
          <el-input-number 
            v-model="form.lower" 
            :precision="0"
            placeholder="请输入下限值"
          />
        </el-form-item>
        
        <el-form-item label="上限">
          <el-input-number
            v-model="form.upper"
            :precision="0"
            placeholder="请输入上限值"
          />
        </el-form-item>
  
        <el-button 
          type="primary" 
          @click="addRange"
          :disabled="!isValidRange"
        >
          添加范围
        </el-button>
      </el-form>
  
      <!-- 范围展示表格 -->
      <el-table
        :data="ranges"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        class="range-table"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="lower" label="下限" width="120">
          <template #default="{ row }">
            {{ row.lower }}
          </template>
        </el-table-column>
        <el-table-column prop="upper" label="上限" width="120">
          <template #default="{ row }">
            {{ row.upper}}
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ $index }">
            <el-button
              size="small"
              type="danger"
              @click="deleteRange($index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
  
      <!-- 批量操作 -->
      <div class="batch-actions">
        <el-button
          type="danger"
          :disabled="selectedRanges.length === 0"
          @click="batchDelete"
        >
          批量删除 ({{ selectedRanges.length }})
        </el-button>
        
        <el-button
          type="success"
          :disabled="selectedRanges.length === 0"
          @click="submitRanges"
        >
          提交选中项
        </el-button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, computed } from 'vue'
  
  // 表单数据
  const form = reactive({
    lower: null,
    upper: null
  })
  
  // 范围列表
  const ranges = ref([])
  
  // 选中项
  const selectedRanges = ref([])
  
  // 验证范围有效性
  const isValidRange = computed(() => {
    return form.lower !== null && 
           form.upper !== null && 
           form.lower < form.upper
  })
  
  // 添加范围
  const addRange = () => {
    if (!isValidRange.value) return
    
    ranges.value.push({
      lower: form.lower,
      upper: form.upper
    })
    
    // 重置表单
    form.lower = null
    form.upper = null
  }
  
  // 删除单个范围
  const deleteRange = (index) => {
    ranges.value.splice(index, 1)
  }
  
  // 批量删除
  const batchDelete = () => {
    const indexes = selectedRanges.value.map(item => 
      ranges.value.indexOf(item)
    )
    ranges.value = ranges.value.filter(
      (_, index) => !indexes.includes(index)
    )
    selectedRanges.value = []
  }
  
  // 提交选中项
  const submitRanges = () => {
    console.log('提交范围:', selectedRanges.value)
    // 这里可以添加实际提交逻辑
  }
  
  // 表格选择变化
  const handleSelectionChange = (val) => {
    selectedRanges.value = val
    console.log('selectedRanges:', selectedRanges.value)
  }
  </script>
  
  <style scoped>
  .range-manager {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    
  }
  
  .add-form {
    display: flex;
    gap: 20px;
    /* align-items: flex-end; */
    /* margin-bottom: 20px; */
  }
  
  .range-table {
    margin: 20px 0;
  }
  
  .batch-actions {
    display: flex;
    gap: 10px;
    /* width:10px; */
    /* height:10px; */
    justify-content: flex-end;
     /* 直接控制按钮尺寸 */
    .el-button {
        padding: 5px 10px;       /* 调整内边距 */
        font-size: 12px;         /* 调整字体大小 */
        line-height: 1.2;        /* 调整行高 */
        border-radius: 3px;      /* 可选：调整圆角 */
    }
  }
  </style>