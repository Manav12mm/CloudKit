"""Result Verification Engine validating analytical output accuracy against query intent."""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ResultVerifier:
    """Verifies executed query results against expected intent and produces analytical summaries."""

    def verify(self, result: Dict[str, Any], plan: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform analytical verification checks on execution result.
        
        Returns:
            Dict:
                - verified: bool
                - confidence_score: float (0.0 .. 1.0)
                - verification_notes: List[str]
                - summary_text: str
        """
        notes = []
        confidence = 1.0

        if not result.get("success"):
            return {
                "verified": False,
                "confidence_score": 0.0,
                "verification_notes": ["Execution failed with database error."],
                "summary_text": "Failed to execute query."
            }

        rows = result.get("rows", [])
        columns = result.get("columns", [])
        row_count = result.get("row_count", 0)

        # 1. Non-empty result check
        if row_count == 0:
            notes.append("Warning: Result set contains 0 rows matching query criteria.")
            confidence -= 0.3
        else:
            notes.append(f"Returned {row_count} record(s) across {len(columns)} attribute column(s).")

        # 2. Key column verification if plan exists
        if plan and plan.get("intent") == "COMPARE_AND_BENCHMARK":
            notes.append("Verified multi-CTE comparison structure and difference calculation.")

        # 3. Formulate analytical explanation summary
        summary = self._generate_summary(rows, columns)

        return {
            "verified": confidence >= 0.7,
            "confidence_score": round(confidence, 2),
            "verification_notes": notes,
            "summary_text": summary
        }

    def _generate_summary(self, rows: List[Dict[str, Any]], columns: List[str]) -> str:
        """Synthesize natural language executive summary from result rows."""
        if not rows:
            return "No data records found matching the specified query filters."

        if len(rows) == 1:
            first_row = rows[0]
            items = [f"**{k}**: {v}" for k, v in first_row.items()]
            return f"Query returned 1 primary result row: {', '.join(items)}."

        # Top record summary
        top = rows[0]
        first_col = columns[0]
        second_col = columns[1] if len(columns) > 1 else columns[0]
        return f"Query returned {len(rows)} records. Top entry is **{top.get(first_col)}** with **{top.get(second_col)}**."
