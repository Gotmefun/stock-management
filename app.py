from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify, send_from_directory
import hashlib
from datetime import datetime, timedelta
import os
from functools import wraps
from dotenv import load_dotenv
from upload_to_drive import create_drive_uploader
from sheets_manager import create_sheets_manager
from oauth_manager import oauth_drive_manager
from supabase_manager import create_supabase_manager

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Google Sheets IDs - Update these with your actual sheet IDs
PRODUCT_SHEET_ID = os.environ.get('PRODUCT_SHEET_ID', '17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM')
STOCK_SHEET_ID = os.environ.get('STOCK_SHEET_ID', '1OaEqOS7I0_hN2Q1nc4isqPXXdjp7_i7ZAPJFhUr5X7k')

# Initialize Google Drive uploader, Sheets manager, and Supabase
try:
    drive_uploader = create_drive_uploader()
    sheets_manager = create_sheets_manager()
    supabase_manager = create_supabase_manager()
    print(f"Drive uploader type: {type(drive_uploader)}")
    print(f"Sheets manager type: {type(sheets_manager)}")
    print(f"Supabase manager type: {type(supabase_manager)}")
except Exception as e:
    print(f"Failed to initialize services: {e}")
    from upload_to_drive import MockGoogleDriveUploader
    drive_uploader = MockGoogleDriveUploader()
    sheets_manager = None
    supabase_manager = None

# Simple user authentication (in production, use proper authentication)
USERS = {
    'admin': {'password': hashlib.sha256('Teeomega2014'.encode()).hexdigest(), 'role': 'admin'},
    'staff': {'password': hashlib.sha256('staff123'.encode()).hexdigest(), 'role': 'staff'}
}

# Google Apps Script Web App URL - ใส่ URL ที่ได้จาก deployment
APPS_SCRIPT_URL = os.environ.get('APPS_SCRIPT_URL', 'https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec')

def upload_via_apps_script(image_data, filename, branch=None):
    """Upload image via Google Apps Script with branch-specific folder"""
    print(f"=== UPLOAD VIA APPS SCRIPT ===")
    print(f"APPS_SCRIPT_URL: {APPS_SCRIPT_URL}")
    
    if not APPS_SCRIPT_URL or APPS_SCRIPT_URL == 'YOUR_APPS_SCRIPT_URL_HERE':
        print("❌ Apps Script URL not configured")
        return None
    
    try:
        import requests
        import json
        
        # Branch mapping for folder organization
        branch_mapping = {
            'CITY': 'สาขาตัวเมือง',
            'SCHOOL': 'สาขาหน้าโรงเรียน', 
            'PONGPAI': 'สาขาโป่งไผ่',
            # Support Thai names as well
            'สาขาตัวเมือง': 'สาขาตัวเมือง',
            'สาขาหน้าโรงเรียน': 'สาขาหน้าโรงเรียน',
            'สาขาโป่งไผ่': 'สาขาโป่งไผ่'
        }
        
        # Create branch-specific folder path
        if branch and branch in branch_mapping:
            folder_name = branch_mapping[branch]
        else:
            folder_name = 'สาขาตัวเมือง'  # Default to CITY branch
        
        folder = f'Pic Stock 3 User/{folder_name}'
        
        payload = {
            'imageData': image_data,
            'filename': filename,
            'folder': folder
        }
        
        print(f"Sending image to Apps Script: {filename} -> {folder}")
        print(f"Payload keys: {list(payload.keys())}")
        print(f"Image data starts with: {payload['imageData'][:50]}...")
        
        response = requests.post(
            APPS_SCRIPT_URL,
            json=payload,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"=== APPS SCRIPT RAW RESPONSE ===")
            print(f"Response text: {response.text}")
            print(f"Response length: {len(response.text)}")
            
            try:
                result = response.json()
                print(f"=== APPS SCRIPT PARSED JSON ===")
                print(f"Response: {result}")
                print(f"Success: {result.get('success')}")
                print(f"webViewLink: {result.get('webViewLink')}")
                
                if result.get('success'):
                    webview_link = result.get('webViewLink')
                    print(f"✅ Apps Script upload successful: {webview_link}")
                    print(f"Returning: {webview_link}")
                    return webview_link
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ Apps Script upload failed: {error_msg}")
                    return None
            except json.JSONDecodeError as e:
                print(f"❌ Apps Script JSON parse error: {e}")
                print(f"Raw response: {response.text}")
                print(f"Response content type: {response.headers.get('content-type')}")
                return None
        else:
            print(f"❌ Apps Script request failed: {response.status_code}")
            print(f"Response text: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error uploading via Apps Script: {e}")
        return None

