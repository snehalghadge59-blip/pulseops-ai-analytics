import os
import re
import pandas as pd
from .database import DatabaseManager

class AIAgent:
    def __init__(self, db_manager: DatabaseManager, openai_api_key: str = None, gemini_api_key: str = None):
        self.db = db_manager
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

    def _generate_sql_offline(self, query_text: str) -> str:
        """Deterministic semantic planner: transforms natural language to SQL without requiring API keys."""
        q = query_text.lower().strip()

        # 1. Carrier SLA / Delays
        if any(w in q for w in ["carrier", "transit", "shipping company"]) and any(w in q for w in ["delay", "worst", "slow", "performance", "csat", "sla"]):
            return """
            SELECT 
                d.carrier,
                COUNT(d.delivery_id) AS total_shipments,
                ROUND(AVG(d.transit_days), 1) AS avg_transit_days,
                SUM(d.is_delayed) AS delayed_orders,
                ROUND(AVG(d.is_delayed) * 100, 1) AS delay_rate_pct,
                ROUND(AVG(d.customer_rating), 2) AS avg_csat
            FROM deliveries d
            GROUP BY d.carrier
            ORDER BY delay_rate_pct DESC;
            """

        # 2. Top products / sales / revenue
        if any(w in q for w in ["product", "item", "sku", "best selling", "top selling"]):
            return """
            SELECT 
                p.product_name,
                p.category,
                SUM(oi.quantity) AS units_sold,
                ROUND(SUM(oi.subtotal), 2) AS total_revenue,
                ROUND(SUM(oi.subtotal - (oi.quantity * p.cost_of_goods)), 2) AS gross_profit
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_id
            ORDER BY total_revenue DESC
            LIMIT 10;
            """

        # 3. Category performance / profit margin
        if any(w in q for w in ["category", "categories", "margin", "profitability"]):
            return """
            SELECT 
                p.category,
                COUNT(DISTINCT oi.order_id) AS order_count,
                ROUND(SUM(oi.subtotal), 2) AS revenue,
                ROUND(SUM(oi.quantity * p.cost_of_goods), 2) AS total_cost,
                ROUND(SUM(oi.subtotal - (oi.quantity * p.cost_of_goods)), 2) AS net_profit,
                ROUND(((SUM(oi.subtotal) - SUM(oi.quantity * p.cost_of_goods)) / SUM(oi.subtotal)) * 100, 1) AS margin_pct
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.category
            ORDER BY revenue DESC;
            """

        # 4. Monthly / Quarterly revenue trends
        if any(w in q for w in ["month", "trend", "over time", "timeline", "revenue trend", "sales over time"]):
            return """
            SELECT 
                strftime('%Y-%m', order_date) AS month,
                COUNT(order_id) AS total_orders,
                ROUND(SUM(total_amount), 2) AS monthly_revenue,
                ROUND(AVG(total_amount), 2) AS avg_order_value
            FROM orders
            WHERE order_status = 'Delivered'
            GROUP BY month
            ORDER BY month ASC;
            """

        # 5. Customer Segments / Geo / Cities
        if any(w in q for w in ["city", "state", "region", "geography"]):
            return """
            SELECT 
                c.city,
                c.state,
                COUNT(DISTINCT o.order_id) AS total_orders,
                ROUND(SUM(o.total_amount), 2) AS city_revenue,
                ROUND(AVG(o.total_amount), 2) AS avg_ticket_size
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.city, c.state
            ORDER BY city_revenue DESC
            LIMIT 8;
            """

        if any(w in q for w in ["customer", "segment", "demographic", "b2b", "enterprise"]):
            return """
            SELECT 
                c.segment,
                COUNT(DISTINCT c.customer_id) AS customer_count,
                COUNT(o.order_id) AS orders_placed,
                ROUND(SUM(o.total_amount), 2) AS total_revenue,
                ROUND(AVG(o.total_amount), 2) AS avg_order_spend
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.segment
            ORDER BY total_revenue DESC;
            """

        # 6. Ratings / CSAT / Delay impact
        if any(w in q for w in ["rating", "csat", "review", "satisfaction", "impact"]):
            return """
            SELECT 
                CASE WHEN d.is_delayed = 1 THEN 'Delayed Shipment' ELSE 'On-Time Shipment' END AS delivery_category,
                COUNT(d.delivery_id) AS total_orders,
                ROUND(AVG(d.customer_rating), 2) AS average_csat_score,
                ROUND(AVG(d.transit_days), 1) AS average_transit_days
            FROM deliveries d
            GROUP BY d.is_delayed;
            """

        # 7. Default fallback query: High-level order distribution
        return """
        SELECT 
            strftime('%Y-%m', o.order_date) AS order_month,
            c.segment,
            COUNT(o.order_id) AS total_orders,
            ROUND(SUM(o.total_amount), 2) AS revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY order_month, c.segment
        ORDER BY order_month DESC
        LIMIT 15;
        """

    def _call_llm_for_sql(self, natural_language_query: str) -> str:
        """Invokes LLM if API key is provided, otherwise falls back gracefully."""
        if self.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                prompt = f"""
                You are a senior data architect. Return ONLY an executable SQLite SQL query for this question:
                Question: "{natural_language_query}"

                Database Schema:
                {self.db.get_schema_summary()}

                Rules:
                - Output ONLY pure SQL. No backticks, no explanations.
                - Use only SELECT or WITH statements.
                - Round calculated numbers to 2 decimal places.
                """
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                raw_sql = response.choices[0].message.content.strip()
                return re.sub(r"```(sql)?", "", raw_sql).strip()
            except Exception:
                pass

        return self._generate_sql_offline(natural_language_query)

    def process_query(self, user_question: str) -> dict:
        """Processes natural language question end-to-end with validation, execution, and insight generation."""
        sql_query = self._call_llm_for_sql(user_question)
        
        # Validation & Execution
        df, error = self.db.execute_query(sql_query)
        if error:
            # Self-healing attempt with fallback
            fallback_sql = self._generate_sql_offline(user_question)
            df, error = self.db.execute_query(fallback_sql)
            if not error:
                sql_query = fallback_sql

        insights = self.generate_insights(user_question, sql_query, df)

        return {
            "question": user_question,
            "sql_query": sql_query.strip(),
            "data": df,
            "error": error,
            "insights": insights,
            "chart_type": self._recommend_chart(df)
        }

    def generate_insights(self, question: str, sql: str, df: pd.DataFrame) -> dict:
        """Synthesizes executive insights, detected anomalies, and business recommendations."""
        if df.empty:
            return {
                "summary": "No matching records found for this operational filter.",
                "key_findings": ["Database returned 0 rows."],
                "recommendation": "Try broadening date filters or searching across another segment."
            }

        findings = []
        recommendations = []
        summary = ""

        cols = df.columns.tolist()

        # Check for carrier delays
        if "carrier" in [c.lower() for c in cols]:
            worst_carrier = df.sort_values(by=cols[3] if len(cols) > 3 else cols[1], ascending=False).iloc[0]
            findings.append(f"Carrier **{worst_carrier['carrier']}** leads in delay rate with **{worst_carrier.get('delay_rate_pct', 'N/A')}%** delayed shipments.")
            findings.append(f"Shipments with delay experienced severe CSAT drops, averaging **{worst_carrier.get('avg_csat', 'N/A')} / 5.0**.")
            recommendations.append("Renegotiate SLA contracts with underperforming carriers or reroute critical orders to high-reliability carriers.")
            summary = f"Carrier logistics performance analysis reveals substantial variance in fulfillment reliability."

        # Check for product sales
        elif "product_name" in [c.lower() for c in cols] or "category" in [c.lower() for c in cols]:
            top_row = df.iloc[0]
            entity = top_row.get("product_name") or top_row.get("category")
            rev = top_row.get("total_revenue") or top_row.get("revenue") or 0
            findings.append(f"Top performing entity is **{entity}** driving **${rev:,.2f}** in revenue.")
            if "margin_pct" in cols:
                findings.append(f"Gross profit margin stands at **{top_row.get('margin_pct')}%**.")
            recommendations.append(f"Increase stock allocation for top quartile products to eliminate stockout risks during peak demand cycles.")
            summary = f"Product portfolio distribution indicates healthy top-tier concentration with solid unit margins."

        # Monthly trends
        elif "month" in [c.lower() for c in cols] or "order_month" in [c.lower() for c in cols]:
            total_rev = df.iloc[:, 2].sum() if df.shape[1] > 2 else 0
            findings.append(f"Cumulative tracked revenue across timeline totaled **${total_rev:,.2f}**.")
            findings.append(f"Active order velocity averaged **{int(df.iloc[:, 1].mean()) if df.shape[1] > 1 else 0}** orders per monthly cycle.")
            recommendations.append("Align inventory procurement cycles with seasonal surges to protect cash flow.")
            summary = "Historical order velocity shows sustained expansion with periodic seasonality."

        # Generic quantitative analysis
        else:
            findings.append(f"Retrieved **{len(df)} records** across key operational parameters.")
            num_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(num_cols) > 0:
                highest_val_col = num_cols[-1]
                max_val = df[highest_val_col].max()
                findings.append(f"Peak value for **{highest_val_col}** reached **{max_val:,.2f}**.")
            recommendations.append("Integrate these metrics into automated weekly executive alerting.")
            summary = f"Query executed successfully, surfacing key metric benchmarks."

        return {
            "summary": summary,
            "key_findings": findings,
            "recommendation": recommendations[0] if recommendations else "Continue periodic monitoring."
        }

    def _recommend_chart(self, df: pd.DataFrame) -> str:
        """Determines best chart type based on data shape and column data types."""
        if df.empty or len(df.columns) < 2:
            return "table"
        
        col_names = [c.lower() for c in df.columns]
        if any(c in col_names for c in ["month", "date", "order_date"]):
            return "line"
        elif len(df) <= 10:
            return "bar"
        else:
            return "table"
