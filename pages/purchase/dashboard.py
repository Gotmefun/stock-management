from flask import render_template, session, redirect, url_for, request, jsonify
from datetime import datetime, timedelta
import json

def purchase_dashboard():
    """Purchase control center with detailed analytics"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    dashboard_data = {
        'purchase_metrics': get_purchase_metrics(),
        'monthly_spending': get_monthly_spending_data(),
        'supplier_analysis': get_detailed_supplier_analysis(),
        'inventory_alerts': get_inventory_alerts(),
        'price_trends': get_price_trends(),
        'order_pipeline': get_order_pipeline(),
        'cost_breakdown': get_cost_breakdown()
    }
    
    return render_template('purchase/dashboard.html', **dashboard_data)

def get_purchase_metrics():
    """Get key purchase metrics"""
    return {
        'total_orders_month': 42,
        'total_spent_month': 145000,
        'avg_order_value': 3452,
        'pending_orders': 8,
        'overdue_orders': 2,
        'supplier_count': 15,
        'cost_savings_month': 12500,
        'order_fulfillment_rate': 94.5
    }

def get_monthly_spending_data():
    """Get monthly spending trend data for chart"""
    return {
        'months': ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.'],
        'spending': [120000, 135000, 98000, 156000, 142000, 138000, 145000],
        'budget': [150000, 150000, 150000, 150000, 150000, 150000, 150000]
    }

def get_detailed_supplier_analysis():
    """Get detailed supplier performance analysis"""
    return [
        {
            'supplier_name': 'บริษัท อะไหล่ยนต์ จำกัด',
            'category': 'อะไหล่รถจักรยานยนต์',
            'total_orders': 24,
            'total_value': 580000,
            'avg_order_value': 24167,
            'on_time_delivery': 95.8,
            'quality_score': 4.8,
            'payment_terms': '30 วัน',
            'last_order_date': '2024-07-22',
            'next_expected_order': '2024-07-30',
            'cost_trend': 'stable',
            'relationship_score': 'excellent'
        },
        {
            'supplier_name': 'บริษัท โซ่สายพาน จำกัด',
            'category': 'โซ่และสายพาน',
            'total_orders': 18,
            'total_value': 420000,
            'avg_order_value': 23333,
            'on_time_delivery': 88.9,
            'quality_score': 4.5,
            'payment_terms': '15 วัน',
            'last_order_date': '2024-07-20',
            'next_expected_order': '2024-08-05',
            'cost_trend': 'increasing',
            'relationship_score': 'good'
        },
        {
            'supplier_name': 'ร้าน น้ำมันเครื่อง พรีเมียม',
            'category': 'น้ำมันและสารหล่อลื่น',
            'total_orders': 12,
            'total_value': 180000,
            'avg_order_value': 15000,
            'on_time_delivery': 100.0,
            'quality_score': 4.9,
            'payment_terms': '7 วัน',
            'last_order_date': '2024-07-25',
            'next_expected_order': '2024-08-10',
            'cost_trend': 'decreasing',
            'relationship_score': 'excellent'
        }
    ]

def get_inventory_alerts():
    """Get inventory-related alerts for purchasing"""
    return [
        {
            'type': 'critical_stock',
            'product_name': 'โซ่ Honda Wave 125',
            'current_stock': 2,
            'reorder_point': 10,
            'days_until_stockout': 1,
            'suggested_action': 'สั่งซื้อทันที',
            'estimated_cost': 15000
        },
        {
            'type': 'slow_moving',
            'product_name': 'กรองอากาศ Yamaha Mio',
            'current_stock': 45,
            'days_in_stock': 120,
            'suggested_action': 'ลดปริมาณการสั่งซื้อ',
            'potential_savings': 3000
        },
        {
            'type': 'price_increase',
            'product_name': 'น้ำมันเครื่อง Shell 20W-50',
            'current_price': 180,
            'new_price': 195,
            'increase_percentage': 8.3,
            'effective_date': '2024-08-01',
            'suggested_action': 'สั่งซื้อล่วงหน้า'
        }
    ]

def get_price_trends():
    """Get price trend data for key products"""
    return [
        {
            'product_name': 'โซ่ Honda Wave',
            'current_price': 350,
            'price_history': [320, 325, 340, 345, 350],
            'trend': 'increasing',
            'forecast_next_month': 360
        },
        {
            'product_name': 'น้ำมันเครื่อง',
            'current_price': 180,
            'price_history': [190, 185, 180, 175, 180],
            'trend': 'stable',
            'forecast_next_month': 185
        }
    ]

def get_order_pipeline():
    """Get order pipeline status"""
    return {
        'draft': 3,
        'pending_approval': 2,
        'approved': 5,
        'sent_to_supplier': 8,
        'confirmed': 12,
        'in_transit': 6,
        'delivered': 4,
        'completed': 2
    }

def get_cost_breakdown():
    """Get cost breakdown by category"""
    return [
        {'category': 'อะไหล่รถจักรยานยนต์', 'amount': 85000, 'percentage': 58.6},
        {'category': 'น้ำมันและสารหล่อลื่น', 'amount': 35000, 'percentage': 24.1},
        {'category': 'โซ่และสายพาน', 'amount': 15000, 'percentage': 10.3},
        {'category': 'อุปกรณ์ซ่อมบำรุง', 'amount': 10000, 'percentage': 6.9}
    ]