"""
Supabase Database Manager for Smart Inventory Management System
Phase 1: Core functionality for dashboard and analytics
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from supabase import create_client, Client

class SupabaseManager:
    def __init__(self):
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    # Product Management
    def get_all_products(self) -> List[Dict]:
        """Get all active products"""
        try:
            response = self.client.table('products').select('*').eq('is_active', True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Get product by barcode"""
        try:
            response = self.client.table('products').select('*').eq('barcode', barcode).eq('is_active', True).single().execute()
            return response.data
        except Exception as e:
            print(f"Error getting product by barcode {barcode}: {e}")
            return None
    
    def add_product(self, product_data: Dict) -> Optional[Dict]:
        """Add new product"""
        try:
            response = self.client.table('products').insert(product_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error adding product: {e}")
            return None
    
    # Branch Management
    def get_all_branches(self) -> List[Dict]:
        """Get all active branches"""
        try:
            response = self.client.table('branches').select('*').eq('is_active', True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting branches: {e}")
            return []
    
    def get_branch_by_name(self, name: str) -> Optional[Dict]:
        """Get branch by name"""
        try:
            response = self.client.table('branches').select('*').eq('name', name).single().execute()
            return response.data
        except Exception as e:
            print(f"Error getting branch by name {name}: {e}")
            return None
    
    # Inventory Management
    def get_inventory_by_branch(self, branch_id: str) -> List[Dict]:
        """Get inventory for a specific branch with product details"""
        try:
            response = self.client.table('inventory').select('''
                *,
                products (id, sku, barcode, name, category, reorder_level),
                branches (id, name, code)
            ''').eq('branch_id', branch_id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting inventory for branch {branch_id}: {e}")
            return []
    
    def update_inventory(self, product_id: str, branch_id: str, quantity: int, user_id: str = None) -> bool:
        """Update inventory quantity"""
        try:
            # Check if inventory record exists
            existing = self.client.table('inventory').select('id').eq('product_id', product_id).eq('branch_id', branch_id).execute()
            
            inventory_data = {
                'quantity': quantity,
                'updated_at': datetime.now().isoformat(),
                'last_counted_at': datetime.now().isoformat()
            }
            
            if user_id:
                inventory_data['last_counted_by'] = user_id
            
            if existing.data:
                # Update existing record
                response = self.client.table('inventory').update(inventory_data).eq('product_id', product_id).eq('branch_id', branch_id).execute()
            else:
                # Insert new record
                inventory_data.update({
                    'product_id': product_id,
                    'branch_id': branch_id
                })
                response = self.client.table('inventory').insert(inventory_data).execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating inventory: {e}")
            return False
    
    # Stock Counting
    def add_stock_count(self, count_data: Dict) -> bool:
        """Add stock count record"""
        try:
            # Ensure all required fields are present
            if 'counted_at' not in count_data:
                count_data['counted_at'] = datetime.now().isoformat()
            
            # Validate required fields
            required_fields = ['product_id', 'branch_id', 'counted_quantity']
            for field in required_fields:
                if field not in count_data:
                    print(f"Missing required field: {field}")
                    return False
            
            print(f"Inserting stock count data: {count_data}")
            response = self.client.table('stock_counts').insert(count_data).execute()
            
            # Update inventory with counted quantity if insert successful
            if response.data:
                print("Stock count inserted successfully, updating inventory...")
                try:
                    self.update_inventory(
                        count_data['product_id'],
                        count_data['branch_id'],
                        count_data['counted_quantity'],
                        count_data.get('counter_name')
                    )
                except Exception as inv_error:
                    print(f"Warning: Failed to update inventory: {inv_error}")
                    # Don't fail the whole operation if inventory update fails
            
            return len(response.data) > 0
        except Exception as e:
            print(f"Error adding stock count: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_stock_summary(self) -> List[Dict]:
        """Get stock summary with product and branch details"""
        try:
            response = self.client.table('inventory').select('''
                *,
                products (id, sku, barcode, name, category, reorder_level, selling_price),
                branches (id, name, code)
            ''').execute()
            return response.data
        except Exception as e:
            print(f"Error getting stock summary: {e}")
            return []
    
    # Sales Analytics
    def get_sales_by_period(self, start_date: datetime, end_date: datetime, branch_id: str = None) -> List[Dict]:
        """Get sales data for a specific period"""
        try:
            query = self.client.table('sales').select('''
                *,
                sale_items (
                    *,
                    products (id, name, category)
                ),
                branches (name, code)
            ''').gte('transaction_date', start_date.isoformat()).lte('transaction_date', end_date.isoformat())
            
            if branch_id:
                query = query.eq('branch_id', branch_id)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error getting sales by period: {e}")
            return []
    
    def get_daily_sales_summary(self, days: int = 30, branch_id: str = None) -> List[Dict]:
        """Get daily sales summary for last N days"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            end_date = datetime.now()
            
            query = f'''
                SELECT 
                    DATE(transaction_date) as sale_date,
                    COUNT(*) as transaction_count,
                    SUM(total_amount) as total_sales
                FROM sales 
                WHERE transaction_date >= '{start_date.isoformat()}'
                AND transaction_date <= '{end_date.isoformat()}'
            '''
            
            if branch_id:
                query += f" AND branch_id = '{branch_id}'"
            
            query += " GROUP BY DATE(transaction_date) ORDER BY sale_date DESC"
            
            response = self.client.rpc('execute_sql', {'query': query}).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting daily sales summary: {e}")
            return []
    
    def get_top_selling_products(self, days: int = 30, limit: int = 10, branch_id: str = None) -> List[Dict]:
        """Get top selling products"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            query = self.client.table('sale_items').select('''
                product_id,
                products (name, category, barcode),
                quantity
            ''').gte('created_at', start_date.isoformat())
            
            # If branch_id is provided, join with sales table to filter by branch
            if branch_id:
                query = query.select('''
                    product_id,
                    products (name, category, barcode),
                    quantity,
                    sales!inner (branch_id)
                ''').eq('sales.branch_id', branch_id)
            
            response = query.execute()
            
            # Aggregate the results
            product_sales = {}
            for item in response.data:
                product_id = item['product_id']
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        'product': item['products'],
                        'total_quantity': 0,
                        'total_sales': 0
                    }
                product_sales[product_id]['total_quantity'] += item['quantity']
            
            # Sort and limit
            sorted_products = sorted(product_sales.values(), key=lambda x: x['total_quantity'], reverse=True)
            return sorted_products[:limit]
        except Exception as e:
            print(f"Error getting top selling products: {e}")
            return []
    
    def get_low_stock_alerts(self, branch_id: str = None) -> List[Dict]:
        """Get products with low stock levels"""
        try:
            query = self.client.table('inventory').select('''
                *,
                products (id, name, barcode, reorder_level),
                branches (name, code)
            ''')
            
            if branch_id:
                query = query.eq('branch_id', branch_id)
            
            response = query.execute()
            
            # Filter products where quantity <= reorder_level
            low_stock_items = []
            for item in response.data:
                reorder_level = item['products']['reorder_level'] or 0
                if item['quantity'] <= reorder_level:
                    low_stock_items.append(item)
            
            return low_stock_items
        except Exception as e:
            print(f"Error getting low stock alerts: {e}")
            return []
    
    # Alert Management
    def create_alert(self, alert_data: Dict) -> bool:
        """Create a new alert"""
        try:
            response = self.client.table('alerts').insert(alert_data).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error creating alert: {e}")
            return False
    
    def get_active_alerts(self, branch_id: str = None) -> List[Dict]:
        """Get active (unresolved) alerts"""
        try:
            query = self.client.table('alerts').select('''
                *,
                products (name, barcode),
                branches (name, code)
            ''').eq('is_resolved', False).order('created_at', desc=True)
            
            if branch_id:
                query = query.eq('branch_id', branch_id)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error getting active alerts: {e}")
            return []
    
    def resolve_alert(self, alert_id: str, user_id: str) -> bool:
        """Resolve an alert"""
        try:
            response = self.client.table('alerts').update({
                'is_resolved': True,
                'resolved_by': user_id,
                'resolved_at': datetime.now().isoformat()
            }).eq('id', alert_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error resolving alert: {e}")
            return False
    
    # Dashboard Analytics
    def get_dashboard_summary(self, branch_id: str = None) -> Dict:
        """Get dashboard summary data"""
        try:
            # Get date ranges
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            last_30_days = today - timedelta(days=30)
            
            summary = {
                'total_products': 0,
                'total_branches': 0,
                'low_stock_count': 0,
                'active_alerts_count': 0,
                'today_sales': 0,
                'yesterday_sales': 0,
                'monthly_sales': 0,
                'top_products': [],
                'recent_stock_counts': []
            }
            
            # Total products
            products = self.get_all_products()
            summary['total_products'] = len(products)
            
            # Total branches
            branches = self.get_all_branches()
            summary['total_branches'] = len(branches)
            
            # Low stock count
            low_stock = self.get_low_stock_alerts(branch_id)
            summary['low_stock_count'] = len(low_stock)
            
            # Active alerts count
            alerts = self.get_active_alerts(branch_id)
            summary['active_alerts_count'] = len(alerts)
            
            # Sales data
            today_sales = self.get_sales_by_period(today.replace(hour=0, minute=0, second=0), today, branch_id)
            summary['today_sales'] = sum(sale['total_amount'] for sale in today_sales)
            
            yesterday_sales = self.get_sales_by_period(yesterday.replace(hour=0, minute=0, second=0), yesterday.replace(hour=23, minute=59, second=59), branch_id)
            summary['yesterday_sales'] = sum(sale['total_amount'] for sale in yesterday_sales)
            
            monthly_sales = self.get_sales_by_period(last_30_days, today, branch_id)
            summary['monthly_sales'] = sum(sale['total_amount'] for sale in monthly_sales)
            
            # Top products
            summary['top_products'] = self.get_top_selling_products(30, 5, branch_id)
            
            # Recent stock counts
            try:
                recent_counts = self.client.table('stock_counts').select('''
                    *,
                    products (name, barcode),
                    branches (name)
                ''').order('counted_at', desc=True).limit(5)
                
                if branch_id:
                    recent_counts = recent_counts.eq('branch_id', branch_id)
                
                response = recent_counts.execute()
                summary['recent_stock_counts'] = response.data
            except Exception as e:
                print(f"Error getting recent stock counts: {e}")
                summary['recent_stock_counts'] = []
            
            return summary
        except Exception as e:
            print(f"Error getting dashboard summary: {e}")
            return {}

def create_supabase_manager():
    """Factory function to create SupabaseManager instance"""
    try:
        return SupabaseManager()
    except Exception as e:
        print(f"Failed to create Supabase manager: {e}")
        return None