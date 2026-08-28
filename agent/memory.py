"""Structured Conversation Memory module for tracking conversational turn state and entity context."""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Maintains state, active entity filters, and conversation history across turns."""

    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.active_filters: Dict[str, Any] = {}
        self.last_query_plan: Optional[Dict[str, Any]] = None
        self.last_sql: Optional[str] = None
        self.last_result: Optional[Dict[str, Any]] = None

    def add_turn(self, question: str, sql: str, result: Dict[str, Any], plan: Dict[str, Any] = None):
        """Record a completed conversation turn."""
        turn = {
            "question": question,
            "sql": sql,
            "row_count": result.get("row_count", 0),
            "plan": plan
        }
        self.history.append(turn)
        self.last_sql = sql
        self.last_result = result
        self.last_query_plan = plan

        # Extract context filters (e.g. department)
        lowered = question.lower()
        if "ai" in lowered or "machine learning" in lowered:
            self.active_filters["department"] = "AI & Machine Learning"
        elif "data science" in lowered:
            self.active_filters["department"] = "Data Science & Analytics"

    def get_context_summary(self) -> str:
        """Format active memory summary for prompt injection."""
        if not self.history:
            return "No previous conversation context."

        summary_lines = ["# Conversation Memory Context:"]
        for idx, turn in enumerate(self.history[-3:], 1):  # Last 3 turns
            summary_lines.append(f"Turn {idx}: Question: '{turn['question']}' | Executed SQL: `{turn['sql']}`")

        if self.active_filters:
            filter_str = ", ".join(f"{k}='{v}'" for k, v in self.active_filters.items())
            summary_lines.append(f"Active Entity Context: {filter_str}")

        return "\n".join(summary_lines)

    def clear(self):
        """Reset conversation memory."""
        self.history.clear()
        self.active_filters.clear()
        self.last_query_plan = None
        self.last_sql = None
        self.last_result = None
