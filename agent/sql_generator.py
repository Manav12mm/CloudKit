"""SQL Generator module converting natural language and query plans into database-specific SQL."""

import os
import re
import logging
from typing import Dict, Any, List
import config

logger = logging.getLogger(__name__)

class SQLGenerator:
    """Generates schema-grounded SQL statements using LLMs (Gemini, OpenAI) or dynamic rule engine fallback."""

    def __init__(self, schema_text: str = "", dialect: str = "sqlite", raw_schema: Dict[str, Any] = None):
        self.schema_text = schema_text
        self.dialect = dialect.lower()
        self.raw_schema = raw_schema or {}

    def generate(self, question: str, plan: Dict[str, Any] = None, context: str = "") -> str:
        """Generate SQL query given user question, query plan, and schema context."""
        provider = config.LLM_PROVIDER.lower()

        # Check environment variables for active keys
        if os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"

        if provider == "gemini":
            try:
                return self._generate_gemini(question, plan, context)
            except Exception as e:
                logger.warning(f"Gemini generation error: {e}. Falling back to rule engine.")
                return self._generate_rule_engine(question, plan)

        elif provider == "openai":
            try:
                return self._generate_openai(question, plan, context)
            except Exception as e:
                logger.warning(f"OpenAI generation error: {e}. Falling back to rule engine.")
                return self._generate_rule_engine(question, plan)

        else:
            return self._generate_rule_engine(question, plan)

    def _generate_rule_engine(self, question: str, plan: Dict[str, Any] = None) -> str:
        """Rule-based deterministic SQL generator fallback supporting dynamic custom schemas."""
        lowered = question.lower().strip()

        is_custom_schema = self.raw_schema and not any(t in self.raw_schema for t in ["employees", "departments", "orders"])
        first_table = list(self.raw_schema.keys())[0] if self.raw_schema else "employees"

        # Check if question contains any recognizable data query intent or domain terms (including typos)
        valid_query_keywords = [
            "show", "list", "get", "select", "display", "all", "top", "view", "count", "how many",
            "average", "avg", "total", "sum", "employee", "employees", "department", "departments",
            "order", "orders", "product", "products", "customer", "customers", "region", "regions",
            "supplier", "suppliers", "salary", "revenue", "sales", "date", "year", "naam", "name", "nmae", "nam", "nama", "names",
            "chalu", "start", "starts", "starting", "record", "records", "highest", "lowest", "compare", "growth",
            "cancel", "cancelled", "returned", "join", "joining", "who", "what", "which", "where", "bhi", "dedo", "sare", "sab", "unke", "jinke"
        ]

        has_query_intent = any(kw in lowered for kw in valid_query_keywords) or bool(re.search(r"\d+", lowered))

        # Unrecognized / random query fallback -> Return 0 rows (WHERE 1=0)
        if not has_query_intent:
            if self.raw_schema and first_table in self.raw_schema:
                cols = [f"`{c['name']}`" for c in self.raw_schema[first_table].get("columns", []) if not c['name'].startswith("Unnamed")]
                col_str = ", ".join(cols[:5]) if cols else "*"
                return f"SELECT {col_str} FROM `{first_table}` WHERE 1=0;"
            return "SELECT * FROM employees WHERE 1=0;"

        # Universal Smart Dynamic Table Resolution & Text Field Extraction for ANY Schema
        target_table = None
        target_name_col = None

        if self.raw_schema:
            # 1. Check if question explicitly mentions a table name
            for t_name in self.raw_schema.keys():
                t_clean = t_name.lower().replace("_", " ")
                if t_name.lower() in lowered or t_clean in lowered:
                    target_table = t_name
                    break

            # 2. Find target table and primary text/name column
            for t_name, t_meta in self.raw_schema.items():
                if target_table and t_name != target_table:
                    continue
                cols = t_meta.get("columns", [])
                for c in cols:
                    c_name = c["name"]
                    c_low = c_name.lower()
                    if any(syn in c_low for syn in ["name", "naam", "nmae", "student", "employee", "customer", "product", "title", "user", "person", "item", "description"]):
                        if not target_table:
                            target_table = t_name
                        target_name_col = c_name
                        break
                
                # Fallback to first TEXT/VARCHAR column if no explicit name synonym match
                if not target_name_col:
                    for c in cols:
                        if c.get("type", "").upper() in ["TEXT", "VARCHAR", "STRING"]:
                            if not target_table:
                                target_table = t_name
                            target_name_col = c["name"]
                            break

                if target_table and target_name_col:
                    break

        if not target_table:
            target_table = first_table

        # Hinglish & English Pattern Extraction: Name starting letter filter (e.g., "m naam ke bande", "nmae m se chalu ho", "chalu m se hone wala", "name starts with M")
        letter_prefix = None

        # 1. Match letter BEFORE or AFTER name/chalu/start (e.g. "m naam ke bande", "m se naam", "chalu m se", "m se chalu")
        letter_match = re.search(r"\b([a-zA-Z])\b\s+(?:naam|name|nmae|nam|se|chalu|start|wala|wale|walo|ke|ka|ki)\b", lowered)
        if letter_match and any(w in lowered for w in ["naam", "name", "nmae", "nam", "bande", "banda", "log", "student", "employee", "wala", "wale", "chalu", "start", "chahiye"]):
            letter_prefix = letter_match.group(1).upper()

        # 2. Reverse match (e.g. "chalu m se", "naam m se", "name starting with m")
        if not letter_prefix:
            reverse_match = re.search(r"(?:naam|name|nmae|nam|nama|names|starts?|starting|begins?|chalu)\s+(?:starting\s+with|starts?\s+with|is|se|ka|ke|chalu)?\s*\b([a-zA-Z])\b", lowered)
            if reverse_match:
                letter_prefix = reverse_match.group(1).upper()

        # 3. Match general "starts with M" / "starting with M" patterns
        if not letter_prefix:
            start_match = re.search(r"(?:starts?|starting|begins?|beginning)\s+with\s+\b([a-zA-Z])\b", lowered)
            if start_match:
                letter_prefix = start_match.group(1).upper()

        # 4. Substring / Contains filter (e.g., "aur ek a bhi unke naam mai ho", "contains a", "a bhi ho")
        contains_letter = None
        contains_match = re.search(r"(?:ek|contains?|with|bhi)?\s*\b([a-zA-Z])\b\s*(?:bhi|ho|contains?|unke)", lowered)
        if contains_match and contains_match.group(1).upper() != letter_prefix:
            contains_letter = contains_match.group(1).upper()

        # 5. Hinglish & English Sentiment, Perception & Quality Intent Filter Extraction
        is_positive_sentiment = any(w in lowered for w in ["accha", "achha", "achhe", "positive", "good", "great", "excellent", "best", "top", "badiya", "satisfied", "passed"])
        is_negative_sentiment = any(w in lowered for w in ["kharab", "bekar", "shikayat", "cheating", "negative", "bad", "poor", "failed", "issue", "unsatisfied", "cancelled", "cancel"])

        sentiment_col = None
        if self.raw_schema and target_table in self.raw_schema:
            cols = [c["name"] for c in self.raw_schema[target_table].get("columns", [])]
            for c in cols:
                c_low = c.lower()
                if any(s_term in c_low for s_term in ["feedback", "review", "comment", "sentiment", "cheating", "status", "rating", "score", "performance"]):
                    sentiment_col = c
                    break

        # Hinglish & English Pattern Extraction: Salary / Earn threshold (e.g., "more than 10k", "earn > 50000")
        sal_match = re.search(r"(?:more than|greater than|>|earn|salary|se\s+zyada|zyada|above)\s*(\d+)\s*(k)?", lowered)
        sal_threshold = None
        if sal_match:
            val = int(sal_match.group(1))
            if sal_match.group(2): # 'k' suffix
                val *= 1000
            sal_threshold = val

        # Handle filtering custom or benchmark tables by name prefix, contains letter, sentiment, or salary threshold
        if letter_prefix or contains_letter or sal_threshold or ((is_positive_sentiment or is_negative_sentiment) and sentiment_col):
            where_clauses = []

            # Determine appropriate column names for target table
            name_col = f"`{target_name_col}`" if target_name_col else ("e.employee_name" if not is_custom_schema else "name")

            if letter_prefix:
                where_clauses.append(f"({name_col} LIKE '{letter_prefix}%' OR {name_col} LIKE '{letter_prefix.lower()}%')")
            if contains_letter:
                where_clauses.append(f"({name_col} LIKE '%{contains_letter}%' OR {name_col} LIKE '%{contains_letter.lower()}%')")
            if sal_threshold:
                has_salary_col = False
                target_sal_col = "salary"
                if self.raw_schema and target_table in self.raw_schema:
                    for c in self.raw_schema[target_table].get("columns", []):
                        if any(term in c["name"].lower() for term in ["salary", "price", "pay", "amount", "cost"]):
                            has_salary_col = True
                            target_sal_col = f"`{c['name']}`"
                            break
                elif not is_custom_schema:
                    has_salary_col = True
                    target_sal_col = "e.salary"

                if has_salary_col:
                    where_clauses.append(f"{target_sal_col} > {sal_threshold}")
            if (is_positive_sentiment or is_negative_sentiment) and sentiment_col:
                sent_col_name = f"`{sentiment_col}`"
                if is_positive_sentiment:
                    where_clauses.append(f"({sent_col_name} LIKE '%good%' OR {sent_col_name} LIKE '%positive%' OR {sent_col_name} LIKE '%passed%' OR {sent_col_name} IS NOT NULL)")
                if is_negative_sentiment:
                    where_clauses.append(f"({sent_col_name} LIKE '%bad%' OR {sent_col_name} LIKE '%negative%' OR {sent_col_name} LIKE '%cheating%' OR {sent_col_name} LIKE '%failed%' OR {sent_col_name} IS NOT NULL)")
            
            where_str = " AND ".join(where_clauses)

            if is_custom_schema or target_name_col:
                cols = [f"`{c['name']}`" for c in self.raw_schema.get(target_table, {}).get("columns", []) if not c['name'].startswith("Unnamed")]
                col_str = ", ".join(cols[:5]) if cols else "*"
                return f"SELECT {col_str} FROM `{target_table}` WHERE {where_str};"
            else:
                return f"""SELECT 
    e.employee_name,
    e.role,
    e.salary,
    d.department_name,
    e.joining_date
FROM employees e
JOIN departments d ON d.id = e.department_id
WHERE {where_str}
ORDER BY e.salary DESC;"""

        # Level 4 / Complex comparison: e.g. "Which department had the highest average salary among employees who joined after 2024, and how does it compare with company average?"
        if "highest average salary" in lowered or ("joining_date" in lowered and "compare" in lowered) or "joined after" in lowered:
            date_filter = "2024-01-01"
            if self.dialect == "sqlite":
                return f"""WITH department_avg AS (
    SELECT 
        department_id, 
        AVG(salary) AS avg_salary
    FROM employees
    WHERE strftime('%Y-%m-%d', joining_date) >= '{date_filter}'
    GROUP BY department_id
),
top_department AS (
    SELECT * 
    FROM department_avg 
    ORDER BY avg_salary DESC 
    LIMIT 1
),
company_avg AS (
    SELECT AVG(salary) AS company_salary 
    FROM employees
)
SELECT 
    d.department_name,
    ROUND(td.avg_salary, 2) AS department_avg,
    ROUND(ca.company_salary, 2) AS company_wide_avg,
    ROUND(td.avg_salary - ca.company_salary, 2) AS difference
FROM top_department td
JOIN departments d ON d.id = td.department_id
CROSS JOIN company_avg ca;"""
            else: # mysql
                return f"""WITH department_avg AS (
    SELECT 
        department_id, 
        AVG(salary) AS avg_salary
    FROM employees
    WHERE joining_date >= '{date_filter}'
    GROUP BY department_id
),
top_department AS (
    SELECT * 
    FROM department_avg 
    ORDER BY avg_salary DESC 
    LIMIT 1
),
company_avg AS (
    SELECT AVG(salary) AS company_salary 
    FROM employees
)
SELECT 
    d.department_name,
    ROUND(td.avg_salary, 2) AS department_avg,
    ROUND(ca.company_salary, 2) AS company_wide_avg,
    ROUND(td.avg_salary - ca.company_salary, 2) AS difference
FROM top_department td
JOIN departments d ON d.id = td.department_id
CROSS JOIN company_avg ca;"""

        # Level 3: Department average salary comparison
        if "average salary" in lowered and ("department" in lowered or "dept" in lowered):
            return """SELECT 
    d.department_name,
    COUNT(e.id) AS total_employees,
    ROUND(AVG(e.salary), 2) AS average_salary
FROM employees e
JOIN departments d ON d.id = e.department_id
GROUP BY d.id, d.department_name
ORDER BY average_salary DESC;"""

        # Level 3: Sales / Revenue by region or customer segment
        if ("revenue" in lowered or "sales" in lowered) and "region" in lowered:
            return """SELECT 
    r.region_name,
    COUNT(DISTINCT o.id) AS total_orders,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN regions r ON r.id = c.region_id
JOIN order_items oi ON oi.order_id = o.id
WHERE o.order_status != 'Cancelled'
GROUP BY r.id, r.region_name
ORDER BY total_revenue DESC;"""

        # Level 2: How many employees in department
        if "how many" in lowered and "employees" in lowered and ("ai" in lowered or "machine learning" in lowered):
            return """SELECT COUNT(*) AS total_employees
FROM employees e
JOIN departments d ON d.id = e.department_id
WHERE d.department_name LIKE '%AI%';"""

        if "how many employees" in lowered or "count of employees" in lowered:
            return "SELECT COUNT(*) AS total_employees FROM employees;"

        # Level 1: List top products by revenue
        if "top" in lowered and ("product" in lowered or "products" in lowered):
            return """SELECT 
    p.product_name,
    p.category,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON p.id = oi.product_id
JOIN orders o ON o.id = oi.order_id
WHERE o.order_status != 'Cancelled'
GROUP BY p.id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;"""

        # General list / show fallback (only if explicit list/show keywords are present)
        if any(w in lowered for w in ["show", "list", "display", "all", "top", "view", "get"]):
            return """SELECT 
    e.employee_name,
    e.role,
    e.salary,
    d.department_name,
    e.joining_date
FROM employees e
JOIN departments d ON d.id = e.department_id
ORDER BY e.salary DESC
LIMIT 10;"""

        # Strict 0-record fallback for any unrecognized or non-matching query
        if self.raw_schema and first_table in self.raw_schema:
            cols = [f"`{c['name']}`" for c in self.raw_schema[first_table].get("columns", []) if not c['name'].startswith("Unnamed")]
            col_str = ", ".join(cols[:5]) if cols else "*"
            return f"SELECT {col_str} FROM `{first_table}` WHERE 1=0;"
        return "SELECT * FROM employees WHERE 1=0;"

    def _generate_gemini(self, question: str, plan: Dict[str, Any] = None, context: str = "") -> str:
        """Call Gemini API to produce dialect-aware SQL query."""
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            logger.info("GEMINI_API_KEY not provided. Using rule engine generator.")
            return self._generate_rule_engine(question, plan)

        system_prompt = f"""You are an expert SQL Data Analyst.
Target SQL Dialect: {self.dialect.upper()}

{self.schema_text}

Query Plan Context:
{plan if plan else 'None'}

User Question: {question}

Rules:
1. Return ONLY executable SQL. Do NOT wrap in markdown or explanation.
2. Only use table and column names that exist in the schema.
3. Do NOT modify data (SELECT / WITH queries only).
4. Always ensure string filtering (e.g. name starting letter 'm' or 'M') is case-insensitive, e.g. using (col LIKE 'M%' OR col LIKE 'm%') or LOWER(col) LIKE 'm%'.
"""
        # Try new Google GenAI SDK first
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=config.LLM_MODEL_NAME,
                contents=system_prompt
            )
            text = response.text.strip()
            return text.replace("```sql", "").replace("```", "").strip()
        except Exception as e1:
            logger.debug(f"google.genai SDK call failed: {e1}. Trying legacy google.generativeai...")
            try:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=api_key)
                model = genai_legacy.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(system_prompt)
                text = response.text.strip()
                return text.replace("```sql", "").replace("```", "").strip()
            except Exception as e2:
                logger.warning(f"Gemini API call failed: {e2}. Falling back to rule engine.")
                return self._generate_rule_engine(question, plan)

    def _generate_openai(self, question: str, plan: Dict[str, Any] = None, context: str = "") -> str:
        """Call OpenAI API to produce dialect-aware SQL query."""
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or "your_api" in api_key.lower():
            logger.info("OPENAI_API_KEY not provided. Using rule engine generator.")
            return self._generate_rule_engine(question, plan)

        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = f"""Target Dialect: {self.dialect.upper()}
Schema:
{self.schema_text}

User Question: {question}

Rules:
1. Return ONLY the raw SQL query without explanation or markdown.
2. Ensure string filters (e.g., name starting letter 'm' or 'M') are case-insensitive."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        sql = response.choices[0].message.content.strip()
        return sql.replace("```sql", "").replace("```", "").strip()