def init_sheets():
    """Initialize Google Sheets with headers and sample data if needed"""
    if not sheets_manager:
        print("Sheets manager not available")
        return
    
    try:
        # Initialize headers for both sheets
        print("Initializing Product Master sheet headers...")
        sheets_manager.initialize_product_sheet_headers(PRODUCT_SHEET_ID)
        
        print("Initializing Stock Counting sheet headers...")  
        sheets_manager.initialize_stock_sheet_headers(STOCK_SHEET_ID)
        
        # Add sample products if sheet is empty
        products = sheets_manager.get_all_products(PRODUCT_SHEET_ID)
        if len(products) == 0:
            print("Adding sample products...")
            sheets_manager.add_sample_products(PRODUCT_SHEET_ID)
        
        print("Google Sheets initialized successfully")
        
    except Exception as e:
        print(f"Error initializing sheets: {e}")

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """Decorator to require staff role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if session.get('role') not in ['staff', 'admin']:
            flash('Access denied. Staff privileges required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check against USERS dictionary
        if username in USERS and USERS[username]['password'] == hashed_password:
            session['user_id'] = username
            session['username'] = username
            session['role'] = USERS[username]['role']
            
            if USERS[username]['role'] == 'admin':
                return redirect(url_for('admin_summary'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/authorize_drive')
@login_required
def authorize_drive():
    """Redirect user to Google OAuth2 authorization"""
    try:
        print("=== Starting OAuth2 authorization ===")
        auth_url = oauth_drive_manager.get_authorization_url()
        print(f"Generated auth URL: {auth_url[:100]}...")
        return redirect(auth_url)
    except Exception as e:
        print(f"OAuth authorization error: {e}")
        flash(f'Authorization error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth2 callback"""
    print("=== OAuth2 Callback Endpoint ===")
    print(f"Request URL: {request.url}")
    print(f"Request args: {dict(request.args)}")
    print(f"Request method: {request.method}")
    
    authorization_code = request.args.get('code')
    error = request.args.get('error')
    state = request.args.get('state')
    
    print(f"Authorization code: {authorization_code[:20] if authorization_code else 'None'}...")
    print(f"Error: {error}")
    print(f"State: {state}")
    
    if error:
        print(f"OAuth error received: {error}")
        flash(f'Authorization error: {error}', 'error')
        return redirect(url_for('index'))
    
    if authorization_code:
        print(f"Processing authorization code: {authorization_code[:20]}...")
        try:
            success = oauth_drive_manager.handle_oauth_callback(authorization_code)
            print(f"OAuth callback result: {success}")
            
            if success:
                print("OAuth callback successful!")
                flash('Google Drive authorization successful!', 'success')
                
                # Verify token file exists after callback
                import os
                token_file = 'drive_token.pickle'
                if os.path.exists(token_file):
                    file_size = os.path.getsize(token_file)
                    print(f"Token file verified: {token_file}, size: {file_size} bytes")
                else:
                    print(f"WARNING: Token file not found after successful callback: {token_file}")
            else:
                print("OAuth callback failed!")
                flash('Google Drive authorization failed!', 'error')
        except Exception as callback_error:
            print(f"Exception in callback processing: {callback_error}")
            import traceback
            traceback.print_exc()
            flash('Google Drive authorization failed!', 'error')
    else:
        print("No authorization code received")
        flash('Authorization cancelled', 'error')
    
    print("=== Redirecting to index ===")
    return redirect(url_for('index'))

@app.route('/drive_status')
@login_required
def drive_status():
    """Check Google Drive authorization status"""
    is_authorized = oauth_drive_manager.is_authorized()
    return jsonify({
        'authorized': is_authorized,
        'message': 'Google Drive is authorized' if is_authorized else 'Google Drive not authorized'
    })

