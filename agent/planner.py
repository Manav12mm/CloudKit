"""Query Planner module for decomposing natural language into structured analytical query plans."""

import json
import re
import logging
from typing import Dict, Any, List
import config

logger = logging.getLogger(__name__)

class QueryPlanner:
    """Decomposes natural language requests into structured execution query plans."""

    def __init__(self, schema_text: str = "", raw_schema: Dict[str, Any] = None):
        self.schema_text = schema_text
        self.raw_schema = raw_schema or {}

    def create_plan(self, question: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Analyze natural language prompt (in any language) and generate a structured Query Plan."""
        lowered = question.lower()

        # Deterministic analytical intent classification
        intent = "UNKNOWN"
        complexity_level = 1
        requires_cte = False
        target_tables = []
        metrics = []
        group_by = []
        filters = []
        plan_steps = []

        # Dynamic table resolution from raw_schema
        if self.raw_schema:
            for table_name, meta in self.raw_schema.items():
                t_lower = table_name.lower()
                # Check if table name or any of its columns match question terms
                if t_lower in lowered or any(t_part in lowered for t_part in t_lower.split("_")):
                    target_tables.append(table_name)
                else:
                    for col in meta.get("columns", []):
                        c_lower = col["name"].lower()
                        if c_lower in lowered or any(c_part in lowered for c_part in c_lower.split("_") if len(c_part) > 2):
                            target_tables.append(table_name)
                            break
        
        # Fallback table keyword matching
        if not target_tables:
            if any(w in lowered for w in ["employee", "employee_name", "salary"]):
                target_tables.append("employees")
            elif any(w in lowered for w in ["department", "dept"]):
                target_tables.append("departments")
            elif any(w in lowered for w in ["order", "sales", "revenue"]):
                target_tables.append("orders")
            elif self.raw_schema:
                target_tables = list(self.raw_schema.keys())[:2]

        target_tables = list(dict.fromkeys(target_tables))

        # Complexity & Intent classification
        if any(w in lowered for w in ["compare", "growth", "versus", "vs", "difference", "quarterly"]):
            intent = "COMPARE_AND_BENCHMARK"
            complexity_level = 4 if ("yoy" in lowered or "growth" in lowered or "quarter" in lowered) else 3
            requires_cte = True
            plan_steps = [
                "Decompose query into CTEs for group metrics and baseline metrics.",
                "Calculate aggregations filtered by date/category boundaries.",
                "Join target CTE with benchmark CTE and compute variance/difference."
            ]
        elif len(target_tables) > 1 or "highest average" in lowered or "top" in lowered or "subquery" in lowered:
            intent = "MULTI_TABLE_AGGREGATION"
            complexity_level = 3
            requires_cte = "highest average" in lowered or "compare" in lowered
            plan_steps = [
                f"Join tables: {', '.join(target_tables)}.",
                "Apply relational filters and grouping.",
                "Compute aggregated metrics and order top N results."
            ]
        elif any(w in lowered for w in ["average", "avg", "total", "sum", "count", "how many"]):
            intent = "AGGREGATION"
            complexity_level = 2 if ("group by" in lowered or "by department" in lowered or "per" in lowered) else 1
            plan_steps = [
                f"Query table {target_tables[0] if target_tables else 'target'}.",
                "Apply summary aggregation functions."
            ]
        else:
            intent = "BASIC_SELECTION"
            complexity_level = 1
            plan_steps = ["Filter and return requested matching records."]

        # Extracted filters & metrics summary
        if "joining_date" in lowered or "2024" in lowered or "2025" in lowered:
            filters.append("date_boundary_filter")
        if "cancel" in lowered or "returned" in lowered:
            filters.append("order_status != 'Cancelled'")

        if "salary" in lowered:
            metrics.append("AVG(salary)")
        if "revenue" in lowered or "sales" in lowered:
            metrics.append("SUM(quantity * unit_price * (1 - discount))")
        if "count" in lowered or "how many" in lowered:
            metrics.append("COUNT(*)")

        # Universal Categorical Ambiguity Detector across ANY Dataset (Branch, Category, Region, Segment, Status)
        needs_clarification = False
        clarification_message = ""
        dimension_name = None
        options = []

        if self.raw_schema:
            for t_name, t_meta in self.raw_schema.items():
                cols = [c["name"] for c in t_meta.get("columns", [])]
                for c in cols:
                    c_low = c.lower()
                    if any(dim in c_low for dim in ["department", "dept", "branch", "category", "region", "segment", "status", "role", "course"]):
                        dimension_name = c
                        break
                if dimension_name:
                    break

        if dimension_name and any(w in lowered for w in ["top", "show", "list", "all", "get", "average", "highest", "give", "sare", "chahiye", "bande", "banda", "log", "dikhao", "batao", "dedo", "merko", "mujhe"]):
            # Check if prompt specifies an explicit letter filter or specific category value
            explicit_val_mentioned = bool(re.search(r"\b[a-zA-Z]\b\s+(?:naam|name|se|wala|ke)", lowered)) or any(val in lowered for val in ["ai", "cse", "ece", "csit", "cloud", "electronics", "furniture", "appliances", "north", "south", "east", "west", "active", "cancelled"])
            if not explicit_val_mentioned:
                needs_clarification = True
                clarification_message = f"Aap kis {dimension_name} ka data analyze karna chahte hain? Ya sabhi {dimension_name}s combine karke dikhau?"
                options = [f"Combine All {dimension_name}s", "Filter by specific choice"]

        plan = {
            "question": question,
            "complexity_level": complexity_level,
            "intent": intent,
            "target_tables": target_tables,
            "metrics": metrics,
            "group_by": group_by,
            "filters": filters,
            "requires_cte": requires_cte,
            "plan_steps": plan_steps,
            "needs_clarification": needs_clarification,
            "clarification_message": clarification_message,
            "dimension_name": dimension_name,
            "options": options
        }

        logger.info(f"Query plan generated: Intent={intent}, Level={complexity_level}, Tables={target_tables}")
        return plan
