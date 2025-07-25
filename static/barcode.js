let html5QrCode;
let cameraId;
let isScanning = false;
let stream;
let recentScans = [];
let deferredPrompt;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    registerServiceWorker();
});

// Register Service Worker for PWA
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/static/sw.js')
                .then(function(registration) {
                    console.log('ServiceWorker registration successful:', registration.scope);
                    
                    // Check for updates
                    registration.addEventListener('updatefound', () => {
                        const newWorker = registration.installing;
                        newWorker.addEventListener('statechange', () => {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                // New content is available, refresh to update
                                if (confirm('มีการอัปเดทใหม่ ต้องการรีเฟรชหน้าเว็บหรือไม่?')) {
                                    window.location.reload();
                                }
                            }
                        });
                    });
                })
                .catch(function(error) {
                    console.log('ServiceWorker registration failed:', error);
                });
        });
    } else {
        console.log('Service Worker not supported');
    }
    
    // Handle PWA install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
        console.log('PWA install prompt triggered');
        console.log('Event details:', e);
        e.preventDefault();
        deferredPrompt = e;
        console.log('deferredPrompt saved:', !!deferredPrompt);
        showInstallPrompt();
    });
    
    // Handle successful app installation
    window.addEventListener('appinstalled', (evt) => {
        console.log('PWA was installed');
        showAlert('✅ แอปถูกติดตั้งเรียบร้อย!', 'success');
    });
}

// Show PWA install prompt
function showInstallPrompt() {
    // Only show install button for admin users
    if (window.sessionData && window.sessionData.role !== 'admin') {
        return;
    }
    
    // Create install button if not exists
    if (!document.getElementById('pwa-install-btn')) {
        const installButton = document.createElement('button');
        installButton.id = 'pwa-install-btn';
        installButton.className = 'camera-btn';
        installButton.style.background = '#28a745';
        installButton.innerHTML = '📱 ติดตั้งแอป';
        installButton.onclick = installPWA;
        
        // Add to camera controls
        const cameraControls = document.querySelector('.camera-controls');
        if (cameraControls) {
            cameraControls.parentNode.appendChild(installButton);
        }
    }
}

// Install PWA
function installPWA() {
    console.log('installPWA function called');
    console.log('deferredPrompt available:', !!deferredPrompt);
    
    const installButton = document.getElementById('pwa-install-btn');
    
    if (deferredPrompt) {
        console.log('Using deferred prompt');
        // Use the deferred prompt if available
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            console.log('User choice:', choiceResult.outcome);
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the PWA install prompt');
                showAlert('✅ แอปถูกติดตั้งเรียบร้อย!', 'success');
                if (installButton) installButton.style.display = 'none';
            } else {
                console.log('User dismissed the PWA install prompt');
                showAlert('❌ การติดตั้งถูกยกเลิก', 'warning');
            }
            deferredPrompt = null;
        });
    } else {
        console.log('No deferred prompt available, showing instructions');
        // Check if already installed
        if (window.navigator.standalone === true || window.matchMedia('(display-mode: standalone)').matches) {
            showAlert('✅ แอปถูกติดตั้งไว้แล้ว!', 'success');
        } else {
            // Show instructions if no prompt available
            showAlert('📱 วิธีติดตั้งแอป:\n• Chrome: กดเมนู 3 จุด → "ติดตั้งแอป"\n• Safari: กด Share Icon → "เพิ่มไปยังหน้าจอหลัก"\n• Firefox: กดเมนู → "ติดตั้งแอป"', 'info');
        }
    }
}

function initializeApp() {
    // Initialize barcode form
    document.getElementById('stock-form').addEventListener('submit', handleSubmit);
    
    // Initialize camera controls
    document.getElementById('start-camera').addEventListener('click', startCamera);
    document.getElementById('take-photo').addEventListener('click', takePhoto);
    document.getElementById('retake-photo').addEventListener('click', retakePhoto);
    document.getElementById('test-upload')?.addEventListener('click', testUpload);
    document.getElementById('authorize-drive')?.addEventListener('click', authorizeDrive);
    document.getElementById('check-drive-status')?.addEventListener('click', checkDriveStatus);
    document.getElementById('pwa-install-btn')?.addEventListener('click', installPWA);
    
    // Initialize barcode input change (both input and change events)
    document.getElementById('barcode').addEventListener('input', handleBarcodeChange);
    document.getElementById('barcode').addEventListener('change', handleBarcodeChange);
    
    // Load recent scans from localStorage
    loadRecentScans();
}


