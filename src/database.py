import sqlite3
import pandas as pd
import re
import os

class DatabaseManager:
    def __init__(self, db_path="data/ecommerce_logistics.db"):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found at {self.db_path}. Please run data/seed_data.py first.")

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_schema_summary(self) -> str:
        """Returns clean schema definition with columns and foreign keys for LLM prompt context."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r[0] for r in cursor.fetchall()]
        
        schema_text = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            cols = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
            
            cursor.execute(f"PRAGMA foreign_key_list({table});")
            fks = [f"FK: {fk[3]} -> {fk[2]}({fk[4]})" for fk in cursor.fetchall()]
            
            table_desc = f"Table: {table}\n  Columns: {', '.join(cols)}"
            if fks:
                table_desc += f"\n  Foreign Keys: {', '.join(fks)}"
            schema_text.append(table_desc)
            
        conn.close()
        return "\n\n".join(schema_text)

    def validate_sql(self, sql_query: str) -> tuple[bool, str]:
        """Validates that query is strictly read-only and safe."""
        cleaned = sql_query.strip().strip(";").strip()
        
        # Check for forbidden destructive keywords
        forbidden_pattern = r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|ATTACH|DETACH|PRAGMA)\b"
        if re.search(forbidden_pattern, cleaned, re.IGNORECASE):
            return False, "Dangerous query detected. Only SELECT statements are permitted."
            
        if not cleaned.lower().startswith("select") and not cleaned.lower().startswith("with"):
            return False, "Query must start with SELECT or WITH (CTE)."
            
        return True, cleaned

    def execute_query(self, sql_query: str) -> tuple[pd.DataFrame, str]:
        """Safely executes SQL query and returns result as DataFrame."""
        is_safe, processed_query = self.validate_sql(sql_query)
        if not is_safe:
            raise ValueError(processed_query)
            
        conn = self.get_connection()
        try:
            df = pd.read_sql_query(processed_query, conn)
            return df, ""
        except Exception as e:
            return pd.DataFrame(), str(e)
        finally:
            conn.close()
