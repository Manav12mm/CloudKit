"""AI Sentiment Analysis & Emotion Intelligence Engine for structured dataset query results."""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Lexicon of positive, negative, and emotion-laden keywords
POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "awesome", "fantastic", "wonderful", "outstanding",
    "satisfied", "happy", "ok", "passed", "success", "successful", "positive", "high", "top",
    "best", "approved", "completed", "perfect", "clear", "clean", "verified", "love", "like",
    "developer", "engineer", "architect", "lead", "manager", "specialist", "ai", "cloud"
}

NEGATIVE_WORDS = {
    "bad", "poor", "terrible", "horrible", "awful", "failed", "failure", "unsatisfied", "disappointed",
    "cheating", "fraud", "cancelled", "cancel", "error", "issue", "bug", "delayed", "late",
    "suspended", "rejected", "negative", "low", "worst", "broken", "warning", "risk"
}

class SentimentAnalyzer:
    """Analyzes sentiment polarity (-1.0 to +1.0) and emotion intensity for dataset records."""

    def detect_text_columns(self, columns: List[str], sample_rows: List[Dict[str, Any]]) -> List[str]:
        """Identify columns containing textual descriptions, emails, names, feedback, or statuses."""
        text_cols = []
        for col in columns:
            col_low = col.lower()
            if any(k in col_low for k in ["email", "feedback", "review", "comment", "note", "description", "status", "role", "name", "cheating"]):
                text_cols.append(col)
                continue
            
            # Check sample row values
            if sample_rows and isinstance(sample_rows[0].get(col), str):
                text_cols.append(col)
                
        return text_cols or (columns[:2] if columns else [])

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Compute polarity score (-1.0 to +1.0), label, and emotion intensity for a string."""
        if not text or not isinstance(text, str):
            return {"score": 0.0, "label": "NEUTRAL", "emotion": "NEUTRAL / INFORMATIVE"}

        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return {"score": 0.0, "label": "NEUTRAL", "emotion": "NEUTRAL / INFORMATIVE"}

        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

        total_words = len(words)
        raw_score = (pos_count - neg_count) / max(total_words, 1)

        # Scale compound score between -1.0 and +1.0
        if pos_count > neg_count:
            compound = round(min(0.3 + pos_count * 0.2, 1.0), 2)
            label = "POSITIVE"
            emotion = "JOY / EXCELLENCE"
        elif neg_count > pos_count:
            compound = round(max(-0.3 - neg_count * 0.2, -1.0), 2)
            label = "NEGATIVE"
            emotion = "FRUSTRATION / ISSUES"
        else:
            compound = 0.0
            label = "NEUTRAL"
            emotion = "NEUTRAL / INFORMATIVE"

        return {
            "score": compound,
            "label": label,
            "emotion": emotion,
            "pos_words": pos_count,
            "neg_words": neg_count
        }

    def analyze_dataset(self, rows: List[Dict[str, Any]], columns: List[str]) -> Dict[str, Any]:
        """Perform A to Z Sentiment Suite Analysis across dataset rows."""
        if not rows or not columns:
            return {"has_sentiment": False}

        text_cols = self.detect_text_columns(columns, rows)
        if not text_cols:
            return {"has_sentiment": False}

        target_col = text_cols[0]
        row_sentiments = []
        pos_cnt = 0
        neg_cnt = 0
        neu_cnt = 0
        scores = []

        for idx, row in enumerate(rows):
            val = str(row.get(target_col, ""))
            res = self.analyze_text(val)
            row_sentiments.append({
                "row_index": idx,
                "row_data": row,
                "target_val": val,
                "score": res["score"],
                "label": res["label"],
                "emotion": res["emotion"]
            })

            scores.append(res["score"])
            if res["label"] == "POSITIVE":
                pos_cnt += 1
            elif res["label"] == "NEGATIVE":
                neg_cnt += 1
            else:
                neu_cnt += 1

        total = len(rows)
        pos_pct = round((pos_cnt / total) * 100, 1) if total > 0 else 0
        neg_pct = round((neg_cnt / total) * 100, 1) if total > 0 else 0
        neu_pct = round((neu_cnt / total) * 100, 1) if total > 0 else 0
        avg_score = round(sum(scores) / total, 2) if total > 0 else 0.0

        health_index = f"{pos_pct}% Positive" if pos_cnt >= neg_cnt else f"{neg_pct}% Issues"

        return {
            "has_sentiment": True,
            "target_column": target_col,
            "text_columns": text_cols,
            "total_records": total,
            "average_score": avg_score,
            "health_index": health_index,
            "positive_count": pos_cnt,
            "negative_count": neg_cnt,
            "neutral_count": neu_cnt,
            "positive_pct": pos_pct,
            "negative_pct": neg_pct,
            "neutral_pct": neu_pct,
            "row_sentiments": row_sentiments
        }