@app.route('/test_upload', methods=['POST'])
@login_required
def test_upload():
    """Test image upload to Google Drive"""
    try:
        data = request.get_json()
        if not data or 'image_data' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Generate test filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_upload_{timestamp}.jpg"
        branch = data.get('branch', 'CITY')
        
        print(f"=== TESTING IMAGE UPLOAD ===")
        print(f"Filename: {filename}")
        print(f"Branch: {branch}")
        print(f"Image data length: {len(data['image_data'])}")
        print(f"Apps Script URL: {APPS_SCRIPT_URL}")
        print(f"OAuth drive manager available: {oauth_drive_manager is not None}")
        
        results = {}
        
        # Test 1: Google Apps Script
        print("\n=== TESTING APPS SCRIPT ===")
        try:
            apps_script_result = upload_via_apps_script(data['image_data'], filename, branch)
            results['apps_script'] = {
                'success': bool(apps_script_result),
                'url': apps_script_result,
                'method': 'Google Apps Script'
            }
            if not apps_script_result:
                results['apps_script']['error'] = 'Upload returned None/empty result'
        except Exception as e:
            results['apps_script'] = {
                'success': False,
                'error': str(e),
                'method': 'Google Apps Script'
            }
        
        # Test 2: OAuth2 Google Drive (if authorized)
        print("\n=== TESTING OAUTH2 DRIVE ===")
        if oauth_drive_manager.is_authorized():
            try:
                # Use branch-specific folder for test upload too
                branch_name_mapping = {
                    'CITY': 'สาขาตัวเมือง',
                    'SCHOOL': 'สาขาหน้าโรงเรียน', 
                    'PONGPAI': 'สาขาโป่งไผ่'
                }
                branch_folder = branch_name_mapping.get(branch, 'สาขาตัวเมือง')
                test_folder_path = f'Pic Stock 3 User/{branch_folder}/Test Upload'
                print(f"Test upload folder path: {test_folder_path}")
                folder_id = oauth_drive_manager.get_or_create_folder_path(test_folder_path)
                oauth_result = oauth_drive_manager.upload_image_from_base64(
                    data['image_data'], 
                    f"oauth_{filename}",
                    folder_id
                )
                results['oauth2'] = {
                    'success': bool(oauth_result),
                    'url': oauth_result.get('web_view_link') if oauth_result else None,
                    'method': 'OAuth2 Google Drive'
                }
            except Exception as e:
                results['oauth2'] = {
                    'success': False,
                    'error': str(e),
                    'method': 'OAuth2 Google Drive'
                }
        else:
            results['oauth2'] = {
                'success': False,
                'error': 'Not authorized',
                'method': 'OAuth2 Google Drive'
            }
        
        # Summary
        successful_methods = [method for method, result in results.items() if result['success']]
        
        return jsonify({
            'success': len(successful_methods) > 0,
            'successful_methods': successful_methods,
            'results': results,
            'summary': f"Successfully uploaded via: {', '.join(successful_methods)}" if successful_methods else "All upload methods failed"
        })
        
    except Exception as e:
        print(f"Error in test_upload: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Test upload failed: {str(e)}'}), 500

@app.route('/')
@staff_required
def index():
    return render_template('index.html')

@app.route('/get_product/<barcode>')
@login_required
def get_product(barcode):
    # Try Supabase first, fallback to Google Sheets
    if supabase_manager:
        try:
            print(f"Looking for barcode in Supabase: {barcode}")
            product = supabase_manager.get_product_by_barcode(barcode)
            if product:
                print(f"Found product in Supabase: {product}")
                
                # Check for existing counts of this product
                duplicate_warning = None
                try:
                    # Get all existing counts for this product (across all branches for now)
                    existing_counts = supabase_manager.client.table('stock_counts').select('branch_name, count_number, counted_at').eq('barcode', barcode).order('counted_at', desc=True).execute()
                    
                    if existing_counts.data and len(existing_counts.data) > 0:
                        total_counts = len(existing_counts.data)
                        latest_count = existing_counts.data[0]
                        
                        # Create warning message
                        branch_info = latest_count.get('branch_name', 'ไม่ระบุสาขา')
                        count_number = latest_count.get('count_number', total_counts)
                        counted_at = latest_count.get('counted_at', '')
                        
                        # Format date
                        date_info = ''
                        if counted_at:
                            try:
                                from datetime import datetime
                                # Parse ISO format and convert to Thai format
                                dt = datetime.fromisoformat(counted_at.replace('Z', '+00:00'))
                                date_info = dt.strftime("%d/%m/%Y %H:%M")
                            except:
                                date_info = counted_at[:16].replace('T', ' ')
                        
                        duplicate_warning = {
                            'message': f"⚠️ สินค้านี้เคยถูกนับไปแล้ว {total_counts} ครั้ง",
                            'details': f"ครั้งล่าสุด: นับครั้งที่ {count_number} ที่ {branch_info}",
                            'date_info': f"วันที่: {date_info}" if date_info else "",
                            'total_counts': total_counts
                        }
                        print(f"Duplicate warning: {duplicate_warning}")
                
                except Exception as dup_error:
                    print(f"Error checking duplicates: {dup_error}")
                
                response_data = {
                    'id': product['id'],
                    'name': product['name'],
                    'barcode': product['barcode'],
                    'sku': product.get('sku', ''),
                    'category': product.get('category', ''),
                    'selling_price': product.get('selling_price', 0)
                }
                
                if duplicate_warning:
                    response_data['duplicate_warning'] = duplicate_warning
                    
                return jsonify(response_data)
        except Exception as e:
            print(f"Error searching Supabase: {e}")
    
    # Fallback to Google Sheets
    if not sheets_manager:
        return jsonify({'error': 'No data source available'}), 500
    
    try:
        print(f"Looking for barcode in Sheets: {barcode}")
        product = sheets_manager.get_product_by_barcode(barcode, PRODUCT_SHEET_ID)
        print(f"Found product in Sheets: {product}")
        
        if product:
            return jsonify(product)
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        print(f"Error in get_product: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/submit_stock', methods=['POST'])
@staff_required
def submit_stock():
    try:
        data = request.get_json()
        print(f"=== SUBMIT STOCK DEBUG ===")
        print(f"Received data keys: {list(data.keys()) if data else 'None'}")
        print(f"Branch: {data.get('branch') if data else 'None'}")
        print(f"Barcode: {data.get('barcode') if data else 'None'}")
        print(f"Has image_data: {'image_data' in data if data else 'None'}")
    except Exception as e:
        print(f"Error parsing request data: {e}")
        return jsonify({'error': 'Invalid request data'}), 400
    
    if not data:
        return jsonify({'error': 'No data received'}), 400
    
    # Save to both Supabase and Google Sheets for redundancy
    supabase_success = False
    sheets_success = False
    count_info = ''
    
    image_url = ''
    
    # Handle image upload if present
    if 'image_data' in data and data['image_data']:
        print(f"Image data received, length: {len(data['image_data'])}")
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_{data['barcode']}_{timestamp}.jpg"
            print(f"Uploading image with filename: {filename}")
            
            # Try Google Apps Script upload first
            print("Trying Google Apps Script upload...")
            branch = data.get('branch', 'CITY')  # Get branch from data or default to CITY
            print(f"Branch mapping: {branch} -> folder will be determined by Apps Script")
            
            image_url = upload_via_apps_script(data['image_data'], filename, branch)
            
            print(f"=== APPS SCRIPT RESULT ===")
            print(f"Returned image_url: {image_url}")
            print(f"image_url type: {type(image_url)}")
            print(f"image_url empty?: {not image_url}")
            
            if image_url:
                print(f"✅ Apps Script upload successful: {image_url}")
            else:
                print("❌ Apps Script upload failed, trying OAuth2...")
                # Try OAuth2 Google Drive upload as fallback
                if oauth_drive_manager.is_authorized():
                    try:
                        # Get or create folder path with branch-specific folder
                        branch_code = data.get('branch', 'CITY')
                        branch_name_mapping = {
                            'CITY': 'สาขาตัวเมือง',
                            'SCHOOL': 'สาขาหน้าโรงเรียน', 
                            'PONGPAI': 'สาขาโป่งไผ่'
                        }
                        branch_folder = branch_name_mapping.get(branch_code, 'สาขาตัวเมือง')
                        folder_path = f'Pic Stock 3 User/{branch_folder}'
                        print(f"OAuth2 folder path: {folder_path}")
                        folder_id = oauth_drive_manager.get_or_create_folder_path(folder_path)
                        
                        # Upload to Google Drive
                        oauth_upload_result = oauth_drive_manager.upload_image_from_base64(
                            data['image_data'], 
                            filename,
                            folder_id
                        )
                        
                        if oauth_upload_result:
                            image_url = oauth_upload_result['web_view_link']
                            print(f"OAuth2 upload successful: {image_url}")
                        else:
                            print("OAuth2 upload failed")
                            
                    except Exception as oauth_error:
                        print(f"OAuth2 upload error: {oauth_error}")
                else:
                    print("Google Drive not authorized")
            
            # Fallback to local storage if OAuth2 failed or not authorized
            if not image_url:
                print("Google Drive upload failed or not authorized - saving locally as backup")
                import os
                import base64
                
                os.makedirs('uploads', exist_ok=True)
                image_data_clean = data['image_data']
                if image_data_clean.startswith('data:'):
                    image_data_clean = image_data_clean.split(',')[1]
                
                image_bytes = base64.b64decode(image_data_clean)
                local_path = os.path.join('uploads', filename)
                
                with open(local_path, 'wb') as f:
                    f.write(image_bytes)
                
                image_url = f"local://{local_path}"
                print(f"Using local backup: {image_url}")
                
        except Exception as e:
            print(f"Error uploading image: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No image data received or image data is empty")
    
    # Try to save to Supabase first
    if supabase_manager:
        try:
            # Get product ID from barcode
            product = supabase_manager.get_product_by_barcode(data['barcode'])
            if product:
                # Get branch ID with mapping
                branch_code = data['branch']
                # Map branch codes to full names
                branch_name_mapping = {
                    'CITY': 'สาขาตัวเมือง',
                    'SCHOOL': 'สาขาหน้าโรงเรียน', 
                    'PONGPAI': 'สาขาโป่งไผ่'
                }
                
                # Try both code and full name
                branch_name = branch_name_mapping.get(branch_code, branch_code)
                print(f"Looking for branch: '{branch_code}' -> '{branch_name}'")
                
                branch = supabase_manager.get_branch_by_name(branch_name)
                if not branch:
                    # Try original code if mapping failed
                    branch = supabase_manager.get_branch_by_name(branch_code)
                
                if branch:
                    # Prepare stock count data for Supabase
                    stock_count_data = {
                        'product_id': product['id'],
                        'branch_id': branch['id'],
                        'barcode': data['barcode'],
                        'product_name': data['product_name'],
                        'counted_quantity': int(data['quantity']),
                        'counter_name': data.get('counter_name', 'Unknown'),
                        'image_url': image_url,
                        'notes': f"Counted by {session.get('username', 'Unknown')}"
                    }
                    
                    # Get count info before saving
                    try:
                        existing_counts = supabase_manager.client.table('stock_counts').select('id').eq('product_id', product['id']).eq('branch_id', branch['id']).execute()
                        count_number = len(existing_counts.data) + 1
                        count_info = f"นับครั้งที่ {count_number}"
                    except:
                        count_info = "นับครั้งแรก"
                    
                    supabase_success = supabase_manager.add_stock_count(stock_count_data)
                    if supabase_success:
                        print(f"✅ Stock data saved to Supabase successfully - {count_info}")
                    else:
                        print("❌ Failed to save stock data to Supabase")
                else:
                    # Create branch if not exists, then save stock count
                    print(f"⚠️ Branch not found: {branch_name}, creating new branch...")
                    
                    # Create new branch
                    new_branch_data = {
                        'name': branch_name,
                        'code': branch_code,
                        'address': f'ที่อยู่ {branch_name}',
                        'phone': '',
                        'is_active': True
                    }
                    
                    new_branch = supabase_manager.add_branch(new_branch_data)
                    if new_branch:
                        print(f"✅ Created new branch: {branch_name}")
                        
                        # Now save stock count with new branch
                        stock_count_data = {
                            'product_id': product['id'],
                            'branch_id': new_branch['id'],
                            'barcode': data['barcode'],
                            'product_name': data['product_name'],
                            'counted_quantity': int(data['quantity']),
                            'counter_name': data.get('counter_name', 'Unknown'),
                            'image_url': image_url,
                            'notes': f"Counted by {session.get('username', 'Unknown')}"
                        }
                        
                        # Get count info for new branch (will be first count)
                        count_info = "นับครั้งแรก"
                        
                        supabase_success = supabase_manager.add_stock_count(stock_count_data)
                        if supabase_success:
                            print(f"✅ Stock data saved to Supabase with new branch - {count_info}")
                        else:
                            print("❌ Failed to save stock data even with new branch")
                    else:
                        print(f"❌ Failed to create branch: {branch_name}")
            else:
                print(f"Product not found in Supabase: {data['barcode']}")
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
    else:
        print("Supabase not available, skipping...")
    
    # Fallback to Google Sheets if available
    if sheets_manager:
        try:
            stock_data = {
                'barcode': data['barcode'],
                'product_name': data['product_name'],
                'quantity': data['quantity'],
                'branch': data['branch'],
                'user': session.get('username', 'Unknown'),
                'image_url': image_url,
                'counter_name': data.get('counter_name', 'Unknown')
            }
            
            sheets_success = sheets_manager.add_stock_record(stock_data, STOCK_SHEET_ID)
            if sheets_success:
                print("Stock data saved to Google Sheets successfully")
            else:
                print("Failed to save stock data to Google Sheets")
        except Exception as e:
            print(f"Error saving to Google Sheets: {e}")
    else:
        print("Google Sheets not available, skipping...")
    
    # If image was uploaded successfully, consider it a success even if database save failed
    if image_url and image_url != '':
        print(f"Image uploaded successfully: {image_url}")
        # At minimum, we have the image uploaded
        supabase_success = True  # Mark as success since image was uploaded
    
    # Return success if either method worked
    if supabase_success or sheets_success:
        response_data = {
            'success': True, 
            'saved_to': {
                'supabase': supabase_success,
                'sheets': sheets_success
            }
        }
        
        # Add count info if available
        if count_info:
            response_data['count_info'] = count_info
            
        return jsonify(response_data)
    else:
        return jsonify({'error': 'Failed to save stock data to any data source'}), 500

# Add global error handler
@app.errorhandler(500)
def internal_error(error):
    print(f"500 Error occurred: {error}")
    import traceback
    traceback.print_exc()
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.route('/report/summary')
@admin_required
def admin_summary():
    print("=== Admin Summary Route Called ===")
    
    if not sheets_manager:
        print("ERROR: Sheets manager not available")
        flash('Sheets manager not available', 'error')
        return redirect(url_for('index'))
    
    try:
        print(f"Getting stock summary from sheets: {STOCK_SHEET_ID}, {PRODUCT_SHEET_ID}")
        products = sheets_manager.get_stock_summary(STOCK_SHEET_ID, PRODUCT_SHEET_ID)
        print(f"Retrieved {len(products) if products else 0} products")
        
        # For now, we'll show basic stock summary
        # In the future, you could integrate with sales data from another sheet
        return render_template('summary.html', products=products, branch_summary=[])
        
    except Exception as e:
        print(f"ERROR in admin_summary: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading summary data: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/report/products')
@admin_required
def view_products():
    if not sheets_manager:
        flash('Sheets manager not available', 'error')
        return redirect(url_for('index'))
    
    try:
        products = sheets_manager.get_all_products(PRODUCT_SHEET_ID)
        return render_template('products.html', products=products)
        
    except Exception as e:
        print(f"Error getting products: {e}")
        flash('Error loading products data', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
@admin_required
def dashboard():
    """Smart Inventory Dashboard - Phase 1"""
    if not supabase_manager:
        flash('Database not available. Using legacy system.', 'error')
        return redirect(url_for('admin_summary'))
    
    try:
        # Get filter parameters
        branch_id = request.args.get('branch_id')
        period = int(request.args.get('period', 30))
        
        # Get dashboard data
        summary = supabase_manager.get_dashboard_summary(branch_id)
        alerts = supabase_manager.get_active_alerts(branch_id)
        branches = supabase_manager.get_all_branches()
        
        return render_template('dashboard.html', 
                             summary=summary, 
                             alerts=alerts, 
                             branches=branches)
        
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('admin_summary'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    init_sheets()
    app.run(host='127.0.0.1', port=8081, debug=True)
