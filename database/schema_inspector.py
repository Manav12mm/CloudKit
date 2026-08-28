"""Dynamic Database Schema Inspector module."""

import logging
from typing import Dict, List, Any
from sqlalchemy import inspect, text, Engine
from database.connection import get_db_engine

logger = logging.getLogger(__name__)

class SchemaInspector:
    """Dynamically inspects database tables, columns, relationships, and data samples."""

    def __init__(self, engine: Engine = None):
        self.engine = engine or get_db_engine()
        self.inspector = inspect(self.engine)

    def get_raw_schema(self) -> Dict[str, Any]:
        """Extract table schema dictionary containing column metadata and foreign keys."""
        table_names = self.inspector.get_table_names()
        schema_info = {}

        for table in table_names:
            columns = self.inspector.get_columns(table)
            foreign_keys = self.inspector.get_foreign_keys(table)
            primary_keys = self.inspector.get_pk_constraint(table).get("constrained_columns", [])

            cols_meta = []
            for col in columns:
                cols_meta.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "primary_key": col["name"] in primary_keys,
                })

            fks_meta = []
            for fk in foreign_keys:
                fks_meta.append({
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"]
                })

            schema_info[table] = {
                "columns": cols_meta,
                "primary_keys": primary_keys,
                "foreign_keys": fks_meta,
                "sample_values": self._get_sample_values(table, cols_meta)
            }

        return schema_info

    def _get_sample_values(self, table_name: str, columns: List[Dict[str, Any]], limit: int = 3) -> Dict[str, List[Any]]:
        """Fetch up to `limit` distinct sample values for text/category columns to aid LLM grounding."""
        samples = {}
        with self.engine.connect() as conn:
            for col in columns:
                col_name = col["name"]
                col_type = col["type"].upper()
                # Sample text, varchar, char columns
                if any(t in col_type for t in ["VARCHAR", "TEXT", "CHAR", "STRING"]):
                    try:
                        query = text(f"SELECT DISTINCT {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL LIMIT {limit}")
                        result = conn.execute(query).fetchall()
                        vals = [r[0] for r in result if r[0] is not None]
                        if vals:
                            samples[col_name] = vals
                    except Exception as e:
                        logger.debug(f"Could not fetch sample values for {table_name}.{col_name}: {e}")
        return samples

    def get_formatted_schema_for_prompt(self) -> str:
        """Format the database schema into a markdown representation optimized for LLM consumption."""
        raw_schema = self.get_raw_schema()
        lines = ["# Database Schema Overview\n"]

        for table_name, meta in raw_schema.items():
            lines.append(f"## Table: `{table_name}`")
            lines.append("Columns:")
            for col in meta["columns"]:
                pk_flag = " [PK]" if col["primary_key"] else ""
                type_str = col["type"]
                sample_str = ""
                if col["name"] in meta["sample_values"]:
                    samples = meta["sample_values"][col["name"]]
                    sample_str = f" (e.g., {', '.join(map(repr, samples))})"
                lines.append(f"  - `{col['name']}` ({type_str}){pk_flag}{sample_str}")

            if meta["foreign_keys"]:
                lines.append("Foreign Keys / Relationships:")
                for fk in meta["foreign_keys"]:
                    c_cols = ", ".join(fk["constrained_columns"])
                    r_table = fk["referred_table"]
                    r_cols = ", ".join(fk["referred_columns"])
                    lines.append(f"  - `{table_name}.{c_cols}` -> `{r_table}.{r_cols}`")
            lines.append("")

        return "\n".join(lines)
