let html5QrCode;
let cameraId;
let isScanning = false;
let stream;
let recentScans = [];

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize barcode form
    document.getElementById('stock-form').addEventListener('submit', handleSubmit);
    
    // Initialize camera controls
    document.getElementById('start-camera').addEventListener('click', startCamera);
    document.getElementById('take-photo').addEventListener('click', takePhoto);
    document.getElementById('retake-photo').addEventListener('click', retakePhoto);
    
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
    
    photo.style.display = 'none';
    video.style.display = 'none';
    
    startButton.disabled = false;
    takeButton.disabled = true;
    retakeButton.disabled = true;
}

function handleSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = {
        barcode: formData.get('barcode'),
        quantity: parseInt(formData.get('quantity')),
        branch: formData.get('branch'),
        product_name: document.getElementById('product-name').textContent,
        counter_name: formData.get('counter_name')
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
            product_name: !!data.product_name
        });
        showAlert('กรุณากรอกข้อมูลให้ครบถ้วน', 'error');
        return;
    }
    
    // Submit data
    submitStockData(data);
}

function submitStockData(data) {
    const submitButton = document.getElementById('submit-btn');
    submitButton.disabled = true;
    submitButton.textContent = 'กำลังบันทึก...';
    
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
            showAlert('บันทึกข้อมูลสำเร็จ!', 'success');
            
            // Add to recent scans
            addRecentScan(data);
            
            // Reset form
            resetForm();
        } else {
            showAlert('เกิดข้อผิดพลาดในการบันทึกข้อมูล', 'error');
        }
    })
    .catch(error => {
        console.error('Error submitting data:', error);
        showAlert('เกิดข้อผิดพลาดในการบันทึกข้อมูล', 'error');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = 'บันทึกข้อมูล';
    });
}

function addRecentScan(data) {
    const scan = {
        barcode: data.barcode,
        product_name: data.product_name,
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
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

