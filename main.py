# Simple LLM‑to‑SQL pipeline demo
"""\
This script demonstrates the minimal end‑to‑end flow described in the
implementation MVP:

1. Accept a natural‑language question from the user.
2. (Mock) call a Large Language Model to generate a SQL statement.
3. Execute the SQL against a MySQL database.
4. Return the result to the console.

The code is intentionally kept straightforward – no complex query‑planning
or multi‑step decomposition – to serve as a starting point for the semester
project. All functions are heavily commented so they can be extended later.
"""

import os
import json
import getpass
from typing import Any, Dict

# ------------------------------------------------------------
# Helper: load DB credentials from environment variables.
# ------------------------------------------------------------
def get_db_config() -> Dict[str, Any]:
    """Return a dictionary with MySQL connection parameters.

    The script expects the following environment variables to be set:
        DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    If any variable is missing, the function will fall back to sensible
    defaults for a local development environment.
    """
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", getpass.getuser()),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "test_db"),
    }

# ------------------------------------------------------------
# Mock LLM – replace with a real API call later.
# ------------------------------------------------------------
def generate_sql(question: str, schema: str) -> str:
    """Generate a SQL query from *question* using a language model.

    For now this function contains a very tiny rule‑based fallback so that the
    script can be run without external APIs. In the full project this function
    will call an LLM (e.g., OpenAI, Anthropic, etc.) and supply *question* and
    *schema* as the prompt.
    """
    # Very naive handling for demo purposes
    lowered = question.lower()
    if "how many" in lowered and "employees" in lowered:
        return "SELECT COUNT(*) FROM employees;"
    if "average salary" in lowered:
        return (
            "SELECT department, AVG(salary) AS avg_salary "
            "FROM employees GROUP BY department;"
        )
    # Fallback – ask the (future) LLM to produce SQL
    # Here we just return a placeholder
    return "-- TODO: call real LLM to generate SQL based on the question"

# ------------------------------------------------------------
# Execute the generated SQL against MySQL.
# ------------------------------------------------------------
def run_sql(sql: str) -> Any:
    """Execute *sql* and return the result set.

    Uses ``pymysql`` which is a pure‑Python MySQL client. If the connection
    cannot be established, an exception is raised – the caller should handle
    it (the main block does a simple try/except and prints the error).
    """
    import pymysql

    cfg = get_db_config()
    connection = pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            # For SELECT statements fetch all rows, otherwise return row count
            if cursor.description:
                result = cursor.fetchall()
            else:
                result = {"affected_rows": cursor.rowcount}
        connection.commit()
        return result
    finally:
        connection.close()

# ------------------------------------------------------------
# Main interactive loop.
# ------------------------------------------------------------
def main():
    print("=== Simple LLM‑SQL Assistant ===")
    # Load a static schema description – in a real system this would be
    # generated dynamically from the MySQL information_schema.
    schema = """\
    tables:
      - employees(id INT, name VARCHAR, department VARCHAR, salary DECIMAL, joining_date DATE)
      - departments(id INT, name VARCHAR)
    """

    while True:
        try:
            question = input("\nEnter your natural‑language question (or 'quit' to exit):\n> ")
        except (EOFError, KeyboardInterrupt):
            break
        if question.strip().lower() in {"quit", "exit"}:
            break

        print("\nGenerating SQL …")
        sql = generate_sql(question, schema)
        print("Generated SQL:\n", sql)

        if sql.strip().startswith("--"):
            print("[Info] SQL generation is a placeholder – implement LLM call.")
            continue

        print("\nExecuting …")
        try:
            result = run_sql(sql)
            print("Result:")
            print(json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"[Error] Failed to run SQL: {e}")

if __name__ == "__main__":
    main()
