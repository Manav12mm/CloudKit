"""SQL Security & Validation module ensuring read-only AST compliance."""

import re
import logging
from typing import Tuple, List, Set
import config

logger = logging.getLogger(__name__)

class SQLValidator:
    """Validates generated SQL queries to guarantee security and read-only execution."""

    def __init__(self, allowed_tables: Set[str] = None):
        self.allowed_tables = {t.lower() for t in (allowed_tables or set())}

    def validate(self, sql: str) -> Tuple[bool, str]:
        """Validate SQL query for security and syntax boundaries.
        
        Returns:
            (is_valid: bool, reason: str)
        """
        if not sql or not sql.strip():
            return False, "Query is empty."

        clean_sql = sql.strip()

        # 1. Check for forbidden keywords (DDL/DML mutations)
        sql_upper = clean_sql.upper()
        for forbidden in config.FORBIDDEN_SQL_COMMANDS:
            # Word boundary regex check to prevent matching sub-words like 'CREATED_AT'
            pattern = rf"\b{forbidden}\b"
            if re.search(pattern, sql_upper):
                return False, f"Security Violation: Command '{forbidden}' is forbidden."

        # 2. Must start with SELECT or WITH (CTEs)
        first_word = re.split(r"\s+", clean_sql.lstrip(" ("))[0].upper()
        if first_word not in config.ALLOWED_SQL_COMMANDS:
            return False, f"Invalid Command: Queries must start with SELECT or WITH, found '{first_word}'."

        # 3. Check for multiple statements separated by semicolons (SQL Injection protection)
        # Split by semicolon ignoring inside string literals
        statements = [s.strip() for s in re.split(r";(?=(?:[^'\"`]*['\"`][^'\"`]*['\"`])*[^'\"`]*$)", clean_sql) if s.strip()]
        if len(statements) > 1:
            return False, "Multiple SQL statements detected in a single request."

        # 4. Table check (if schema tables provided)
        if self.allowed_tables:
            referenced_tables = self._extract_tables(clean_sql)
            invalid_tables = referenced_tables - self.allowed_tables
            if invalid_tables:
                return False, f"Unknown Table(s) referenced: {', '.join(invalid_tables)}"

        return True, "Valid SQL query."

    def _extract_tables(self, sql: str) -> Set[str]:
        """Extract table names referenced in FROM and JOIN clauses, excluding defined CTE aliases."""
        sql_lower = sql.lower()
        # Extract CTE names defined in WITH clauses: e.g. "WITH cte_name AS (" or ", cte_name AS ("
        cte_pattern = r"(?:with|,)\s+([a-zA-Z0-9_]+)\s+as\s*\("
        cte_names = set(re.findall(cte_pattern, sql_lower))

        # Extract tables in FROM or JOIN clauses
        pattern = r"\b(?:from|join)\s+([a-zA-Z0-9_]+)"
        matches = set(re.findall(pattern, sql_lower))
        return matches - cte_names
