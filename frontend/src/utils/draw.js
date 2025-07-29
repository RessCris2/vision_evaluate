
// 创建多边形
export  function createPolygon(canvas, points, scale, fillColor = 'rgba(255, 0, 0, 0.5)') {
    const ctx = canvas.getContext('2d');
    ctx.beginPath();
    // console.log('points:', points);
    points.forEach((point, index) => {
        const x = point[0] * scale.x;
        const y = point[1] * scale.y;
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.closePath();
    ctx.fillStyle = fillColor;
    ctx.fill();
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 1;
    ctx.stroke();
}


// 绘制图像和多边形
export function drawImageAndPolygons(canvas, imgSrc, initialWidth, initialHeight, jsonData, showIndexList, highlightedPolygonIndex, fillColor='rgba(155,111, 0, 0.5)') {
    const ctx = canvas.getContext('2d');
    const image = new Image();
    // image.src = 'testcat.jpg';
    image.src = imgSrc;
    
    
    image.onload = () => {
        console.log('drawImageAndPolygons');
        const scale = getScale(canvas, initialWidth, initialHeight);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

        // 绘制多边形
        jsonData.shapes.forEach((shape, index) => {
            if (showIndexList.includes(index)) {
            const color = index === highlightedPolygonIndex.value ? 'rgba(111, 233, 144, 0.5)' : fillColor; // 高亮颜色
            createPolygon(canvas, shape.points, scale, color);
            }
        });
    };
    image.onerror = () => {
        console.error("Failed to load image from: " + imgSrc.value);
    };
}


export function drawImageAndPolygonsAndTables(config){
    const {  
        canvas,  
        imgSrc,  
        initialWidth,  
        initialHeight,  
        jsonData,  
        showIndexList,  
        highlightedPolygonIndex=[],  
        area_min,
        area_max,
        fillColor = ['rgba(155,111, 0, 0.5)'] // 默认填充颜色  
    } = config;
    const ctx = canvas.getContext('2d');
    const image = new Image();
    // image.src = 'testcat.jpg';
    image.src = imgSrc;
    // let highlightedPolygonIndex = -1;
    
    
    image.onload = () => {
        console.log('drawImageAndPolygons');
        const scale = getScale(canvas, initialWidth, initialHeight);
        // canvas.width = canvas.clientWidth;
        // canvas.height = canvas.clientHeight;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
        // ctx.drawImage(image, 0, 0, canvas.clientWidth, canvas.clientHeight);

        console.log('showIndexList:', showIndexList);
        // 绘制多边形
        jsonData.shapes.forEach((shape, index) => {
            // 添加面积区间过滤条件
            const isInAreaRange = shape.area >= area_min && shape.area <= area_max;
            if (showIndexList.includes(index) && isInAreaRange) {
            const color = highlightedPolygonIndex.includes(index) ?  'rgba(111, 233, 144, 0.5)': fillColor[shape.cls_id] ; // 高亮颜色
            createPolygon(canvas, shape.points, scale, color);
            }
        });
    }
    // image.onerror = () => {
    //     console.error("Failed to load image from: " + imgSrc.value);
    // };
    const tableData = jsonData.shapes.map((shape, index) => {
        return {
            index: index + 1,
            pred: shape.label,
            true: shape.label,
        };
    });
    return tableData
}

// 获取缩放比例
export function getScale(canvas, initialWidth, initialHeight) {
    const scaleX = canvas.width / initialWidth;
    const scaleY = canvas.height / initialHeight;
    return { x: scaleX, y: scaleY };
}

// 窗口大小变化时调整 canvas
export function resizeCanvas(canvas, imgSrc,initialWidth, initialHeight, jsonData, showIndexList, highlightedPolygonIndex ) {
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
    drawImageAndPolygons(canvas, imgSrc,initialWidth, initialHeight, jsonData, showIndexList, highlightedPolygonIndex);
}


// 判断点击是否在多边形内
export function isPointInPolygon(x, y, points, scale) {
    const scaledPoints = points.map(point => [point[0] * scale.x, point[1] * scale.y]);
    let inside = false;
    for (let i = 0, j = scaledPoints.length - 1; i < scaledPoints.length; j = i++) {
        const xi = scaledPoints[i][0], yi = scaledPoints[i][1];
        const xj = scaledPoints[j][0], yj = scaledPoints[j][1];
        const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

// 绘制图片到 canvas
export const drawImageOnCanvas = (canvas, image) => {
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.src = image;
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height); // 清空画布
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height); // 绘制图片
    };
  };




/**
 * 
 * @param stateConfig 一个对象，包含以下属性
 * {
 * canvas: canvas,
 * imgSrc: imgSrc,
 * initialWidth: initialWidth,
 * initialHeight: initialHeight,
 * jsonPred: 预测数据,
 * jsonTrue: 真实数据,
 * predShowIndexList: 预测显示的多边形索引,
 * trueShowIndexList: 真实显示的多边形索引,
 * // highlightedPolygonIndex: highlightedPolygonIndex, // 高亮index
 * fillColor: fillColor
 * 
 * }
 * 
 */
export function CreateDraw(stateConfig){
    this.canvas = stateConfig.canvas;
    this.imgSrc = stateConfig.imgSrc;
    this.initialWidth = stateConfig.initialWidth;
    this.initialHeight = stateConfig.initialHeight;
    this.jsonPred = stateConfig.jsonPred;
    this.jsonTrue = stateConfig.jsonTrue;
    
    this.predShowIndexList = stateConfig.predShowIndexList; // predIds
    this.trueShowIndexList = stateConfig.trueShowIndexList; // trueIds
    this.unmatchedPredIds = stateConfig.unmatchedPredIds;
    this.unmatchedTrueIds = stateConfig.unmatchedTrueIds;
    this.matchedPredIds = stateConfig.matchedPredIds;
    this.matchedTrueIds = stateConfig.matchedTrueIds;

    // this.highlightedPolygonIndex = stateConfig.highlightedPolygonIndex; // 高亮index
    this.fillColor = stateConfig.fillColor;
    this.area_min = stateConfig.area_min;
    this.area_max = stateConfig.area_max;



    this.getScale = function(){
        const scaleX = this.canvas.clientwidth / this.initialWidth;
        const scaleY = this.canvas.clientHeight / this.initialHeight;
        return { x: scaleX, y: scaleY };
    };

    this.resizeCanvas = function(){
        this.canvas.width = this.canvas.clientWidth;
        this.canvas.height = this.canvas.clientHeight;
        this.drawWholePreds();
    };

    this.drawWholePreds = function(){
        const config = {
            canvas: this.canvas,
            imgSrc: this.imgSrc,
            initialWidth: this.initialWidth,
            initialHeight: this.initialHeight,
            jsonData: this.jsonPred,
            showIndexList: this.predShowIndexList,
            highlightedPolygonIndex: this.matchedPredIds,
            fillColor: this.fillColor,
            area_min: this.area_min,
            area_max: this.area_max

        };
        drawImageAndPolygonsAndTables(config);
    }

    this.drawWholeTrues = function(){
        const config = {
            canvas: this.canvas,
            imgSrc: this.imgSrc,
            initialWidth: this.initialWidth,
            initialHeight: this.initialHeight,
            jsonData: this.jsonTrue,
            showIndexList: this.trueShowIndexList,
            highlightedPolygonIndex: this.matchedTrueIds,
            fillColor: this.fillColor,
            area_min: this.area_min,
            area_max: this.area_max
        };
        drawImageAndPolygonsAndTables(config);
    }


    this.drawUnmatchedPreds = function(){
        const config = {
            canvas: this.canvas,
            imgSrc: this.imgSrc,
            initialWidth: this.initialWidth,
            initialHeight: this.initialHeight,
            jsonData: this.jsonPred,
            showIndexList: this.unmatchedPredIds,
            // highlightedPolygonIndex: this.highlightedPolygonIndex,
            fillColor: this.fillColor,
            area_min: this.area_min,
            area_max: this.area_max
        };
        drawImageAndPolygonsAndTables(config);
    }
    
    this.drawUnmatchedTrues = function(){
        const config = {
                canvas: this.canvas,
                imgSrc: this.imgSrc,
                initialWidth: this.initialWidth,
                initialHeight: this.initialHeight,
                jsonData: this.jsonTrue,
                showIndexList: this.unmatchedTrueIds,
                // highlightedPolygonIndex: this.highlightedPolygonIndex,
                fillColor: this.fillColor,
                area_min: this.area_min,
                area_max: this.area_max
            };
            drawImageAndPolygonsAndTables(config);
        }
    
    
    // 重点改造对象
    this.drawMatchedPairs = function(){
        console.log('matchedPairs:', this.matchedPredIds);
        const config = {
            canvas: this.canvas,
            imgSrc: this.imgSrc,
            initialWidth: this.initialWidth,
            initialHeight: this.initialHeight,
            // jsonData: this.jsonPred,
            // showIndexList: this.matchedPredIds,

            jsonData: this.jsonTrue,
            showIndexList: this.matchedTrueIds,
            // highlightedPolygonIndex: this.highlightedPolygonIndex,
            fillColor: this.fillColor,
            area_min: this.area_min,
            area_max: this.area_max
        };
        drawImageAndPolygonsAndTables(config);
    }

    this.drawImageOnCanvas = function(){
        drawImageOnCanvas(this.canvas, this.imgSrc);
    }

}


export function switchSelect(drawInst, type){
    switch(type){
        case 'original_img':
            drawInst.drawImageOnCanvas();
            break;

        case 'wholePreds':
            drawInst.drawWholePreds();
            break;
        case 'wholeTrue':
            drawInst.drawWholeTrues();
            break;
        case 'unmatchedPreds':
            drawInst.drawUnmatchedPreds();
            break;
        case 'unmatchedTrues':
            drawInst.drawUnmatchedTrues();
            break;
        case 'matchedPairs':
            drawInst.drawMatchedPairs();
            break;
        default:
            console.error('Invalid type:', type);
    }
}


// export const isPointInPolygon = (point, vertices) => {
//     let [px, py] = point;
//     let inside = false;

//     for (let i = 0, j = vertices.length - 1; i < vertices.length; j = i++) {
//         const [xi, yi] = vertices[i];
//         const [xj, yj] = vertices[j];

//         const intersect =
//             yi > py !== yj > py &&
//             px < ((xj - xi) * (py - yi)) / (yj - yi) + xi;

//         if (intersect) inside = !inside;
//     }

//     return inside;
// };
