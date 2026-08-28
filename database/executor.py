"""SQL Execution module for running queries safely and capturing timing and metadata."""

import time
import logging
from typing import Dict, Any, List
import pandas as pd
from sqlalchemy import text, Engine
from database.connection import get_db_engine
import config

logger = logging.getLogger(__name__)

class SQLExecutor:
    """Executes validated SQL queries against the database and returns structured results."""

    def __init__(self, engine: Engine = None):
        self.engine = engine or get_db_engine()

    def execute_query(self, sql: str, max_rows: int = None) -> Dict[str, Any]:
        """Execute a SELECT SQL query and return columns, rows, timing, and metadata.
        
        Returns:
            Dict containing:
                - success: bool
                - columns: List[str]
                - rows: List[Dict[str, Any]]
                - row_count: int
                - execution_time_ms: float
                - df: pandas DataFrame (or None if error)
                - error: str (if failed)
        """
        max_rows = max_rows or config.MAX_RESULT_ROWS
        start_time = time.perf_counter()

        # Clean trailing semicolons or spaces
        clean_sql = sql.strip().rstrip(";")

        try:
            with self.engine.connect() as conn:
                df = pd.read_sql_query(text(clean_sql), conn)
                execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

                # Cap results to max_rows
                capped_df = df.head(max_rows)
                records = capped_df.to_dict(orient="records")

                # Sanitize non-JSON types like Timestamps or Decimals
                for r in records:
                    for k, v in r.items():
                        if pd.isna(v):
                            r[k] = None
                        elif hasattr(v, "isoformat"):
                            r[k] = v.isoformat()
                        elif isinstance(v, float) and (v != v):  # NaN check
                            r[k] = None

                return {
                    "success": True,
                    "columns": list(df.columns),
                    "rows": records,
                    "row_count": len(df),
                    "execution_time_ms": execution_time_ms,
                    "df": df,
                    "error": None
                }

        except Exception as e:
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"SQL execution error: {e}")
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": execution_time_ms,
                "df": None,
                "error": str(e)
            }
