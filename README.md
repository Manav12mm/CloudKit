# ⚡ CloudKit - AI SQL Data Analyst & Sentiment Suite

CloudKit is an AI-powered SQL data analysis platform that converts natural language questions into accurate SQL queries, executes them against relational databases (SQLite / MySQL), self-corrects invalid queries, and provides dynamic data visualizations with dataset sentiment analysis.

---

## 🌟 Key Features

- 🧠 **AI-Powered Text-to-SQL Engine**: Translates natural language questions into database queries.
- 🔄 **Self-Correction & Plan Validation**: Detects and fixes syntax/schema errors automatically.
- 📊 **Sentiment & Analytics Suite**: Computes automated data insights and sentiment trends.
- ⚡ **FastAPI Backend**: Lightweight, asynchronous REST API layer for database execution.
- 🎨 **React + Tailwind Frontend**: Clean, responsive dashboard for query exploration and visual reporting.
- 📂 **Custom Dataset Upload**: Upload `.csv` or `.db`/`.sqlite` files to analyze custom data instantly.

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.9+
- **Node.js**: 18+ & npm

---

### Backend Setup (FastAPI)

1. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn pymysql pandas pydantic
   ```

2. **Start the API server:**
   ```bash
   python server.py
   ```
   The backend server will run at `http://localhost:8000`.

3. **Run Benchmark Tests:**
   ```bash
   python tests/test_benchmark.py
   ```

---

### Frontend Setup (React + Vite)

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the dev server:**
   ```bash
   npm run dev
   ```
   The application UI will run at `http://localhost:5173`.

---

## 🛠️ Project Structure

```
.
├── agent/                  # AI SQL Generator, Planner, Validator & Corrector
├── analytics/              # Analytics & Sentiment Engine
├── database/               # DB connection, schema inspector, executor & seeders
├── frontend/               # React + Vite + Tailwind CSS frontend dashboard
├── tests/                  # Automated benchmark test suite
├── uploads/                # Directory for user-uploaded custom datasets
├── server.py               # Main FastAPI backend server entry point
├── main.py                 # CLI demo entry point
└── README.md
```

---

## 📄 License

MIT License © 2026 Manav Mishra
