"""Dynamic Data Visualizer module generating interactive Plotly figures."""

import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

class DataVisualizer:
    """Generates optimal interactive Plotly charts based on DataFrame metadata and intent."""

    def create_figure(self, df: pd.DataFrame, plan: Dict[str, Any] = None) -> Optional[go.Figure]:
        """Auto-detect column types and build an interactive Plotly figure."""
        if df is None or df.empty or len(df.columns) < 2:
            return None

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        date_cols = [c for c in df.columns if "date" in c.lower() or "year" in c.lower() or "month" in c.lower()]

        # 1. Comparison with baseline (e.g. Department Avg vs Company Avg)
        if len(numeric_cols) >= 2 and len(categorical_cols) >= 1:
            cat_col = categorical_cols[0]
            fig = go.Figure()
            for num_col in numeric_cols[:3]:
                fig.add_trace(go.Bar(
                    x=df[cat_col],
                    y=df[num_col],
                    name=num_col.replace("_", " ").title()
                ))
            fig.update_layout(
                title="Analytical Metric Comparison",
                barmode="group",
                template="plotly_dark",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            return fig

        # 2. Time series / Date trends (Line Chart)
        if date_cols and numeric_cols:
            d_col = date_cols[0]
            num_col = numeric_cols[0]
            fig = px.line(
                df, x=d_col, y=num_col,
                title=f"{num_col.replace('_', ' ').title()} Over Time",
                template="plotly_dark",
                markers=True
            )
            return fig

        # 3. Categorical distribution (Bar or Donut Chart)
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]

            if len(df) <= 5:
                fig = px.pie(
                    df, names=cat_col, values=num_col,
                    title=f"Composition of {num_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}",
                    hole=0.4,
                    template="plotly_dark"
                )
            else:
                fig = px.bar(
                    df, x=cat_col, y=num_col,
                    color=num_col,
                    title=f"{num_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}",
                    template="plotly_dark",
                    text_auto=".2s"
                )
                fig.update_layout(xaxis_tickangle=-45)

            return fig

        return None
