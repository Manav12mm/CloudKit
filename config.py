"""Global configuration module for AI Data Analyst system."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DB_ENGINE_TYPE = os.getenv("DB_ENGINE", "sqlite").lower()  # "sqlite" or "mysql"
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "company_analytics.db"))

MYSQL_HOST = os.getenv("DB_HOST", "localhost")
MYSQL_PORT = int(os.getenv("DB_PORT", "3306"))
MYSQL_USER = os.getenv("DB_USER", "root")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "")
MYSQL_DATABASE = os.getenv("DB_NAME", "company_analytics")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()  # "gemini", "openai", "mock"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL", "gemini-1.5-flash")

# Security & Guardrails
MAX_RESULT_ROWS = int(os.getenv("MAX_RESULT_ROWS", "500"))
MAX_SELF_CORRECT_ATTEMPTS = int(os.getenv("MAX_SELF_CORRECT_ATTEMPTS", "3"))
ALLOWED_SQL_COMMANDS = {"SELECT", "WITH"}
FORBIDDEN_SQL_COMMANDS = {
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", 
    "TRUNCATE", "CREATE", "REPLACE", "GRANT", "REVOKE"
}
