import { createRouter, createWebHistory } from 'vue-router';
import predictResult from '../components/predictResult.vue';
import EvaluateTable from '../components/evaluateTable.vue';
import EvalPredict from '../views/EvalPredict.vue';
import AreaQuantile from '@/views/AreaQuantile.vue';
import AreaChart from '@/components/Charts.vue';
import drawResult from '@/components/drawResult.vue';
// import Chart from 'vue-echarts';

const routes = [
  {
    path: '/area',
    name: 'AreaChart',
    component: AreaChart,
  },
  {
    path: '/cut',
    name: 'AreaQuantile',
    component: AreaQuantile,
  },
  {
    path: '/',
    name: 'EvalPredict',
    component: EvalPredict,
  },
];

const router = createRouter({
  history: createWebHistory("/"),
  routes,
});

export default router;
