"""Clarification Engine evaluating whether a natural language query is underspecified or ambiguous."""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ClarificationEngine:
    """Detects missing filters, underspecified metrics, or multi-meaning terms before executing queries."""

    def check_ambiguity(self, question: str, schema_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze question for ambiguity.
        
        Returns:
            Dict:
                - is_ambiguous: bool
                - clarification_needed: str or None
                - suggested_options: List[str]
        """
        lowered = question.lower().strip()

        # Vague term: "top employees" without metric
        if ("top employee" in lowered or "best employee" in lowered) and not any(w in lowered for w in ["salary", "performance", "sales", "tenure"]):
            return {
                "is_ambiguous": True,
                "clarification_needed": "Should we rank employees by salary, sales performance, or joining date/tenure?",
                "suggested_options": ["Highest Salary", "Total Sales Revenue", "Earliest Joining Date"]
            }

        # Vague term: "show sales" without timeframe
        if lowered in ["show sales", "get sales", "sales summary"]:
            return {
                "is_ambiguous": True,
                "clarification_needed": "Which timeframe or breakdown would you like for sales?",
                "suggested_options": ["By Region", "By Product Category", "Total Sales Overall"]
            }

        # Clear query
        return {
            "is_ambiguous": False,
            "clarification_needed": None,
            "suggested_options": []
        }
