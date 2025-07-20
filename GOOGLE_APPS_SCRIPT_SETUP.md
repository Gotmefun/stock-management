# Google Apps Script Setup สำหรับอัปโหลดรูปภาพ

## ขั้นตอนการตั้งค่า:

### 1. สร้าง Google Apps Script
1. ไปที่ https://script.google.com
2. คลิก "New Project"
3. ตั้งชื่อ "Stock Image Uploader"

### 2. ใส่โค้ด Google Apps Script

```javascript
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    
    // รับ base64 image data
    var base64Data = data.imageData.split(',')[1]; // Remove data:image/jpeg;base64,
    var filename = data.filename || 'stock_image.jpg';
    var folderId = '1N7qa43TTh-iCQFz-fSY9PwEq9-oMRZDR'; // Pic Stock Counting folder ID
    
    // แปลง base64 เป็น blob
    var blob = Utilities.newBlob(Utilities.base64Decode(base64Data), 'image/jpeg', filename);
    
    // หา folder
    var folder = DriveApp.getFolderById(folderId);
    
    // สร้างไฟล์
    var file = folder.createFile(blob);
    
    // กำหนด permission ให้ดูได้
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    
    return ContentService
      .createTextOutput(JSON.stringify({
        success: true,
        fileId: file.getId(),
        webViewLink: file.getUrl(),
        filename: filename
      }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({
        success: false,
        error: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

### 3. Deploy as Web App
1. คลิก "Deploy" → "New deployment"
2. Type: Web app
3. Execute as: Me
4. Who has access: Anyone
5. คลิก "Deploy"
6. คัดลอก Web app URL

### 4. อัปเดตโค้ด Python
ใส่ Web app URL ใน app.py เพื่อส่ง HTTP POST ไปที่ Google Apps Script

Web app URL จะมีลักษณะ:
`https://script.google.com/macros/s/[SCRIPT_ID]/exec`