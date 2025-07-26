from flask import render_template, session, redirect, url_for, request, jsonify
from datetime import datetime, timedelta
import json
import requests

def moment():
    """Get current datetime for template"""
    return datetime.now()

def business_dashboard():
    """Enhanced Business Dashboard - Central hub for all business metrics"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get filter parameters
    branch_filter = request.args.get('branch', 'all')
    period_filter = request.args.get('period', '30')
    
    dashboard_data = {
        'real_time_metrics': get_real_time_business_metrics(),
        'branch_overview': get_branch_overview(),
        'cash_flow_status': get_cash_flow_status(),
        'kpi_cards': get_key_performance_indicators(),
        'critical_alerts': get_critical_business_alerts(),
        'quick_actions': get_quick_actions(),
        'weather_data': get_weather_data(),
        'daily_sales_chart': get_daily_sales_data(),
        'inventory_status': get_inventory_overview(),
        'recent_activities': get_recent_business_activities(),
        'upcoming_tasks': get_upcoming_tasks(),
        'financial_summary': get_financial_summary(),
        'moment': moment
    }
    
    return render_template('dashboard/index.html', **dashboard_data)

def get_real_time_business_metrics():
    """Get real-time business metrics for the dashboard"""
    return {
        'total_revenue_today': 25400,
        'total_revenue_change': +8.5,
        'orders_today': 47,
        'orders_change': +12.3,
        'active_customers': 156,
        'customers_change': +5.8,
        'low_stock_items': 8,
        'stock_change': +2,
        'pending_purchases': 12,
        'purchases_change': -3,
        'cash_in_hand': 145000,
        'cash_change': +15.2
    }

def get_branch_overview():
    """Get overview of all 3 branches"""
    return [
        {
            'name': 'สาขาตัวเมือง',
            'code': 'CITY',
            'revenue_today': 12500,
            'revenue_target': 15000,
            'performance': 83.3,
            'orders_count': 23,
            'staff_count': 3,
            'status': 'active',
            'last_update': '2024-07-26 14:30'
        },
        {
            'name': 'สาขาโป่งไผ่',
            'code': 'PONGPAI', 
            'revenue_today': 8900,
            'revenue_target': 10000,
            'performance': 89.0,
            'orders_count': 15,
            'staff_count': 2,
            'status': 'active',
            'last_update': '2024-07-26 14:25'
        },
        {
            'name': 'สาขาหน้าโรงเรียน',
            'code': 'SCHOOL',
            'revenue_today': 4000,
            'revenue_target': 8000,
            'performance': 50.0,
            'orders_count': 9,
            'staff_count': 2,
            'status': 'alert',
            'last_update': '2024-07-26 14:20'
        }
    ]

def get_cash_flow_status():
    """Get current cash flow status with alerts"""
    return {
        'total_cash': 145000,
        'receivables': 85000,
        'payables': 120000,
        'net_position': 110000,
        'days_cash_on_hand': 25,
        'burn_rate': 5800,
        'status': 'healthy',  # healthy, warning, critical
        'alerts': [
            {
                'type': 'warning',
                'message': 'ค่าใช้จ่ายเดือนนี้สูงกว่าปกติ 15%',
                'action': 'ตรวจสอบค่าใช้จ่าย'
            },
            {
                'type': 'info',
                'message': 'มีลูกหนี้ครบกำหนด 25,000฿',
                'action': 'ติดตามการชำระ'
            }
        ]
    }

def get_key_performance_indicators():
    """Get KPI cards with targets and performance"""
    return [
        {
            'name': 'ROI',
            'value': 18.5,
            'unit': '%',
            'target': 20.0,
            'performance': 92.5,
            'trend': 'up',
            'period': 'เดือนนี้'
        },
        {
            'name': 'Inventory Turnover',
            'value': 8.2,
            'unit': 'ครั้ง',
            'target': 10.0,
            'performance': 82.0,
            'trend': 'stable',
            'period': 'ปีนี้'
        },
        {
            'name': 'Profit Margin',
            'value': 24.8,
            'unit': '%',
            'target': 25.0,
            'performance': 99.2,
            'trend': 'up',
            'period': 'เดือนนี้'
        },
        {
            'name': 'Customer Satisfaction',
            'value': 4.6,
            'unit': '/5',
            'target': 4.5,
            'performance': 102.2,
            'trend': 'up',
            'period': 'เดือนนี้'
        }
    ]

def get_critical_business_alerts():
    """Get critical alerts that need immediate attention"""
    return [
        {
            'id': 1,
            'type': 'critical',
            'category': 'inventory',
            'title': 'สินค้าใกล้หมดสต๊อก',
            'message': 'โซ่ Honda Wave 125 เหลือ 2 ชิ้น (ปกติ 50 ชิ้น)',
            'action': 'สั่งซื้อทันที',
            'url': '/purchase?product=honda-wave-chain',
            'urgency': 'high',
            'time': '5 นาทีที่แล้ว'
        },
        {
            'id': 2,
            'type': 'warning',
            'category': 'finance',
            'title': 'งบประมาณใกล้เกิน',
            'message': 'ใช้งบประมาณไป 85% เหลืออีก 5 วัน',
            'action': 'ทบทวนค่าใช้จ่าย',
            'url': '/finance/budget',
            'urgency': 'medium',
            'time': '1 ชั่วโมงที่แล้ว'
        },
        {
            'id': 3,
            'type': 'info',
            'category': 'sales',
            'title': 'ยอดขายดีผิดปกติ',
            'message': 'สาขาโป่งไผ่มียอดขายสูงกว่าเป้าหมาย 15%',
            'action': 'เตรียมสินค้าเพิ่ม',
            'url': '/inventory/reorder',
            'urgency': 'low',
            'time': '2 ชั่วโมงที่แล้ว'
        }
    ]

def get_quick_actions():
    """Get quick action buttons for common tasks"""
    return [
        {
            'name': 'สั่งซื้อด่วน',
            'description': 'สั่งซื้อสินค้าที่ใกล้หมด',
            'icon': '🛒',
            'url': '/purchase/recommendations',
            'color': 'danger',
            'count': 8
        },
        {
            'name': 'เช็คสต๊อก',
            'description': 'ตรวจสอบสต๊อกสินค้าทุกสาขา',
            'icon': '📦',
            'url': '/inventory/stock',
            'color': 'primary',
            'count': 45
        },
        {
            'name': 'รายงานยอดขาย',
            'description': 'ดูรายงานยอดขายวันนี้',
            'icon': '📊',
            'url': '/sales/overview',
            'color': 'success',
            'count': 0
        },
        {
            'name': 'จัดการลูกค้า',
            'description': 'อัปเดตฐานข้อมูลลูกค้า',
            'icon': '👥',
            'url': '/customers/database',
            'color': 'info',
            'count': 12
        }
    ]

def get_weather_data():
    """Get weather data for business planning"""
    # Mock weather data - in production, integrate with weather API
    return {
        'location': 'อำเภอเมือง, จังหวัดแพร่',
        'temperature': 32,
        'condition': 'sunny',
        'humidity': 65,
        'description': 'แจ่มใส',
        'forecast': [
            {'day': 'วันนี้', 'temp': 32, 'condition': 'sunny'},
            {'day': 'พรุ่งนี้', 'temp': 30, 'condition': 'cloudy'},
            {'day': 'มะรืนนี้', 'temp': 28, 'condition': 'rainy'}
        ],
        'business_impact': {
            'type': 'positive',
            'message': 'อากาศดี คาดว่ายอดขายจะเพิ่มขึ้น 10-15%'
        }
    }

def get_daily_sales_data():
    """Get daily sales data for chart"""
    return {
        'labels': ['6:00', '8:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00'],
        'datasets': [
            {
                'label': 'ตัวเมือง',
                'data': [500, 1200, 2100, 3500, 2800, 3200, 4100, 3800],
                'color': '#667eea'
            },
            {
                'label': 'โป่งไผ่',
                'data': [300, 800, 1500, 2200, 1800, 2100, 2800, 2600],
                'color': '#764ba2'
            },
            {
                'label': 'หน้าโรงเรียน',
                'data': [200, 400, 600, 1100, 900, 1200, 1400, 1300],
                'color': '#f093fb'
            }
        ]
    }

def get_inventory_overview():
    """Get inventory status overview"""
    return {
        'total_items': 1247,
        'low_stock_items': 8,
        'out_of_stock': 3,
        'overstocked': 12,
        'total_value': 580000,
        'turnover_rate': 8.2,
        'categories': [
            {'name': 'อะไหล่รถจักรยานยนต์', 'count': 456, 'value': 280000},
            {'name': 'น้ำมันเครื่องและสารหล่อลื่น', 'count': 234, 'value': 150000},
            {'name': 'โซ่และสายพาน', 'count': 189, 'value': 95000},
            {'name': 'อุปกรณ์ซ่อมบำรุง', 'count': 368, 'value': 55000}
        ]
    }

def get_recent_business_activities():
    """Get recent business activities"""
    return [
        {
            'time': '14:30',
            'type': 'sale',
            'message': 'ขายโซ่ Honda Wave - 1,200฿ (สาขาตัวเมือง)',
            'user': 'พนักงาน A'
        },
        {
            'time': '14:15',
            'type': 'inventory',
            'message': 'นับสต๊อกน้ำมันเครื่อง Shell - 24 ขวด (สาขาโป่งไผ่)',
            'user': 'พนักงาน B'
        },
        {
            'time': '13:45',
            'type': 'purchase',
            'message': 'อนุมัติใบสั่งซื้อ PO-2024-015 - 25,000฿',
            'user': 'Admin'
        },
        {
            'time': '13:30',
            'type': 'alert',
            'message': 'แจ้งเตือน: ผ้าเบรค Honda Click ใกล้หมด',
            'user': 'System'
        }
    ]

def get_upcoming_tasks():
    """Get upcoming tasks and reminders"""
    return [
        {
            'title': 'ชำระค่าสินค้าซัพพลายเออร์ A',
            'due_date': '2024-07-28',
            'amount': 45000,
            'priority': 'high',
            'category': 'payment'
        },
        {
            'title': 'ส่งรายงานยอดขายประจำเดือน',
            'due_date': '2024-07-30',
            'amount': 0,
            'priority': 'medium',
            'category': 'report'  
        },
        {
            'title': 'ตรวจสอบสต๊อกสินค้าประจำสัปดาห์',
            'due_date': '2024-07-29',
            'amount': 0,
            'priority': 'low',
            'category': 'inventory'
        }
    ]

def get_financial_summary():
    """Get financial summary for the dashboard"""
    return {
        'revenue_month': 580000,
        'revenue_target': 600000,
        'expenses_month': 420000,
        'profit_month': 160000,
        'profit_margin': 24.8,
        'cash_flow': 145000,
        'outstanding_receivables': 85000,
        'outstanding_payables': 120000
    }