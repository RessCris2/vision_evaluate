<template>
    <div>
        <predictResult />
        <hr style="margin: 20px 0;" />
        <evaluateTable />
        <hr style="margin: 20px 0;" />
        <DrawResult />
    </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import predictResult from '../components/predictResult.vue'
import evaluateTable from '../components/evaluateTable.vue'
import DrawResult from '../components/drawResult.vue'
</script>

<!-- <style scoped>
div {
    display: flex;
    flex-direction: column;
}
</style> -->
