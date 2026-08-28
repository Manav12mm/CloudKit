import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import QueryInput from './components/QueryInput';
import ResultsTable from './components/ResultsTable';
import SqlViewer from './components/SqlViewer';
import SentimentViewer from './components/SentimentViewer';
import { Sparkles, ArrowRight, ShieldCheck, Database, Table, Code2, Cloud, CheckCircle2, Globe } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function App() {
  const [schemaData, setSchemaData] = useState(null);
  const [selectedTable, setSelectedTable] = useState('');
  const [question, setQuestion] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('results');

  // Load Schema on Mount
  useEffect(() => {
    fetchSchema();
    // Auto run default query on start
    handleExecute("har department mai m se naam chalu hone wale ka with salary greater than 1000");
  }, []);

  const fetchSchema = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/schema`);
      const data = await res.json();
      setSchemaData(data);
    } catch (err) {
      console.error("Failed to fetch schema:", err);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await fetch(`${API_BASE}/api/seed`, { method: 'POST' });
      await fetchSchema();
    } catch (err) {
      console.error("Failed to re-seed DB:", err);
    } finally {
      setSeeding(false);
    }
  };

  const handleUpload = async (file) => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.success) {
        alert(data.message);
        await fetchSchema();
        if (data.table_name) {
          setSelectedTable(data.table_name);
          const autoQuery = `Show top 10 records from ${data.table_name}`;
          setQuestion(autoQuery);
          handleExecute(autoQuery, data.table_name);
        }
      } else {
        alert(data.detail || "Upload failed");
      }
    } catch (err) {
      console.error("Upload error:", err);
      alert("Failed to upload file to backend server.");
    } finally {
      setUploading(false);
    }
  };

  const handleExecute = async (qText, targetT) => {
    const qToRun = qText || question;
    if (!qToRun.trim()) return;

    const tableToUse = targetT || selectedTable;
    setLoading(true);
    setQueryResult(null);

    try {
      const res = await fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: qToRun, target_table: tableToUse })
      });
      const data = await res.json();
      setQueryResult(data);
    } catch (err) {
      console.error("Query execution error:", err);
      setQueryResult({
        success: false,
        error: "Failed to connect to Python REST API server at http://localhost:8000"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col pb-16">
      {/* Floating Pill Header */}
      <Navbar
        dialect={schemaData?.dialect}
        onSeed={handleSeed}
        seeding={seeding}
        onUpload={handleUpload}
        uploading={uploading}
      />

      {/* Hero Section */}
      <section id="hero" className="max-w-4xl mx-auto px-4 text-center flex flex-col items-center gap-6 pt-4 pb-10">
        {/* Floating Pill Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/80 border border-sky-200/80 shadow-xs text-xs font-semibold text-sky-900">
          <span className="text-amber-500">✨</span>
          <span>The future of AI natural language SQL analytics</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 leading-[1.15]">
          Your intelligent space <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-sky-600 to-indigo-600 bg-clip-text text-transparent">
            in the database cloud
          </span>
        </h1>

        {/* Hero Subtitle */}
        <p className="text-base sm:text-lg text-slate-600 max-w-2xl font-normal leading-relaxed">
          Unmatched natural language to SQL intelligence with dynamic schema inspection, 
          self-correcting execution, and seamless Hinglish & English query understanding.
        </p>

        {/* Action Buttons */}
        <div className="flex items-center gap-4 pt-2">
          <a href="#dashboard" className="btn-white-pill text-xs py-3 px-6 shadow-md font-bold hover:bg-slate-50">
            Discover Queries
          </a>
          <a href="#schema" className="text-xs font-semibold text-slate-700 hover:text-sky-600 transition-colors flex items-center gap-1.5 px-3 py-2">
            Inspect Schema <ArrowRight className="w-3.5 h-3.5" />
          </a>
        </div>
      </section>

      {/* Main Interactive Dashboard Container */}
      <section id="dashboard" className="max-w-[1500px] w-full mx-auto px-4 sm:px-6">
        <div className="cloud-card p-6 sm:p-8 flex flex-col gap-6">
          {/* Active Target Dataset Indicator Banner */}
          {selectedTable ? (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between px-4 py-2.5 rounded-2xl bg-emerald-50/90 border border-emerald-300 text-emerald-950 text-xs font-bold shadow-2xs gap-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Active Selected Dataset: <code className="mono-font text-emerald-950 bg-emerald-200/80 px-2.5 py-0.5 rounded-full border border-emerald-400/60 font-black">{selectedTable}</code></span>
              </div>
              <span className="text-[11px] font-bold text-emerald-800 bg-emerald-100 px-3 py-0.5 rounded-full border border-emerald-200 shrink-0">
                {schemaData?.tables?.[selectedTable]?.columns?.length || 0} Columns & Data Types Configured
              </span>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between px-4 py-2.5 rounded-2xl bg-sky-50/90 border border-sky-300 text-sky-950 text-xs font-bold shadow-2xs gap-2">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-sky-600 shrink-0" />
                <span>Active Mode: <code className="mono-font text-sky-950 bg-sky-200/80 px-2.5 py-0.5 rounded-full border border-sky-400/60 font-black">All Datasets (Auto AI Intent Detection)</code></span>
              </div>
              <span className="text-[11px] font-bold text-sky-800 bg-sky-100 px-3 py-0.5 rounded-full border border-sky-200 shrink-0">
                {Object.keys(schemaData?.tables || {}).length} Tables Available for Smart AI Resolution
              </span>
            </div>
          )}

          {/* Query Input Section */}
          <QueryInput
            question={question}
            setQuestion={setQuestion}
            onExecute={handleExecute}
            loading={loading}
          />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-4 border-t border-slate-100">
            {/* Left Sidebar - Schema Browser */}
            <div id="schema" className="lg:col-span-3">
              <Sidebar
                schema={schemaData?.tables}
                selectedTable={selectedTable}
                onSelectTable={(t) => setSelectedTable(t)}
                onUpload={handleUpload}
                uploading={uploading}
              />
            </div>

            {/* Main Results Content Area */}
            <main className="lg:col-span-9 flex flex-col gap-5">
              {/* AI Clarification Card */}
              {queryResult?.clarification?.needs_clarification && (
                <div className="cloud-card p-5 border-sky-300 bg-gradient-to-r from-sky-50/90 via-indigo-50/80 to-white flex flex-col gap-3 shadow-md mb-2">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-full bg-sky-600 text-white flex items-center justify-center font-bold shadow-xs shrink-0">
                      <Sparkles className="w-4 h-4 text-amber-300" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-sky-950 uppercase tracking-wider">AI Dataset Assistant Clarification</h4>
                      <p className="text-sm font-semibold text-slate-800">{queryResult.clarification.message}</p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    {queryResult.clarification.options?.map((opt, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          let newQ = question || "Show records";
                          if (opt.includes("Combine All")) {
                            newQ = `Show overall combined ${newQ}`;
                          } else {
                            newQ = `${newQ} for ${queryResult.clarification.dimension_name} ${opt}`;
                          }
                          setQuestion(newQ);
                          handleExecute(newQ);
                        }}
                        className="badge-pill bg-white hover:bg-sky-600 hover:text-white border border-sky-200 shadow-xs text-xs py-1.5 px-4 font-bold text-sky-900 cursor-pointer transition-all flex items-center gap-1.5"
                      >
                        <span>{opt}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab Navigation */}
              <div className="flex items-center gap-2 border-b border-slate-200/80 pb-3">
                <button
                  onClick={() => setActiveTab('results')}
                  className={`flex items-center gap-2 px-5 py-2.5 text-xs font-bold rounded-full transition-all ${
                    activeTab === 'results'
                      ? 'bg-slate-900 text-white shadow-md'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-white/80'
                  }`}
                >
                  <Table className="w-4 h-4" />
                  Result Dataset
                </button>

                <button
                  onClick={() => setActiveTab('sql')}
                  className={`flex items-center gap-2 px-5 py-2.5 text-xs font-bold rounded-full transition-all ${
                    activeTab === 'sql'
                      ? 'bg-slate-900 text-white shadow-md'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-white/80'
                  }`}
                >
                  <Code2 className="w-4 h-4 text-sky-400" />
                  SQL & Query Plan
                </button>
              </div>

              {/* Tab Views */}
              {activeTab === 'results' && (
                <ResultsTable
                  data={queryResult?.data}
                  columns={queryResult?.columns}
                  rowCount={queryResult?.row_count || 0}
                  executionTime={queryResult?.execution_time_ms || 0}
                  error={queryResult?.error}
                />
              )}

              {activeTab === 'sql' && queryResult && (
                <SqlViewer
                  sql={queryResult?.sql || "-- No SQL generated"}
                  plan={queryResult?.plan}
                  verifier={queryResult?.verifier}
                />
              )}
            </main>
          </div>
        </div>
      </section>
    </div>
  );
}
