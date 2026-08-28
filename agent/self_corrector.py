"""Self-Correction Engine for capturing database execution errors and auto-repairing SQL."""

import logging
from typing import Dict, Any, Tuple, List
from database.executor import SQLExecutor
from agent.validator import SQLValidator
import config

logger = logging.getLogger(__name__)

class SelfCorrector:
    """Interprets database syntax/schema runtime errors and re-prompts for auto-correction."""

    def __init__(self, executor: SQLExecutor, validator: SQLValidator, generator):
        self.executor = executor
        self.validator = validator
        self.generator = generator

    def execute_with_self_correction(
        self,
        question: str,
        initial_sql: str,
        plan: Dict[str, Any] = None,
        max_attempts: int = None
    ) -> Tuple[Dict[str, Any], str, List[Dict[str, Any]]]:
        """Execute SQL with auto-repair loop upon runtime failure.
        
        Returns:
            Tuple: (final_execution_result, final_sql, attempt_logs)
        """
        max_attempts = max_attempts or config.MAX_SELF_CORRECT_ATTEMPTS
        attempt_logs = []
        current_sql = initial_sql
        result = {"success": False, "columns": [], "rows": [], "row_count": 0, "execution_time_ms": 0, "df": None, "error": "Execution or validation failed"}

        for attempt in range(1, max_attempts + 1):
            logger.info(f"Execution Attempt {attempt}/{max_attempts}: SQL=`{current_sql}`")

            # 1. Security & AST Validation
            is_valid, validation_msg = self.validator.validate(current_sql)
            if not is_valid:
                attempt_logs.append({
                    "attempt": attempt,
                    "sql": current_sql,
                    "status": "Validation Failed",
                    "error": validation_msg
                })
                # Re-generate fixing validation failure
                current_sql = self.generator._generate_rule_engine(question, plan)
                continue

            # 2. Database Execution
            result = self.executor.execute_query(current_sql)

            if result["success"]:
                attempt_logs.append({
                    "attempt": attempt,
                    "sql": current_sql,
                    "status": "Success",
                    "error": None,
                    "row_count": result["row_count"],
                    "execution_time_ms": result["execution_time_ms"]
                })
                return result, current_sql, attempt_logs

            # Execution Failed -> Record Error & Attempt Self-Correction
            error_msg = result["error"]
            attempt_logs.append({
                "attempt": attempt,
                "sql": current_sql,
                "status": "Execution Error",
                "error": error_msg
            })

            logger.warning(f"Attempt {attempt} failed: {error_msg}. Triggering repair...")

            # 3. Construct Feedback Prompt & Re-generate SQL
            correction_feedback = f"Error in previous SQL: {error_msg}. Please fix syntax or column names."
            current_sql = self.generator.generate(
                question=question,
                plan=plan,
                context=correction_feedback
            )

        # If all retries exhausted, return last result
        return result, current_sql, attempt_logs
