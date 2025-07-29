
export const options = [  
    {value: 'secondary_particle', label: '二次颗粒', children: [{value: 'big', label: '大颗粒'}, {value: 'small', label: '小颗粒'}, {value: 'cont', label: '连续式'}, {value: 'powder_material', label: '粉体'},{value: 'powder_material_big', label: '粉体-大颗粒'},{value: 'ferro', label: '磷铁'},
        {value: 'cyto', label: 'cyto'}, {value: 'cyto2', label: 'cyto2'}, {value: 'CP', label: 'CP'}, {value: 'CP2', label: 'CP2'}
        ]},  
    {value: 'primary_particle', label: '一次颗粒', children: [{value: 'needle', label: '针状'}, {value: 'strip', label: '条状'}, {value: 'plate', label: '板状'}]},  
    // {value: 'cracking_ball', label: '开裂球', children: [{value: 'big', label: '大颗粒'}, {value: 'cont', label: '连续式'}]},  
    {value: 'micro_powder', label: '微粉', children: [{value: 'big', label: '大颗粒'}, {value: 'small', label: '小颗粒'},]}  
];

// export const options_ch = [  
//     {value: '二次颗粒', label: '二次颗粒', children: [
//       {value: '粉体', label: '粉体'},
//         {value: '粉体-大颗粒', label: '粉体-大颗粒'},
//         {value: '磷铁', label: '磷铁'},
//         {value: '单晶', label: '单晶'},
//         {value: '多晶', label: '多晶'},
//         {value: '大颗粒', label: '大颗粒'}, 
//         {value: '小颗粒', label: '小颗粒'}, 
//         {value: '连续式', label: '连续式'}, 
        
//         {value: 'cyto', label: 'cyto'}, 
//         {value: 'cyto2', label: 'cyto2'}, 
//         {value: 'CP', label: 'CP'}, 
//         {value: 'CP2', label: 'CP2'}
//     ]},  
//     {value: '一次颗粒', label: '一次颗粒', children: [
//         {value: '针状', label: '针状'}, 
//         {value: '条状', label: '条状'}, 
//         {value: '板状', label: '板状'}
//     ]},  
//     {value: '微粉', label: '微粉', children: [
//         {value: '大颗粒', label: '大颗粒'}, 
//         {value: '小颗粒', label: '小颗粒'}
//     ]}  
// ];
export const options_ch = [
  {
    value: '二次颗粒',
    label: '二次颗粒',
    children: [
      {
        value: '镍系',
        label: '镍系',
        children: [
          { value: '大颗粒', label: '大颗粒' },
          { value: '小颗粒', label: '小颗粒' },
          { value: '连续式', label: '连续式' },
          { value: 'cyto', label: 'cyto' },
          { value: 'cyto2', label: 'cyto2' },
          { value: 'CP', label: 'CP' },
          { value: 'CP2', label: 'CP2' }
        ]
      },
       {
        value: '磷系',
        label: '磷系',
        children: [
          { value: '粉体', label: '粉体' },
          { value: '粉体-大颗粒', label: '粉体-大颗粒' },
          { value: '磷铁', label: '磷铁' },
        ]
      },
      {
        value: '前沿所',
        label: '前沿所',
        children: [
          { value: '单晶', label: '单晶' },
          { value: '多晶', label: '多晶' },
          { value: 'cyto', label: 'cyto' },
          { value: 'cyto2', label: 'cyto2' },
        ]
      }
    ]
  },
  {
    value: '一次颗粒',
    label: '一次颗粒',
    children: [
      {
        value: '镍系',
        label: '镍系',
        children: [
          { value: '针状', label: '针状' },
          { value: '条状', label: '条状' },
          { value: '板状', label: '板状' }
        ]
      },
    ]
     
  },
  {
    value: '微粉',
    label: '微粉',
    children: [
      {
        value: '镍系',
        label: '镍系',
        children: [
          { value: '大颗粒', label: '大颗粒' },
          { value: '小颗粒', label: '小颗粒' }
        ]
      },
    ]
  },
  {
    value: '开裂球',
    label: '开裂球',
    children: [
      {
        value: '镍系',
        label: '镍系',
        children: [
          { value: '大颗粒', label: '大颗粒' },
          { value: '连续式', label: '连续式' }
        ]
      },
    ]
  }
];

const envSuffix = import.meta.env.MODE === 'production' ? '' : (import.meta.env.MODE === 'test' ? '-test' : '-dev');
export const predict_options = [
  { value: `ai${envSuffix}`, label: 'AI计算平台测试' },
  { value: `common${envSuffix}`, label: '中伟测试' },
  { value: `opton${envSuffix}`, label: '欧波同测试' },
  ];

export const select_options = [
    { value: 'original_img', label: '原图' },
    { value: 'wholePreds', label: '所有预测实例' },
    { value: 'wholeTrue', label: '所有真实实例' },
    { value: 'matchedPairs', label: '配对的实例' },
    { value: 'unmatchedPreds', label: '未匹配的预测实例' },
    { value: 'unmatchedTrues', label: '未匹配的真实实例' }
  ];
  


