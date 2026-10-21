import pandas as pd
from .database import DatabaseManager

class AnalyticsEngine:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_executive_kpis(self) -> dict:
        """Returns core operational business KPIs."""
        query = """
        WITH order_metrics AS (
            SELECT 
                COUNT(order_id) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value
            FROM orders
            WHERE order_status = 'Delivered'
        ),
        cost_metrics AS (
            SELECT 
                SUM(oi.quantity * p.cost_of_goods) as total_cogs
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_status = 'Delivered'
        ),
        delivery_metrics AS (
            SELECT 
                COUNT(*) as total_deliveries,
                SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) as on_time_deliveries,
                AVG(customer_rating) as avg_csat
            FROM deliveries
        )
        SELECT 
            om.total_orders,
            om.total_revenue,
            om.avg_order_value,
            cm.total_cogs,
            (om.total_revenue - cm.total_cogs) as gross_profit,
            ((om.total_revenue - cm.total_cogs) / om.total_revenue) * 100 as gross_margin_pct,
            (CAST(dm.on_time_deliveries AS FLOAT) / dm.total_deliveries) * 100 as on_time_rate,
            dm.avg_csat
        FROM order_metrics om, cost_metrics cm, delivery_metrics dm;
        """
        df, err = self.db.execute_query(query)
        if not df.empty:
            res = df.iloc[0].to_dict()
            return {
                "total_revenue": float(res["total_revenue"] or 0),
                "total_orders": int(res["total_orders"] or 0),
                "avg_order_value": float(res["avg_order_value"] or 0),
                "gross_margin_pct": float(res["gross_margin_pct"] or 0),
                "on_time_rate": float(res["on_time_rate"] or 0),
                "avg_csat": float(res["avg_csat"] or 0)
            }
        return {}

    def get_cohort_retention(self) -> pd.DataFrame:
        """Computes customer cohort retention matrix using advanced CTEs."""
        query = """
        WITH customer_first_order AS (
            SELECT 
                customer_id,
                MIN(strftime('%Y-%m', order_date)) as cohort_month
            FROM orders
            GROUP BY customer_id
        ),
        order_periods AS (
            SELECT 
                o.customer_id,
                cfo.cohort_month,
                strftime('%Y-%m', o.order_date) as order_month,
                (CAST(strftime('%Y', o.order_date) AS INTEGER) - CAST(substr(cfo.cohort_month, 1, 4) AS INTEGER)) * 12 +
                (CAST(strftime('%m', o.order_date) AS INTEGER) - CAST(substr(cfo.cohort_month, 6, 2) AS INTEGER)) as period_number
            FROM orders o
            JOIN customer_first_order cfo ON o.customer_id = cfo.customer_id
        ),
        cohort_size AS (
            SELECT 
                cohort_month,
                COUNT(DISTINCT customer_id) as num_cohort_customers
            FROM customer_first_order
            GROUP BY cohort_month
        ),
        cohort_retention AS (
            SELECT 
                op.cohort_month,
                op.period_number,
                COUNT(DISTINCT op.customer_id) as active_customers
            FROM order_periods op
            GROUP BY op.cohort_month, op.period_number
        )
        SELECT 
            cr.cohort_month,
            cs.num_cohort_customers,
            cr.period_number,
            cr.active_customers,
            ROUND((CAST(cr.active_customers AS FLOAT) / cs.num_cohort_customers) * 100, 1) as retention_pct
        FROM cohort_retention cr
        JOIN cohort_size cs ON cr.cohort_month = cs.cohort_month
        WHERE cr.period_number <= 6
        ORDER BY cr.cohort_month, cr.period_number;
        """
        df, _ = self.db.execute_query(query)
        if not df.empty:
            pivot_df = df.pivot(index="cohort_month", columns="period_number", values="retention_pct").fillna(0)
            return pivot_df
        return pd.DataFrame()

    def get_rfm_segments(self) -> pd.DataFrame:
        """Computes RFM (Recency, Frequency, Monetary) segmentation using SQL Window Functions."""
        query = """
        WITH rfm_raw AS (
            SELECT 
                customer_id,
                MAX(order_date) as last_order_date,
                COUNT(order_id) as frequency,
                SUM(total_amount) as monetary
            FROM orders
            GROUP BY customer_id
        ),
        rfm_scored AS (
            SELECT 
                customer_id,
                frequency,
                monetary,
                NTILE(4) OVER (ORDER BY last_order_date ASC) as r_score,
                NTILE(4) OVER (ORDER BY frequency ASC) as f_score,
                NTILE(4) OVER (ORDER BY monetary ASC) as m_score
            FROM rfm_raw
        ),
        rfm_segmented AS (
            SELECT 
                customer_id,
                frequency,
                monetary,
                r_score, f_score, m_score,
                CASE 
                    WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
                    WHEN f_score >= 3 THEN 'Loyal Customers'
                    WHEN r_score >= 3 AND f_score < 3 THEN 'Potential Loyalists'
                    WHEN r_score <= 2 AND f_score >= 2 THEN 'At Risk'
                    ELSE 'Hibernating / Needs Attention'
                END as customer_tier
            FROM rfm_scored
        )
        SELECT 
            customer_tier,
            COUNT(customer_id) as customer_count,
            ROUND(AVG(frequency), 1) as avg_frequency,
            ROUND(AVG(monetary), 2) as avg_monetary_spend,
            ROUND(SUM(monetary), 2) as total_tier_revenue
        FROM rfm_segmented
        GROUP BY customer_tier
        ORDER BY total_tier_revenue DESC;
        """
        df, _ = self.db.execute_query(query)
        return df

    def get_carrier_sla_performance(self) -> pd.DataFrame:
        """Analyzes logistics carriers, transit time, SLA breach rate, and CSAT impact."""
        query = """
        SELECT 
            d.carrier,
            COUNT(d.delivery_id) as total_shipments,
            ROUND(AVG(d.transit_days), 1) as avg_transit_days,
            SUM(d.is_delayed) as delayed_shipments,
            ROUND((CAST(SUM(d.is_delayed) AS FLOAT) / COUNT(d.delivery_id)) * 100, 1) as delay_rate_pct,
            ROUND(AVG(d.customer_rating), 2) as avg_csat_score,
            ROUND(SUM(CASE WHEN d.is_delayed = 1 THEN o.freight_cost * 0.40 ELSE 0 END), 2) as estimated_delay_penalty_cost
        FROM deliveries d
        JOIN orders o ON d.order_id = o.order_id
        GROUP BY d.carrier
        ORDER BY delay_rate_pct DESC;
        """
        df, _ = self.db.execute_query(query)
        return df

    def get_category_profitability(self) -> pd.DataFrame:
        """Calculates product category revenue, COGS, and gross margin percentage."""
        query = """
        SELECT 
            p.category,
            COUNT(DISTINCT oi.order_id) as orders_count,
            SUM(oi.quantity) as units_sold,
            ROUND(SUM(oi.subtotal), 2) as revenue,
            ROUND(SUM(oi.quantity * p.cost_of_goods), 2) as cogs,
            ROUND(SUM(oi.subtotal) - SUM(oi.quantity * p.cost_of_goods), 2) as gross_profit,
            ROUND(((SUM(oi.subtotal) - SUM(oi.quantity * p.cost_of_goods)) / SUM(oi.subtotal)) * 100, 1) as margin_pct
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC;
        """
        df, _ = self.db.execute_query(query)
        return df
