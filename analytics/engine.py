"""Analytics Engine module for calculating statistical metrics, growth rates, and derived insights."""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Computes advanced analytics, percentage contributions, and statistical trends on result sets."""

    def compute_insights(self, df: pd.DataFrame, plan: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compute key data metrics and derived statistical insights from execution DataFrame.
        
        Returns:
            Dict:
                - record_count: int
                - numeric_summary: Dict[str, Dict[str, float]]
                - top_contributor: Dict[str, Any]
                - insights_list: List[str]
        """
        if df is None or df.empty:
            return {
                "record_count": 0,
                "numeric_summary": {},
                "top_contributor": None,
                "insights_list": ["No records available for analytics."]
            }

        insights = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()

        numeric_summary = {}
        for col in numeric_cols:
            total = float(df[col].sum())
            avg = float(df[col].mean())
            max_val = float(df[col].max())
            min_val = float(df[col].min())

            numeric_summary[col] = {
                "total": round(total, 2),
                "mean": round(avg, 2),
                "max": round(max_val, 2),
                "min": round(min_val, 2)
            }

            if "salary" in col.lower() or "avg" in col.lower() or "revenue" in col.lower():
                insights.append(f"**{col}**: Average = {round(avg, 2):,}, Highest = {round(max_val, 2):,}.")

        top_contributor = None
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            top_row = df.sort_values(by=num_col, ascending=False).iloc[0]
            top_contributor = {
                "name": str(top_row[cat_col]),
                "metric": num_col,
                "value": float(top_row[num_col])
            }
            insights.append(f"Highest performing `{cat_col}` is **{top_contributor['name']}** with **{top_contributor['value']:,}** `{num_col}`.")

        return {
            "record_count": len(df),
            "numeric_summary": numeric_summary,
            "top_contributor": top_contributor,
            "insights_list": insights
        }
