"""Automated Benchmark & Evaluation Suite for testing AI Data Analyst across Complexity Levels 1-4."""

import unittest
import time
import logging
from typing import Dict, Any, List

from database.connection import get_db_engine
from database.schema_inspector import SchemaInspector
from database.executor import SQLExecutor
from database.seed_db import seed_database
from agent.validator import SQLValidator
from agent.planner import QueryPlanner
from agent.sql_generator import SQLGenerator
from agent.self_corrector import SelfCorrector
from agent.verifier import ResultVerifier

logger = logging.getLogger(__name__)

class TestAIDataAnalystBenchmark(unittest.TestCase):
    """Evaluation benchmark measuring SQL validity, execution accuracy, and latency across 4 complexity levels."""

    @classmethod
    def setUpClass(cls):
        # 1. Initialize DB and seed test data
        cls.engine = get_db_engine("sqlite")
        seed_database(cls.engine)

        cls.inspector = SchemaInspector(cls.engine)
        cls.schema_text = cls.inspector.get_formatted_schema_for_prompt()
        cls.raw_schema = cls.inspector.get_raw_schema()

        cls.executor = SQLExecutor(cls.engine)
        cls.validator = SQLValidator(set(cls.raw_schema.keys()))
        cls.planner = QueryPlanner(cls.schema_text)
        cls.generator = SQLGenerator(cls.schema_text, dialect="sqlite")
        cls.self_corrector = SelfCorrector(cls.executor, cls.validator, cls.generator)
        cls.verifier = ResultVerifier()

        # Benchmark questions across 4 complexity levels
        cls.benchmark_suite = [
            # Level 1: Basic
            {
                "level": 1,
                "name": "Level 1 - Simple Count",
                "question": "How many employees are in the company?",
                "expected_min_rows": 1
            },
            # Level 2: Intermediate Aggregation
            {
                "level": 2,
                "name": "Level 2 - Group By Aggregation",
                "question": "What is the average salary by department?",
                "expected_min_rows": 3
            },
            # Level 3: Complex Join & Filter
            {
                "level": 3,
                "name": "Level 3 - Multi-Table Join & Filter",
                "question": "Show total sales revenue by region excluding cancelled orders.",
                "expected_min_rows": 1
            },
            # Level 4: Advanced CTE & Temporal Baseline Comparison
            {
                "level": 4,
                "name": "Level 4 - CTE Baseline Comparison",
                "question": "Which department had the highest average salary among employees who joined after 2024, and how does it compare with company average?",
                "expected_min_rows": 1
            },
            # Level 2: Hinglish Name Starting Letter Filter
            {
                "level": 2,
                "name": "Level 2 - Hinglish Name Filter (M)",
                "question": "har department mai m se naam chalu hone wale ka with salary greater than 1000",
                "expected_min_rows": 1
            }
        ]

    def test_run_benchmark_suite(self):
        """Run all benchmark cases and print evaluation metrics report."""
        total_tests = len(self.benchmark_suite)
        valid_sql_count = 0
        execution_success_count = 0
        latencies = []

        print("\n=======================================================")
        print("          AI DATA ANALYST BENCHMARK SUITE              ")
        print("=======================================================\n")

        for test in self.benchmark_suite:
            start_t = time.perf_counter()

            # 1. Plan
            plan = self.planner.create_plan(test["question"])

            # 2. Generate SQL
            sql = self.generator.generate(test["question"], plan=plan)

            # 3. Validate & Execute with Self-Correction
            result, final_sql, attempt_logs = self.self_corrector.execute_with_self_correction(
                question=test["question"],
                initial_sql=sql,
                plan=plan
            )

            latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
            latencies.append(latency_ms)

            # Check validity
            is_valid, v_msg = self.validator.validate(final_sql)
            if is_valid:
                valid_sql_count += 1

            # Check execution
            if result["success"] and result["row_count"] >= test["expected_min_rows"]:
                execution_success_count += 1

            status_icon = "[PASS]" if (is_valid and result["success"]) else "[FAIL]"
            print(f"[{status_icon}] {test['name']} (Level {test['level']})")
            print(f"  Question : {test['question']}")
            print(f"  SQL      : {final_sql.strip()}")
            print(f"  Rows     : {result.get('row_count', 0)} | Latency: {latency_ms} ms")
            print(f"  Attempts : {len(attempt_logs)}\n")

        # Evaluation metrics summary
        sql_validity_rate = round((valid_sql_count / total_tests) * 100, 1)
        execution_accuracy_rate = round((execution_success_count / total_tests) * 100, 1)
        avg_latency_ms = round(sum(latencies) / total_tests, 2)

        print("-------------------------------------------------------")
        print("                 BENCHMARK METRICS SUMMARY             ")
        print("-------------------------------------------------------")
        print(f"  Total Benchmark Tests    : {total_tests}")
        print(f"  SQL Validity Rate        : {sql_validity_rate}% ({valid_sql_count}/{total_tests})")
        print(f"  Execution Accuracy Rate  : {execution_accuracy_rate}% ({execution_success_count}/{total_tests})")
        print(f"  Average Latency          : {avg_latency_ms} ms")
        print("=======================================================\n")

        # Assertions
        self.assertGreaterEqual(sql_validity_rate, 75.0, "SQL Validity Rate below threshold!")
        self.assertGreaterEqual(execution_accuracy_rate, 75.0, "Execution Accuracy Rate below threshold!")

if __name__ == "__main__":
    unittest.main()
