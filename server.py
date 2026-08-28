"""FastAPI REST API Server bridging React MERN-style Frontend with AI SQL Agent Engine."""

import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

# Ensure root dir is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from database.connection import get_db_engine, get_dialect_name
from database.schema_inspector import SchemaInspector
from database.executor import SQLExecutor
from database.seed_db import seed_database
from agent.validator import SQLValidator
from agent.planner import QueryPlanner
from agent.sql_generator import SQLGenerator
from agent.self_corrector import SelfCorrector
from agent.verifier import ResultVerifier
from analytics.engine import AnalyticsEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SQL_Server")

app = FastAPI(title="AI Data Analyst REST API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    target_table: Optional[str] = None

def get_system():
    engine = get_db_engine()
    dialect = get_dialect_name()
    inspector = SchemaInspector(engine)
    raw_schema = inspector.get_raw_schema()
    schema_prompt_text = inspector.get_formatted_schema_for_prompt()
    executor = SQLExecutor(engine)
    validator = SQLValidator(set(raw_schema.keys()))
    planner = QueryPlanner(schema_prompt_text, raw_schema=raw_schema)
    generator = SQLGenerator(schema_prompt_text, dialect, raw_schema=raw_schema)
    self_corrector = SelfCorrector(executor, validator, generator)
    verifier = ResultVerifier()
    analytics = AnalyticsEngine()

    return {
        "engine": engine,
        "dialect": dialect,
        "raw_schema": raw_schema,
        "schema_text": schema_prompt_text,
        "executor": executor,
        "validator": validator,
        "planner": planner,
        "generator": generator,
        "self_corrector": self_corrector,
        "verifier": verifier,
        "analytics": analytics
    }

@app.on_event("startup")
def startup_event():
    from database.connection import set_custom_sqlite_path
    upload_dir = ROOT_DIR / "uploads"
    custom_db_path = upload_dir / "user_custom_dataset.db"
    if custom_db_path.exists():
        logger.info("Loading active custom user database on startup...")
        set_custom_sqlite_path(str(custom_db_path))
    else:
        engine = get_db_engine()
        seed_database(engine)
        logger.info("Default sample database initialized and seeded.")

@app.get("/api/health")
def health():
    return {"status": "online", "dialect": get_dialect_name()}

@app.get("/api/schema")
def get_schema():
    sys_comp = get_system()
    return {
        "dialect": sys_comp["dialect"],
        "tables": sys_comp["raw_schema"],
        "schema_text": sys_comp["schema_text"]
    }

@app.post("/api/query")
def execute_query(req: QueryRequest):
    q = req.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    start_time = time.perf_counter()
    sys_comp = get_system()

    try:
        # 1. Create Query Plan
        plan = sys_comp["planner"].create_plan(q)

        # 2. Generate Initial SQL
        initial_sql = sys_comp["generator"].generate(q, plan=plan)

        # 3. Execute with Self-Correction
        result, final_sql, attempt_logs = sys_comp["self_corrector"].execute_with_self_correction(
            question=q,
            initial_sql=initial_sql,
            plan=plan
        )

        exec_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        data = result.get("rows", [])
        columns = result.get("columns", [])
        row_count = result.get("row_count", len(data))

        # Perform verifications
        verifier_res = sys_comp["verifier"].verify(result, plan)

        # Dynamic Distinct Options for Universal Ambiguity Resolution
        clarification_data = None
        if plan.get("needs_clarification") and plan.get("dimension_name"):
            dim = plan["dimension_name"]
            target_t = plan.get("target_tables", [])[0] if plan.get("target_tables") else None
            if target_t:
                try:
                    from database.executor import SQLExecutor
                    from database.connection import get_db_engine
                    executor = SQLExecutor(get_db_engine())
                    distinct_res = executor.execute_query(f"SELECT DISTINCT `{dim}` FROM `{target_t}` WHERE `{dim}` IS NOT NULL LIMIT 5;")
                    distinct_vals = [str(r[dim]) for r in distinct_res.get("rows", []) if r.get(dim)]
                    clarification_data = {
                        "needs_clarification": True,
                        "dimension_name": dim,
                        "message": f"Aap kis {dim} ka data analyze karna chahte hain? Ya sabhi {dim}s combine karke dikhau?",
                        "options": [f"🌐 Combine All {dim}s"] + distinct_vals
                    }
                except Exception as e:
                    logger.warning(f"Failed to fetch distinct clarification options: {e}")

        # Compute A to Z Sentiment Analysis Suite
        sentiment_suite = None
        try:
            from agent.sentiment_analyzer import SentimentAnalyzer
            sentiment_suite = SentimentAnalyzer().analyze_dataset(data, columns)
        except Exception as e:
            logger.warning(f"Failed to perform sentiment analysis: {e}")

        return {
            "success": True,
            "question": q,
            "sql": final_sql,
            "data": data,
            "columns": columns,
            "row_count": row_count,
            "execution_time_ms": exec_time_ms,
            "plan": plan,
            "logs": attempt_logs,
            "verifier": verifier_res,
            "clarification": clarification_data,
            "sentiment_suite": sentiment_suite
        }
    except Exception as e:
        logger.error(f"Query execution error: {e}", exc_info=True)
        return {
            "success": False,
            "question": q,
            "error": str(e),
            "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }

@app.post("/api/seed")
def seed_db():
    from database.connection import set_custom_sqlite_path
    upload_dir = ROOT_DIR / "uploads"
    custom_db_path = upload_dir / "user_custom_dataset.db"
    if custom_db_path.exists():
        try:
            os.remove(custom_db_path)
        except Exception:
            pass

    default_db_path = str(ROOT_DIR / "company_analytics.db")
    engine = set_custom_sqlite_path(default_db_path)
    seed_database(engine)
    return {"status": "success", "message": "Database reset to sample benchmark dataset."}

@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    filename = file.filename
    ext = Path(filename).suffix.lower()

    upload_dir = ROOT_DIR / "uploads"
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    if ext == ".csv":
        import pandas as pd
        from database.connection import set_custom_sqlite_path, get_db_engine

        custom_db_path = upload_dir / "user_custom_dataset.db"
        current_engine = get_db_engine()

        # If currently pointing to default sample DB, switch to a fresh custom DB for user files
        if "company_analytics.db" in str(current_engine.url):
            if custom_db_path.exists():
                try:
                    os.remove(custom_db_path)
                except Exception:
                    pass
            engine = set_custom_sqlite_path(str(custom_db_path))
        else:
            engine = current_engine

        table_name = Path(filename).stem.lower().replace(" ", "_").replace("-", "_")
        table_name = "".join(c for c in table_name if c.isalnum() or c == "_")
        if not table_name:
            table_name = "uploaded_dataset"

        df = pd.read_csv(file_path)
        df.to_sql(table_name, engine, if_exists="replace", index=False)

        new_schema = SchemaInspector(engine).get_raw_schema()

        return {
            "success": True,
            "filename": filename,
            "table_name": table_name,
            "row_count": len(df),
            "columns": list(df.columns),
            "message": f"Successfully loaded custom dataset '{filename}' as table '{table_name}' ({len(df)} rows)!",
            "tables": new_schema
        }

    elif ext in [".db", ".sqlite", ".sqlite3"]:
        from database.connection import set_custom_sqlite_path
        new_engine = set_custom_sqlite_path(str(file_path))
        new_schema = SchemaInspector(new_engine).get_raw_schema()

        return {
            "success": True,
            "filename": filename,
            "message": f"Successfully switched database to uploaded SQLite file '{filename}'!",
            "tables": new_schema
        }

    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a .csv or .db / .sqlite file.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
