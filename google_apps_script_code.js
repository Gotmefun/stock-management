/**
 * Google Apps Script for Stock Management Image Upload
 * รองรับการอัปโหลดรูปภาพไปยัง Google Drive ตามสาขา
 * 
 * จุดประสงค์:
 * 1. รับรูปภาพ base64 จาก web app
 * 2. สร้างโฟลเดอร์ตามสาขา (สาขาตัวเมือง, สาขาหน้าโรงเรียน, สาขาโป่งไผ่)
 * 3. บันทึกรูปภาพใน Google Drive
 * 4. ส่งลิงก์กลับไปให้ web app
 */

function doPost(e) {
  try {
    console.log('=== Starting doPost ===');
    
    // Parse request data
    let requestData;
    try {
      const postData = e.postData.contents;
      requestData = JSON.parse(postData);
      console.log('Request data parsed successfully');
      console.log('Data keys:', Object.keys(requestData));
    } catch (parseError) {
      console.error('Error parsing request data:', parseError);
      return ContentService
        .createTextOutput(JSON.stringify({
          success: false,
          error: 'Invalid JSON data: ' + parseError.toString()
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Validate required fields
    const { imageData, filename, folder } = requestData;
    console.log('Folder requested:', folder);
    console.log('Filename:', filename);
    console.log('Image data length:', imageData ? imageData.length : 'undefined');
    
    if (!imageData || !filename || !folder) {
      console.error('Missing required fields');
      return ContentService
        .createTextOutput(JSON.stringify({
          success: false,
          error: 'Missing required fields: imageData, filename, or folder'
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Process image data
    let imageBlob;
    try {
      // Remove data URL prefix if present
      let cleanImageData = imageData;
      if (imageData.startsWith('data:')) {
        cleanImageData = imageData.split(',')[1];
      }
      
      // Convert base64 to blob
      const imageBytes = Utilities.base64Decode(cleanImageData);
      
      // Determine MIME type from filename or default to JPEG
      let mimeType = 'image/jpeg';
      if (filename.toLowerCase().endsWith('.png')) {
        mimeType = 'image/png';
      } else if (filename.toLowerCase().endsWith('.gif')) {
        mimeType = 'image/gif';
      } else if (filename.toLowerCase().endsWith('.webp')) {
        mimeType = 'image/webp';
      }
      
      imageBlob = Utilities.newBlob(imageBytes, mimeType, filename);
      console.log('Image blob created successfully');
      console.log('MIME type:', mimeType);
      
    } catch (imageError) {
      console.error('Error processing image data:', imageError);
      return ContentService
        .createTextOutput(JSON.stringify({
          success: false,
          error: 'Error processing image: ' + imageError.toString()
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Create or get folder
    let targetFolder;
    try {
      targetFolder = createFolderPath(folder);
      console.log('Target folder ID:', targetFolder.getId());
      console.log('Target folder name:', targetFolder.getName());
    } catch (folderError) {
      console.error('Error creating folder:', folderError);
      return ContentService
        .createTextOutput(JSON.stringify({
          success: false,
          error: 'Error creating folder: ' + folderError.toString()
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Upload file to Google Drive
    let uploadedFile;
    try {
      // Check if file with same name already exists
      const existingFiles = targetFolder.getFilesByName(filename);
      if (existingFiles.hasNext()) {
        // File exists, create a unique name
        const timestamp = new Date().getTime();
        const nameParts = filename.split('.');
        const extension = nameParts.pop();
        const baseName = nameParts.join('.');
        const uniqueFilename = `${baseName}_${timestamp}.${extension}`;
        imageBlob.setName(uniqueFilename);
        console.log('File exists, using unique name:', uniqueFilename);
      }
      
      uploadedFile = targetFolder.createFile(imageBlob);
      console.log('File uploaded successfully');
      console.log('File ID:', uploadedFile.getId());
      
      // Set file permissions to public readable
      uploadedFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      console.log('File permissions set to public readable');
      
    } catch (uploadError) {
      console.error('Error uploading file:', uploadError);
      return ContentService
        .createTextOutput(JSON.stringify({
          success: false,
          error: 'Error uploading file: ' + uploadError.toString()
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Return success response
    const response = {
      success: true,
      fileId: uploadedFile.getId(),
      filename: uploadedFile.getName(),
      webViewLink: uploadedFile.getUrl(),
      downloadLink: `https://drive.google.com/uc?id=${uploadedFile.getId()}`,
      folder: folder,
      folderId: targetFolder.getId()
    };
    
    console.log('=== Upload completed successfully ===');
    console.log('Response:', JSON.stringify(response, null, 2));
    
    return ContentService
      .createTextOutput(JSON.stringify(response))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('=== Unexpected error in doPost ===');
    console.error('Error:', error);
    console.error('Stack trace:', error.stack);
    
    return ContentService
      .createTextOutput(JSON.stringify({
        success: false,
        error: 'Unexpected error: ' + error.toString(),
        stack: error.stack
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * สร้างโฟลเดอร์ตาม path ที่กำหนด
 * รองรับการสร้างโฟลเดอร์ซ้อนกัน
 */
function createFolderPath(folderPath) {
  try {
    console.log('Creating folder path:', folderPath);
    
    // Split path and clean up
    const pathParts = folderPath.split('/').filter(part => part.trim() !== '');
    console.log('Path parts:', pathParts);
    
    let currentFolder = DriveApp.getRootFolder();
    
    for (let i = 0; i < pathParts.length; i++) {
      const folderName = pathParts[i].trim();
      console.log(`Processing folder part ${i + 1}/${pathParts.length}: "${folderName}"`);
      
      // Check if folder exists
      const existingFolders = currentFolder.getFoldersByName(folderName);
      
      if (existingFolders.hasNext()) {
        // Folder exists, use it
        currentFolder = existingFolders.next();
        console.log('Found existing folder:', folderName);
      } else {
        // Folder doesn't exist, create it
        currentFolder = currentFolder.createFolder(folderName);
        console.log('Created new folder:', folderName);
      }
      
      console.log('Current folder ID:', currentFolder.getId());
    }
    
    console.log('Final folder path created successfully');
    console.log('Final folder ID:', currentFolder.getId());
    console.log('Final folder name:', currentFolder.getName());
    
    return currentFolder;
    
  } catch (error) {
    console.error('Error in createFolderPath:', error);
    throw new Error('Failed to create folder path: ' + error.toString());
  }
}

/**
 * Test function สำหรับทดสอบการทำงาน
 */
function testImageUpload() {
  console.log('=== Testing Image Upload ===');
  
  // Create a simple test image (1x1 red pixel PNG)
  const testImageBase64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==';
  
  const testData = {
    imageData: 'data:image/png;base64,' + testImageBase64,
    filename: 'test_upload.png',
    folder: 'Check Stock Project/สาขาตัวเมือง'
  };
  
  // Simulate POST request
  const mockRequest = {
    postData: {
      contents: JSON.stringify(testData)
    }
  };
  
  try {
    const result = doPost(mockRequest);
    const response = JSON.parse(result.getContent());
    
    console.log('Test result:');
    console.log(JSON.stringify(response, null, 2));
    
    if (response.success) {
      console.log('✅ Test passed!');
      console.log('File URL:', response.webViewLink);
    } else {
      console.log('❌ Test failed:', response.error);
    }
    
  } catch (error) {
    console.error('❌ Test error:', error);
  }
}

/**
 * Test function สำหรับทดสอบการสร้างโฟลเดอร์
 */
function testFolderCreation() {
  console.log('=== Testing Folder Creation ===');
  
  const testPaths = [
    'Check Stock Project/สาขาตัวเมือง',
    'Check Stock Project/สาขาหน้าโรงเรียน', 
    'Check Stock Project/สาขาโป่งไผ่'
  ];
  
  testPaths.forEach(path => {
    try {
      console.log(`\nTesting path: ${path}`);
      const folder = createFolderPath(path);
      console.log(`✅ Success: ${folder.getName()} (ID: ${folder.getId()})`);
    } catch (error) {
      console.log(`❌ Failed: ${error.toString()}`);
    }
  });
}

/**
 * Utility function สำหรับ cleanup test files
 */
function cleanupTestFiles() {
  console.log('=== Cleaning up test files ===');
  
  try {
    // Find Check Stock Project folder
    const rootFolders = DriveApp.getFoldersByName('Check Stock Project');
    
    if (rootFolders.hasNext()) {
      const checkStockFolder = rootFolders.next();
      console.log('Found Check Stock Project folder');
      
      // List all files in subfolders
      const subFolders = checkStockFolder.getFolders();
      while (subFolders.hasNext()) {
        const subFolder = subFolders.next();
        console.log(`\nChecking folder: ${subFolder.getName()}`);
        
        const files = subFolder.getFiles();
        while (files.hasNext()) {
          const file = files.next();
          if (file.getName().startsWith('test_')) {
            console.log(`Deleting test file: ${file.getName()}`);
            file.setTrashed(true);
          }
        }
      }
      
      console.log('✅ Cleanup completed');
      
    } else {
      console.log('Check Stock Project folder not found');
    }
    
  } catch (error) {
    console.error('❌ Cleanup error:', error);
  }
}