function toggleScanner() {
    const button = document.getElementById('scanner-toggle');
    const qrReader = document.getElementById('qr-reader');
    
    if (!isScanning) {
        startScanner();
        button.textContent = 'ปิดกล้อง';
        button.classList.add('stop');
        qrReader.style.display = 'block';
        isScanning = true;
    } else {
        stopScanner();
        button.textContent = 'เปิดกล้อง';
        button.classList.remove('stop');
        qrReader.style.display = 'none';
        isScanning = false;
    }
}

function startScanner() {
    html5QrCode = new Html5Qrcode("qr-reader");
    
    Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length) {
            // Try to find back camera first
            let backCamera = devices.find(device => 
                device.label.toLowerCase().includes('back') || 
                device.label.toLowerCase().includes('rear') ||
                device.label.toLowerCase().includes('environment')
            );
            
            cameraId = backCamera ? backCamera.id : devices[devices.length - 1].id;
            
            html5QrCode.start(
                cameraId,
                {
                    fps: 10,
                    qrbox: { width: 250, height: 250 },
                    facingMode: "environment" // Force back camera
                },
                onScanSuccess,
                onScanFailure
            ).catch(err => {
                console.error('Error starting camera:', err);
                showAlert('ไม่สามารถเข้าถึงกล้องได้', 'error');
            });
        }
    }).catch(err => {
        console.error('Error getting cameras:', err);
        showAlert('ไม่พบกล้องในอุปกรณ์', 'error');
    });
}

function stopScanner() {
    if (html5QrCode) {
        html5QrCode.stop().then(ignore => {
            html5QrCode.clear();
        }).catch(err => {
            console.error('Error stopping scanner:', err);
        });
    }
}

function onScanSuccess(decodedText, decodedResult) {
    document.getElementById('barcode').value = decodedText;
    handleBarcodeChange();
    
    // Auto-stop scanner after successful scan
    toggleScanner();
}

function onScanFailure(error) {
    // Handle scan failure silently
}

function handleBarcodeChange() {
    const barcode = document.getElementById('barcode').value.trim();
    
    if (barcode) {
        fetchProductInfo(barcode);
    } else {
        hideProductInfo();
    }
}

