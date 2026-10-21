import unittest
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import DatabaseManager
from src.analytics import AnalyticsEngine
from src.agent import AIAgent

class TestPulseOpsSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = "data/ecommerce_logistics.db"
        cls.db = DatabaseManager(cls.db_path)
        cls.analytics = AnalyticsEngine(cls.db)
        cls.agent = AIAgent(cls.db)

    def test_database_connection_and_schema(self):
        schema = self.db.get_schema_summary()
        self.assertIn("Table: orders", schema)
        self.assertIn("Table: customers", schema)
        self.assertIn("Table: products", schema)
        self.assertIn("Table: deliveries", schema)

    def test_sql_safety_validator(self):
        # Unsafe queries must be blocked
        is_safe, msg = self.db.validate_sql("DROP TABLE orders;")
        self.assertFalse(is_safe)
        
        is_safe, msg = self.db.validate_sql("DELETE FROM customers WHERE customer_id='1';")
        self.assertFalse(is_safe)

        # Safe queries must pass
        is_safe, msg = self.db.validate_sql("SELECT * FROM products LIMIT 5;")
        self.assertTrue(is_safe)

    def test_executive_kpis(self):
        kpis = self.analytics.get_executive_kpis()
        self.assertIn("total_revenue", kpis)
        self.assertGreater(kpis["total_revenue"], 0)
        self.assertGreater(kpis["gross_margin_pct"], 0)
        self.assertGreater(kpis["on_time_rate"], 0)

    def test_ai_agent_nlp_query(self):
        result = self.agent.process_query("Which carrier has the worst delivery delay rate?")
        self.assertEqual(result["error"], "")
        self.assertFalse(result["data"].empty)
        self.assertIn("carrier", result["data"].columns)
        self.assertGreater(len(result["insights"]["key_findings"]), 0)

if __name__ == "__main__":
    unittest.main()
