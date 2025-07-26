from flask import render_template, session, redirect, url_for, request, jsonify
from datetime import datetime, timedelta
import json

def purchase_hub():
    """Main purchase hub - overview of all purchase activities"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Sample data - replace with actual database queries
    purchase_data = {
        'pending_orders': get_pending_orders(),
        'critical_reorders': get_critical_reorders(),
        'supplier_performance': get_supplier_performance(),
        'budget_status': get_budget_status(),
        'recent_deliveries': get_recent_deliveries(),
        'ai_recommendations': get_ai_purchase_recommendations()
    }
    
    return render_template('purchase/index.html', **purchase_data)

def get_pending_orders():
    """Get pending purchase orders"""
    return [
        {
            'order_id': 'PO-2024-001',
            'supplier': 'บริษัท อะไหล่ยนต์ จำกัด',
            'total_amount': 45000,
            'order_date': '2024-07-20',
            'expected_delivery': '2024-07-28',
            'status': 'confirmed',
            'items_count': 12
        },
        {
            'order_id': 'PO-2024-002', 
            'supplier': 'บริษัท โซ่สายพาน จำกัด',
            'total_amount': 28500,
            'order_date': '2024-07-22',
            'expected_delivery': '2024-07-30',
            'status': 'pending',
            'items_count': 8
        }
    ]

def get_critical_reorders():
    """Get items that need immediate reordering"""
    return [
        {
            'product_name': 'โซ่ Honda Wave 125',
            'current_stock': 2,
            'reorder_point': 10,
            'suggested_quantity': 50,
            'average_daily_usage': 3,
            'days_until_stockout': 1,
            'priority': 'urgent'
        },
        {
            'product_name': 'ผ้าเบรค Honda Click',
            'current_stock': 5,
            'reorder_point': 15,
            'suggested_quantity': 30,
            'average_daily_usage': 2,
            'days_until_stockout': 3,
            'priority': 'high'
        }
    ]

def get_supplier_performance():
    """Get supplier performance metrics"""
    return [
        {
            'supplier_name': 'บริษัท อะไหล่ยนต์ จำกัด',
            'on_time_delivery': 95,
            'quality_score': 4.8,
            'total_orders': 24,
            'total_value': 580000,
            'avg_delivery_days': 5
        },
        {
            'supplier_name': 'บริษัท โซ่สายพาน จำกัด',
            'on_time_delivery': 88,
            'quality_score': 4.5,
            'total_orders': 18,
            'total_value': 420000,
            'avg_delivery_days': 7
        }
    ]

def get_budget_status():
    """Get current budget status"""
    return {
        'monthly_budget': 200000,
        'spent_this_month': 145000,
        'remaining_budget': 55000,
        'projected_month_end': 185000,
        'budget_utilization': 72.5,
        'days_remaining': 9
    }

def get_recent_deliveries():
    """Get recent deliveries"""
    return [
        {
            'order_id': 'PO-2024-001',
            'supplier': 'บริษัท อะไหล่ยนต์ จำกัด',
            'delivery_date': '2024-07-25',
            'items_received': 12,
            'total_value': 45000,
            'status': 'completed'
        }
    ]

def get_ai_purchase_recommendations():
    """Get AI-powered purchase recommendations"""
    return [
        {
            'product_name': 'น้ำมันเครื่อง Shell 20W-50',
            'recommended_quantity': 24,
            'reason': 'Seasonal demand increase detected',
            'potential_savings': 2400,
            'confidence': 85
        },
        {
            'product_name': 'ยางใน Honda Wave',
            'recommended_quantity': 40,
            'reason': 'Bulk discount opportunity',
            'potential_savings': 1200,
            'confidence': 78
        }
    ]