function fetchProductInfo(barcode) {
    fetch(`/get_product/${barcode}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(`ไม่พบสินค้าที่มีบาร์โค้ด: ${barcode}`, 'error');
                hideProductInfo();
            } else {
                showProductInfo(data);
            }
        })
        .catch(error => {
            console.error('Error fetching product:', error);
            showAlert('เกิดข้อผิดพลาดในการค้นหาสินค้า', 'error');
        });
}

function showProductInfo(product) {
    // Handle both API response formats: product.name or product.product_name
    const productName = product.name || product.product_name || 'ชื่อสินค้าไม่ระบุ';
    document.getElementById('product-name').textContent = productName;
    document.getElementById('product-barcode').textContent = product.barcode;
    document.getElementById('product-info').style.display = 'block';
    
    // Show duplicate warning if exists
    if (product.duplicate_warning) {
        const warning = product.duplicate_warning;
        let warningMsg = `${warning.message}<br><small>${warning.details}`;
        
        // Add date info if available
        if (warning.date_info) {
            warningMsg += `<br>${warning.date_info}`;
        }
        
        warningMsg += `</small>`;
        
        // Show warning alert
        showAlert(warningMsg, 'warning');
        
        // Also log to console
        console.log('Duplicate count warning:', warning);
    }
}

function hideProductInfo() {
    document.getElementById('product-info').style.display = 'none';
}

function startCamera() {
    const video = document.getElementById('video');
    const startButton = document.getElementById('start-camera');
    const takeButton = document.getElementById('take-photo');
    
    // Try back camera first, fallback to any camera
    const constraints = [
        { video: { facingMode: "environment" } }, // Prefer back camera
        { video: { facingMode: "user" } }, // Front camera
        { video: true } // Any available camera
    ];
    
    async function tryCamera(constraintIndex = 0) {
        if (constraintIndex >= constraints.length) {
            showAlert('ไม่สามารถเข้าถึงกล้องได้', 'error');
            return;
        }
        
        try {
            console.log(`Trying camera constraint ${constraintIndex}:`, constraints[constraintIndex]);
            const mediaStream = await navigator.mediaDevices.getUserMedia(constraints[constraintIndex]);
            stream = mediaStream;
            video.srcObject = stream;
            video.style.display = 'block';
            startButton.disabled = true;
            takeButton.disabled = false;
            console.log(`Camera started successfully with constraint ${constraintIndex}`);
        } catch (err) {
            console.error(`Error with constraint ${constraintIndex}:`, err);
            console.error('Error details:', {
                name: err.name,
                message: err.message,
                constraint: constraints[constraintIndex]
            });
            // Try next constraint
            await new Promise(resolve => setTimeout(resolve, 100)); // Small delay before retry
            tryCamera(constraintIndex + 1);
        }
    }
    
    tryCamera();
}

function takePhoto() {
    console.log('takePhoto function called');
    
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const photo = document.getElementById('photo');
    const takeButton = document.getElementById('take-photo');
    const retakeButton = document.getElementById('retake-photo');
    const testUploadButton = document.getElementById('test-upload');
    
    console.log('Video dimensions:', video.videoWidth, 'x', video.videoHeight);
    
    if (video.videoWidth === 0 || video.videoHeight === 0) {
        console.error('Video not ready or no dimensions');
        return;
    }
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    console.log('Image data generated, length:', imageData.length);
    console.log('Image data preview:', imageData.substring(0, 50) + '...');
    
    photo.src = imageData;
    photo.style.display = 'block';
    video.style.display = 'none';
    
    takeButton.disabled = true;
    retakeButton.disabled = false;
    testUploadButton.disabled = false; // Enable test upload button
    
    console.log('Photo taken and UI updated');
    
    // Stop camera stream
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}

function retakePhoto() {
    const video = document.getElementById('video');
    const photo = document.getElementById('photo');
    const startButton = document.getElementById('start-camera');
    const takeButton = document.getElementById('take-photo');
    const retakeButton = document.getElementById('retake-photo');
    const testUploadButton = document.getElementById('test-upload');
    
    photo.style.display = 'none';
    video.style.display = 'none';
    
    startButton.disabled = false;
    takeButton.disabled = true;
    retakeButton.disabled = true;
    testUploadButton.disabled = true; // Disable test upload button
}

function handleSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const productNameFromBarcode = document.getElementById('product-name').textContent;
    const manualProductName = formData.get('manual_product_name');
    
    // Use manual product name if barcode product name is empty or default
    let finalProductName = productNameFromBarcode && productNameFromBarcode !== '' && productNameFromBarcode !== 'ชื่อสินค้าไม่ระบุ' 
        ? productNameFromBarcode 
        : manualProductName;
    
    const data = {
        barcode: formData.get('barcode'),
        quantity: parseInt(formData.get('quantity')),
        branch: formData.get('branch'),
        product_name: finalProductName,
        counter_name: formData.get('counter_name'),
        manual_product_name: manualProductName
    };
    
    // Debug logging
    console.log('Form data:', data);
    console.log('Product name element:', document.getElementById('product-name'));
    console.log('Product name text:', data.product_name);
    
    // Add image data if photo was taken
    const photo = document.getElementById('photo');
    console.log('Photo element:', photo);
    console.log('Photo src:', photo.src);
    console.log('Photo src starts with data:', photo.src && photo.src.startsWith('data:'));
    
    if (photo.src && photo.src.startsWith('data:')) {
        data.image_data = photo.src;
        console.log('Image data added, length:', photo.src.length);
    } else {
        console.log('No image data to add');
    }
    
    // Validate required fields
    if (!data.barcode || !data.quantity || !data.branch || !data.product_name) {
        console.log('Validation failed:', {
            barcode: !!data.barcode,
            quantity: !!data.quantity, 
            branch: !!data.branch,
            product_name: !!data.product_name,
            manual_product_name: !!data.manual_product_name
        });
        showAlert('กรุณากรอกข้อมูลให้ครบถ้วน (บาร์โค้ด, จำนวน, สาขา, และชื่อสินค้า)', 'error');
        return;
    }
    
    // Submit data
    submitStockData(data);
}

function submitStockData(data) {
    const submitButton = document.getElementById('submit-btn');
    const statusDiv = document.getElementById('submit-status');
    const statusMessage = document.getElementById('status-message');
    
    // Show loading status
    submitButton.disabled = true;
    submitButton.textContent = 'กำลังบันทึก...';
    showSubmitStatus('กำลังบันทึกข้อมูล...', 'loading');
    
    console.log('Submitting to server:', data);
    
    fetch('/submit_stock', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // Show success status with count info if available
            let successMsg = '✅ บันทึกข้อมูลสำเร็จ!';
            if (result.count_info) {
                successMsg += ` (${result.count_info})`;
            }
            showSubmitStatus(successMsg, 'success');
            
            // Add to recent scans
            addRecentScan(data);
            
            // Reset form after short delay
            setTimeout(() => {
                resetForm();
                hideSubmitStatus();
            }, 3000);
        } else {
            // Show error status
            const errorMsg = result.error || 'เกิดข้อผิดพลาดในการบันทึกข้อมูล';
            showSubmitStatus('❌ ' + errorMsg, 'error');
        }
    })
    .catch(error => {
        console.error('Error submitting data:', error);
        showSubmitStatus('❌ เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = 'บันทึกข้อมูล';
    });
}

function addRecentScan(data) {
    const scan = {
        barcode: data.barcode,
        product_name: data.product_name || data.manual_product_name || 'ไม่ระบุชื่อสินค้า',
        quantity: data.quantity,
        branch: data.branch,
        timestamp: new Date().toLocaleString('th-TH')
    };
    
    recentScans.unshift(scan);
    
    // Keep only last 10 scans
    if (recentScans.length > 10) {
        recentScans = recentScans.slice(0, 10);
    }
    
    // Save to localStorage
    localStorage.setItem('recentScans', JSON.stringify(recentScans));
    
    // Update display
    updateRecentScansDisplay();
}

function loadRecentScans() {
    const saved = localStorage.getItem('recentScans');
    if (saved) {
        recentScans = JSON.parse(saved);
        updateRecentScansDisplay();
    }
}

function updateRecentScansDisplay() {
    const container = document.getElementById('recent-scans-list');
    
    if (recentScans.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">ยังไม่มีการนับสต๊อก</p>';
        return;
    }
    
    container.innerHTML = recentScans.map(scan => `
        <div class="scan-item">
            <div class="scan-info">
                <h4>${scan.product_name}</h4>
                <p>บาร์โค้ด: ${scan.barcode} | สาขา: ${scan.branch}</p>
                <p>เวลา: ${scan.timestamp}</p>
            </div>
            <div class="scan-quantity">${scan.quantity}</div>
        </div>
    `).join('');
}

function resetForm() {
    document.getElementById('stock-form').reset();
    hideProductInfo();
    
    // Clear manual product name field
    document.getElementById('manual_product_name').value = '';
    
    // Reset camera
    const video = document.getElementById('video');
    const photo = document.getElementById('photo');
    const startButton = document.getElementById('start-camera');
    const takeButton = document.getElementById('take-photo');
    const retakeButton = document.getElementById('retake-photo');
    
    video.style.display = 'none';
    photo.style.display = 'none';
    startButton.disabled = false;
    takeButton.disabled = true;
    retakeButton.disabled = true;
    
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

function showAlert(message, type) {
    const container = document.getElementById('alert-container');
    container.innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;
    
    // Auto-hide after longer time for warnings (8 seconds)
    const hideDelay = type === 'warning' ? 8000 : 5000;
    setTimeout(() => {
        container.innerHTML = '';
    }, hideDelay);
}

function showSubmitStatus(message, type) {
    console.log('showSubmitStatus called:', message, type);
    const statusDiv = document.getElementById('submit-status');
    const statusMessage = document.getElementById('status-message');
    
    console.log('Status div found:', statusDiv);
    console.log('Status message found:', statusMessage);
    
    if (statusDiv && statusMessage) {
        statusMessage.textContent = message;
        statusDiv.className = 'submit-status ' + type + ' show';
        console.log('Status message displayed successfully');
        console.log('Final className:', statusDiv.className);
    } else {
        console.error('Status elements not found!');
    }
}

function hideSubmitStatus() {
    console.log('hideSubmitStatus called');
    const statusDiv = document.getElementById('submit-status');
    if (statusDiv) {
        statusDiv.className = 'submit-status';
        console.log('Status message hidden');
    } else {
        console.error('Status div not found for hiding!');
    }
}

function testUpload() {
    console.log('testUpload function called');
    
    const photo = document.getElementById('photo');
    const branchSelect = document.getElementById('branch');
    const testButton = document.getElementById('test-upload');
    
    if (!photo.src || !photo.src.startsWith('data:')) {
        showAlert('กรุณาถ่ายภาพก่อนทดสอบอัปโหลด', 'error');
        return;
    }
    
    const branch = branchSelect.value || 'CITY';
    
    // Disable button and show loading
    testButton.disabled = true;
    testButton.textContent = 'กำลังทดสอบ...';
    showAlert('กำลังทดสอบการอัปโหลดไป Google Drive...', 'info');
    
    console.log('Testing upload with branch:', branch);
    console.log('Image data length:', photo.src.length);
    
    fetch('/test_upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_data: photo.src,
            branch: branch
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log('Test upload result:', result);
        
        if (result.success) {
            const methods = result.successful_methods.join(', ');
            showAlert(`✅ ทดสอบสำเร็จ!\n${result.summary}`, 'success');
            
            // Log detailed results
            console.log('Successful methods:', result.successful_methods);
            console.log('Detailed results:', result.results);
            
            // Show URLs in console
            for (const [method, details] of Object.entries(result.results)) {
                if (details.success && details.url) {
                    console.log(`${method} URL:`, details.url);
                }
            }
        } else {
            // Show detailed error information
            let errorDetails = result.summary || 'ไม่สามารถอัปโหลดได้ทุกวิธี';
            
            // Add specific error details for each method
            if (result.results) {
                let details = [];
                if (result.results.apps_script && !result.results.apps_script.success) {
                    details.push(`Apps Script: ${result.results.apps_script.error || 'ล้มเหลว'}`);
                }
                if (result.results.oauth2 && !result.results.oauth2.success) {
                    details.push(`OAuth2: ${result.results.oauth2.error || 'ล้มเหลว'}`);
                }
                if (details.length > 0) {
                    errorDetails += `\n\nรายละเอียด:\n${details.join('\n')}`;
                }
            }
            
            showAlert(`❌ ทดสอบล้มเหลว!\n${errorDetails}`, 'error');
            console.error('Upload test failed:', result);
            
            // Also log individual results for debugging
            console.log('Apps Script result:', result.results?.apps_script);
            console.log('OAuth2 result:', result.results?.oauth2);
        }
    })
    .catch(error => {
        console.error('Error testing upload:', error);
        showAlert('❌ เกิดข้อผิดพลาดในการทดสอบ', 'error');
    })
    .finally(() => {
        // Re-enable button
        testButton.disabled = false;
        testButton.textContent = 'ทดสอบอัปโหลด Drive';
    });
}

function authorizeDrive() {
    console.log('authorizeDrive function called');
    showAlert('กำลังเปลี่ยนไปหน้า Google Authorization...', 'info');
    
    // Redirect to authorization endpoint
    window.location.href = '/authorize_drive';
}

function checkDriveStatus() {
    console.log('checkDriveStatus function called');
    
    const statusButton = document.getElementById('check-drive-status');
    statusButton.disabled = true;
    statusButton.textContent = 'กำลังตรวจสอบ...';
    
    fetch('/drive_status')
    .then(response => response.json())
    .then(result => {
        console.log('Drive status result:', result);
        
        if (result.authorized) {
            showAlert(`✅ ${result.message}`, 'success');
        } else {
            showAlert(`❌ ${result.message}\nกรุณากด "🔑 Authorize Google Drive" เพื่อให้สิทธิ์`, 'warning');
        }
    })
    .catch(error => {
        console.error('Error checking drive status:', error);
        showAlert('❌ เกิดข้อผิดพลาดในการตรวจสอบสถานะ', 'error');
    })
    .finally(() => {
        statusButton.disabled = false;
        statusButton.textContent = '📊 ตรวจสอบสถานะ Drive';
    });
}

