import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from extensions import db
from models.sale import Sale, SaleItem
from models.purchase import Purchase, PurchaseItem
from models.company import Company
from models.item import Item

class SalesAnalytics:
    @staticmethod
    def get_sales_by_company(start_date=None, end_date=None):
        """Analisi delle vendite per fornitore"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        query = text("""
            SELECT 
                c.id as company_id,
                c.name as company_name,
                i.id as item_id,
                i.name as item_name,
                i.sku,
                si.quantity,
                si.unit_price,
                si.total_price,
                s.date as sale_date,
                s.status
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            JOIN items i ON si.item_id = i.id
            JOIN companies c ON i.company_id = c.id
            WHERE s.date BETWEEN :start_date AND :end_date
            AND s.status != 'cancelled'
        """)

        result = db.session.execute(query, {
            'start_date': start_date,
            'end_date': end_date
        })

        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return {
                'message': 'Nessun dato disponibile per il periodo selezionato',
                'data': {}
            }

        company_analysis = {}
        for company_id in df['company_id'].unique():
            company_df = df[df['company_id'] == company_id]
            company_name = company_df['company_name'].iloc[0]

            analysis = {
                'company_name': company_name,
                'total_sales': float(company_df['total_price'].sum()),
                'total_items_sold': int(company_df['quantity'].sum()),
                'average_order_value': float(company_df['total_price'].mean()),
                'items_analysis': [],
                'daily_sales': SalesAnalytics._get_daily_sales(company_df),
                'top_selling_items': SalesAnalytics._get_top_selling_items(company_df)
            }

            for item_id in company_df['item_id'].unique():
                item_df = company_df[company_df['item_id'] == item_id]
                item_analysis = {
                    'item_name': item_df['item_name'].iloc[0],
                    'sku': item_df['sku'].iloc[0],
                    'total_quantity': int(item_df['quantity'].sum()),
                    'total_revenue': float(item_df['total_price'].sum()),
                    'average_price': float(item_df['unit_price'].mean())
                }
                analysis['items_analysis'].append(item_analysis)

            company_analysis[int(company_id)] = analysis

        return {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            },
            'data': company_analysis
        }

    @staticmethod
    def get_inventory_analysis():
        """Analisi dell'inventario per fornitore"""
        query = text("""
            SELECT 
                c.id as company_id,
                c.name as company_name,
                i.id as item_id,
                i.name as item_name,
                i.sku,
                i.stock,
                i.stock_unit,
                i.price as current_price,
                i.price_unit
            FROM items i
            JOIN companies c ON i.company_id = c.id
        """)

        result = db.session.execute(query)
        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return {
                'message': 'Nessun dato inventario disponibile',
                'data': {}
            }

        inventory_analysis = {}
        for company_id in df['company_id'].unique():
            company_df = df[df['company_id'] == company_id]
            company_name = company_df['company_name'].iloc[0]

            analysis = {
                'company_name': company_name,
                'total_items': len(company_df),
                'total_stock_value': float((company_df['stock'] * company_df['current_price']).sum()),
                'items_detail': [],
                'low_stock_items': []
            }

            for _, item in company_df.iterrows():
                item_detail = {
                    'item_name': item['item_name'],
                    'sku': item['sku'],
                    'current_stock': int(item['stock']),
                    'stock_unit': item['stock_unit'],
                    'current_price': float(item['current_price']),
                    'price_unit': item['price_unit'],
                    'stock_value': float(item['stock'] * item['current_price'])
                }
                analysis['items_detail'].append(item_detail)

                if item['stock'] < 10:
                    analysis['low_stock_items'].append({
                        'item_name': item['item_name'],
                        'sku': item['sku'],
                        'current_stock': int(item['stock'])
                    })

            inventory_analysis[int(company_id)] = analysis

        return {'data': inventory_analysis}

    @staticmethod
    def get_profit_analysis(start_date=None, end_date=None):
        """Analisi dei profitti per fornitore"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        sales_query = text("""
            SELECT 
                c.id as company_id,
                c.name as company_name,
                i.id as item_id,
                i.name as item_name,
                si.quantity as sold_quantity,
                si.unit_price as selling_price,
                si.total_price as revenue,
                s.date
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            JOIN items i ON si.item_id = i.id
            JOIN companies c ON i.company_id = c.id
            WHERE s.date BETWEEN :start_date AND :end_date
            AND s.status != 'cancelled'
        """)

        purchases_query = text("""
            SELECT 
                c.id as company_id,
                c.name as company_name,
                i.id as item_id,
                i.name as item_name,
                pi.quantity as purchased_quantity,
                pi.unit_price as purchase_price,
                pi.total_price as cost,
                p.date
            FROM purchases p
            JOIN purchase_items pi ON p.id = pi.purchase_id
            JOIN items i ON pi.item_id = i.id
            JOIN companies c ON i.company_id = c.id
            WHERE p.date BETWEEN :start_date AND :end_date
            AND p.status != 'cancelled'
        """)

        sales_df = pd.DataFrame(db.session.execute(sales_query, {
            'start_date': start_date,
            'end_date': end_date
        }).fetchall())

        purchases_df = pd.DataFrame(db.session.execute(purchases_query, {
            'start_date': start_date,
            'end_date': end_date
        }).fetchall())

        profit_analysis = {}
        
        if not sales_df.empty:
            for company_id in sales_df['company_id'].unique():
                company_sales = sales_df[sales_df['company_id'] == company_id]
                company_purchases = purchases_df[purchases_df['company_id'] == company_id] if not purchases_df.empty else pd.DataFrame()
                
                analysis = {
                    'company_name': company_sales['company_name'].iloc[0],
                    'total_revenue': float(company_sales['revenue'].sum()),
                    'total_cost': float(company_purchases['cost'].sum()) if not company_purchases.empty else 0,
                    'items_analysis': []
                }
                
                analysis['gross_profit'] = analysis['total_revenue'] - analysis['total_cost']
                analysis['profit_margin'] = (analysis['gross_profit'] / analysis['total_revenue'] * 100) if analysis['total_revenue'] > 0 else 0
                
                for item_id in company_sales['item_id'].unique():
                    item_sales = company_sales[company_sales['item_id'] == item_id]
                    item_purchases = company_purchases[company_purchases['item_id'] == item_id] if not company_purchases.empty else pd.DataFrame()
                    
                    item_analysis = {
                        'item_name': item_sales['item_name'].iloc[0],
                        'revenue': float(item_sales['revenue'].sum()),
                        'cost': float(item_purchases['cost'].sum()) if not item_purchases.empty else 0,
                        'sold_quantity': int(item_sales['sold_quantity'].sum()),
                        'purchased_quantity': int(item_purchases['purchased_quantity'].sum()) if not item_purchases.empty else 0
                    }
                    
                    item_analysis['profit'] = item_analysis['revenue'] - item_analysis['cost']
                    item_analysis['profit_margin'] = (item_analysis['profit'] / item_analysis['revenue'] * 100) if item_analysis['revenue'] > 0 else 0
                    
                    analysis['items_analysis'].append(item_analysis)
                
                profit_analysis[company_id] = analysis

        return {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            },
            'data': profit_analysis
        }

    @staticmethod
    def _get_daily_sales(df):
        """Calcola le vendite giornaliere"""
        daily_sales = df.groupby('sale_date').agg({
            'total_price': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        return [{
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(revenue),
            'quantity': int(quantity)
        } for date, revenue, quantity in daily_sales.values]

    @staticmethod
    def _get_top_selling_items(df, limit=5):
        """Ottiene i prodotti più venduti"""
        top_items = df.groupby(['item_id', 'item_name', 'sku']).agg({
            'quantity': 'sum',
            'total_price': 'sum'
        }).reset_index().nlargest(limit, 'quantity')
        
        return [{
            'item_name': row['item_name'],
            'sku': row['sku'],
            'quantity': int(row['quantity']),
            'revenue': float(row['total_price'])
        } for _, row in top_items.iterrows()] 

    @staticmethod
    def get_sales_trend(start_date=None, end_date=None):
        """Analisi dell'andamento delle vendite nel tempo"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)   
        if not end_date:
            end_date = datetime.now()

        query = text("""
            SELECT 
                DATE_TRUNC('month', s.date) as month,
                COUNT(DISTINCT s.id) as total_orders,
                SUM(s.total_amount) as total_revenue,
                COUNT(DISTINCT s.customer_name) as unique_customers,
                AVG(s.total_amount) as average_order_value,
                SUM(si.quantity) as total_items_sold
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            WHERE s.date BETWEEN :start_date AND :end_date
            AND s.status != 'cancelled'
            GROUP BY DATE_TRUNC('month', s.date)
            ORDER BY month ASC
        """)

        result = db.session.execute(query, {
            'start_date': start_date,
            'end_date': end_date
        })

        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return {
                'message': 'Nessun dato disponibile per il periodo selezionato',
                'data': {
                    'monthly_trend': [],
                    'summary': {
                        'total_orders': 0,
                        'total_revenue': 0,
                        'total_items_sold': 0,
                        'average_order_value': 0,
                        'unique_customers': 0
                    }
                }
            }

        monthly_trend = [{
            'month': month.strftime('%Y-%m'),
            'total_orders': int(orders),
            'total_revenue': float(revenue),
            'unique_customers': int(customers),
            'average_order_value': float(avg_value),
            'total_items_sold': int(items)
        } for month, orders, revenue, customers, avg_value, items in df.values]

        summary = {
            'total_orders': int(df['total_orders'].sum()),
            'total_revenue': float(df['total_revenue'].sum()),
            'total_items_sold': int(df['total_items_sold'].sum()),
            'average_order_value': float(df['average_order_value'].mean()),
            'unique_customers': int(df['unique_customers'].sum())
        }

        return {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            },
            'data': {
                'monthly_trend': monthly_trend,
                'summary': summary
            }
        } 

    @staticmethod
    def get_top_items_analysis(start_date=None, end_date=None, limit=10):
        """Analisi degli item più venduti"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=365) 
        if not end_date:
            end_date = datetime.now()

        query = text("""
            SELECT 
                i.id as item_id,
                i.name as item_name,
                i.sku,
                c.id as company_id,
                c.name as company_name,
                SUM(si.quantity) as total_quantity,
                SUM(si.total_price) as total_revenue,
                COUNT(DISTINCT s.id) as orders_count,
                AVG(si.unit_price) as average_price,
                i.stock as current_stock
            FROM items i
            JOIN sale_items si ON i.id = si.item_id
            JOIN sales s ON si.sale_id = s.id
            JOIN companies c ON i.company_id = c.id
            WHERE s.date BETWEEN :start_date AND :end_date
            AND s.status != 'cancelled'
            GROUP BY i.id, i.name, i.sku, c.id, c.name, i.stock
            ORDER BY total_quantity DESC
            LIMIT :limit
        """)

        result = db.session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit
        })

        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return {
                'message': 'Nessun dato disponibile per il periodo selezionato',
                'data': {
                    'top_items': [],
                    'summary': {
                        'total_items_sold': 0,
                        'total_revenue': 0,
                        'average_price': 0
                    }
                }
            }

        top_items = [{
            'item_id': int(item_id),
            'item_name': item_name,
            'sku': sku,
            'company': {
                'id': int(company_id),
                'name': company_name
            },
            'total_quantity': int(quantity),
            'total_revenue': float(revenue),
            'orders_count': int(orders),
            'average_price': float(avg_price),
            'current_stock': int(stock)
        } for item_id, item_name, sku, company_id, company_name, quantity, revenue, orders, avg_price, stock in df.values]

        summary = {
            'total_items_sold': int(df['total_quantity'].sum()),
            'total_revenue': float(df['total_revenue'].sum()),
            'average_price': float(df['average_price'].mean())
        }

        return {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            },
            'data': {
                'top_items': top_items,
                'summary': summary
            }
        } 

    @staticmethod
    def get_dashboard_metrics():
        """Ottiene le metriche principali per la dashboard"""
        current_month = datetime.now().replace(day=1)
        last_month = (current_month - timedelta(days=1)).replace(day=1)

        query = text("""
            WITH monthly_metrics AS (
                SELECT 
                    DATE_TRUNC('month', s.date) as month,
                    COUNT(DISTINCT s.id) as total_sales,
                    AVG(s.total_amount) as average_sale,
                    COUNT(DISTINCT CASE WHEN s.status = 'pending' THEN s.id END) as inquiries,
                    COUNT(DISTINCT CASE WHEN s.status IN ('confirmed', 'shipped', 'delivered') THEN s.id END) as invoices
                FROM sales s
                WHERE s.date >= :last_month
                AND s.status != 'cancelled'
                GROUP BY DATE_TRUNC('month', s.date)
            )
            SELECT 
                month,
                total_sales,
                average_sale,
                inquiries,
                invoices,
                LAG(total_sales) OVER (ORDER BY month) as prev_total_sales,
                LAG(inquiries) OVER (ORDER BY month) as prev_inquiries,
                LAG(invoices) OVER (ORDER BY month) as prev_invoices
            FROM monthly_metrics
            ORDER BY month DESC
            LIMIT 2
        """)

        result = db.session.execute(query, {
            'last_month': last_month
        })

        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return {
                'average_sales': {
                    'value': 0,
                    'change': 0
                },
                'total_sales': {
                    'value': 0,
                    'change': 0
                },
                'inquiries': {
                    'value': 0,
                    'change': 0
                },
                'invoices': {
                    'value': 0,
                    'change': 0
                }
            }

        current = df.iloc[0]
        
        return {
            'average_sales': {
                'value': float(current['average_sale']) if pd.notnull(current['average_sale']) else 0,
                'change': 0 
            },
            'total_sales': {
                'value': int(current['total_sales']),
                'change': SalesAnalytics._calculate_percentage_change(
                    current['total_sales'], 
                    current['prev_total_sales']
                )
            },
            'inquiries': {
                'value': int(current['inquiries']),
                'change': SalesAnalytics._calculate_percentage_change(
                    current['inquiries'], 
                    current['prev_inquiries']
                )
            },
            'invoices': {
                'value': int(current['invoices']),
                'change': SalesAnalytics._calculate_percentage_change(
                    current['invoices'], 
                    current['prev_invoices']
                )
            }
        }

    @staticmethod
    def get_hourly_profit_sales():
        """Ottiene l'andamento orario di profitti e vendite"""
        query = text("""
            WITH hourly_sales AS (
                SELECT 
                    DATE_TRUNC('hour', s.date) as hour,
                    SUM(si.total_price) as sales_amount,
                    SUM(
                        CASE 
                            WHEN i.gross_margin IS NOT NULL 
                            THEN si.total_price * (i.gross_margin / 100)
                            ELSE si.total_price * 0.2  -- margine di default del 20%
                        END
                    ) as profit
                FROM sales s
                JOIN sale_items si ON s.id = si.sale_id
                JOIN items i ON si.item_id = i.id
                WHERE s.date >= NOW() - INTERVAL '24 hours'
                AND s.status != 'cancelled'
                GROUP BY DATE_TRUNC('hour', s.date)
                ORDER BY hour ASC
            )
            SELECT 
                hour,
                sales_amount,
                profit,
                EXTRACT(HOUR FROM hour) as hour_number
            FROM hourly_sales
        """)

        result = db.session.execute(query)
        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return {
                'hours': [],
                'sales': [],
                'profit': []
            }

        return {
            'hours': [f"{int(row['hour_number']):02d}:00" for _, row in df.iterrows()],
            'sales': [float(row['sales_amount']) for _, row in df.iterrows()],
            'profit': [float(row['profit']) for _, row in df.iterrows()]
        }

    @staticmethod
    def get_sales_by_brand():
        """Ottiene le vendite totali per brand/company"""
        query = text("""
            SELECT 
                c.name as brand,
                COUNT(DISTINCT s.id) as total_orders,
                SUM(si.total_price) as total_sales
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            JOIN items i ON si.item_id = i.id
            JOIN companies c ON i.company_id = c.id
            WHERE s.status != 'cancelled'
            GROUP BY c.id, c.name
            ORDER BY total_sales DESC
        """)

        result = db.session.execute(query)
        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return {
                'brands': [],
                'sales': []
            }

        return {
            'brands': df['brand'].tolist(),
            'sales': [float(x) for x in df['total_sales'].tolist()]
        }

    @staticmethod
    def get_brand_popularity():
        """Ottiene la popolarità dei brand basata su vendite e recensioni"""
        query = text("""
            WITH brand_metrics AS (
                SELECT 
                    c.id,
                    c.name as brand,
                    COUNT(DISTINCT s.id) as total_orders,
                    SUM(si.quantity) as total_items_sold,
                    COUNT(DISTINCT s.customer_name) as unique_customers
                FROM companies c
                JOIN items i ON c.id = i.company_id
                JOIN sale_items si ON i.id = si.item_id
                JOIN sales s ON si.sale_id = s.id
                WHERE s.status != 'cancelled'
                GROUP BY c.id, c.name
            )
            SELECT 
                brand,
                total_orders,
                total_items_sold,
                unique_customers,
                (total_orders * 0.4 + total_items_sold * 0.4 + unique_customers * 0.2) as popularity_score
            FROM brand_metrics
            ORDER BY popularity_score DESC
        """)

        result = db.session.execute(query)
        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return {
                'brands': [],
                'popularity': []
            }

        max_score = df['popularity_score'].max()
        df['normalized_score'] = (df['popularity_score'] / max_score) * 100

        return {
            'brands': df['brand'].tolist(),
            'popularity': [float(x) for x in df['normalized_score'].tolist()]
        }

    @staticmethod
    def get_brand_average_sales(period='monthly'):
        """Ottiene la media delle vendite per brand (settimanale o mensile)"""
        interval = "week" if period == 'weekly' else "month"
        
        query = text(f"""
            WITH brand_sales AS (
                SELECT 
                    c.name as brand,
                    DATE_TRUNC(:interval, s.date) as period,
                    SUM(si.total_price) as total_sales
                FROM sales s
                JOIN sale_items si ON s.id = si.sale_id
                JOIN items i ON si.item_id = i.id
                JOIN companies c ON i.company_id = c.id
                WHERE s.status != 'cancelled'
                GROUP BY c.name, DATE_TRUNC(:interval, s.date)
            )
            SELECT 
                brand,
                AVG(total_sales) as average_sales
            FROM brand_sales
            GROUP BY brand
            ORDER BY average_sales DESC
        """)

        result = db.session.execute(query, {'interval': interval})
        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return {
                'brands': [],
                'averages': []
            }

        return {
            'brands': df['brand'].tolist(),
            'averages': [float(x) for x in df['average_sales'].tolist()]
        }

    @staticmethod
    def _calculate_percentage_change(current, previous):
        """Calcola la variazione percentuale tra due valori"""
        if pd.isnull(previous) or previous == 0:
            return 0
        return ((current - previous) / previous) * 100 