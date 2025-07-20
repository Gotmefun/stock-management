# Google Apps Script สำหรับอัปโหลดรูป

## ขั้นตอนที่ 1: สร้าง Apps Script

1. ไปที่ https://script.google.com
2. คลิก "New project"
3. ลบโค้ดเดิม แล้วใส่โค้ดนี้:

```javascript
function doPost(e) {
  try {
    Logger.log('Received request');
    
    // Parse JSON data
    const data = JSON.parse(e.postData.contents);
    const imageData = data.imageData;
    const filename = data.filename || 'stock_image.jpg';
    
    Logger.log('Processing image: ' + filename);
    
    // Remove data URL prefix if present
    let base64Data = imageData;
    if (base64Data.indexOf('data:') === 0) {
      base64Data = base64Data.split(',')[1];
    }
    
    // Convert base64 to blob
    const imageBlob = Utilities.base64Decode(base64Data);
    const blob = Utilities.newBlob(imageBlob, 'image/jpeg', filename);
    
    // Get or create folders
    const checkStockFolder = getOrCreateFolder('Check Stock Project', DriveApp.getRootFolder());
    const picFolder = getOrCreateFolder('Pic Stock Counting', checkStockFolder);
    
    // Upload file
    const file = picFolder.createFile(blob);
    
    // Make file publicly viewable
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    
    Logger.log('Upload successful: ' + file.getId());
    
    return ContentService
      .createTextOutput(JSON.stringify({
        success: true,
        fileId: file.getId(),
        webViewLink: file.getUrl(),
        filename: filename
      }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    return ContentService
      .createTextOutput(JSON.stringify({
        success: false,
        error: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function getOrCreateFolder(folderName, parentFolder) {
  const folders = parentFolder.getFoldersByName(folderName);
  if (folders.hasNext()) {
    return folders.next();
  } else {
    return parentFolder.createFolder(folderName);
  }
}
```

## ขั้นตอนที่ 2: Deploy Apps Script

1. คลิก "Deploy" > "New deployment"
2. เลือก type: "Web app"
3. Execute as: "Me"
4. Who has access: "Anyone"
5. คลิก "Deploy"
6. Copy Web app URL

## ขั้นตอนที่ 3: Update App

ใส่ URL ที่ได้ใน environment variable หรือโค้ด