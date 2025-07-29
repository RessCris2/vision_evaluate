
  // 将 Base64 数据转换为 Blob 对象
export function base64ToBlob(base64Data) {
    const byteCharacters = atob(base64Data.split(',')[1]);  // 去掉前缀部分 (data:image/png;base64,)
    const byteArrays = [];
    
    // 将 Base64 转换为字节数组
    for (let offset = 0; offset < byteCharacters.length; offset += 1024) {
        const slice = byteCharacters.slice(offset, offset + 1024);
        const byteNumbers = new Array(slice.length);
        
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }
        
        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }
    
    return new Blob(byteArrays, { type: 'image/png' });  // 可以根据实际图片类型设置 mimeType
}
