import React, { useState } from 'react';
import { Smile, Frown, Meh, Sparkles, Filter, Activity, CheckCircle2, AlertCircle } from 'lucide-react';

export default function SentimentViewer({ sentimentSuite }) {
  const [filterLabel, setFilterLabel] = useState('ALL');

  if (!sentimentSuite || !sentimentSuite.has_sentiment) {
    return (
      <div className="cloud-card p-10 text-center flex flex-col items-center justify-center gap-3">
        <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-200 text-slate-400 flex items-center justify-center">
          <Smile className="w-6 h-6" />
        </div>
        <h3 className="text-sm font-bold text-slate-800">No Text Columns Identified for Sentiment Analysis</h3>
        <p className="text-xs text-slate-500 max-w-md">
          Sentiment analysis automatically evaluates textual fields like feedback, emails, comments, and roles. Upload a dataset with text descriptions to unlock sentiment metrics!
        </p>
      </div>
    );
  }

  const {
    target_column,
    total_records,
    average_score,
    health_index,
    positive_count,
    negative_count,
    neutral_count,
    positive_pct,
    negative_pct,
    neutral_pct,
    row_sentiments
  } = sentimentSuite;

  const filteredRows = row_sentiments.filter((r) => {
    if (filterLabel === 'POSITIVE') return r.label === 'POSITIVE';
    if (filterLabel === 'NEGATIVE') return r.label === 'NEGATIVE';
    if (filterLabel === 'NEUTRAL') return r.label === 'NEUTRAL';
    return true;
  });

  return (
    <div className="flex flex-col gap-6">
      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {/* Overall Health Card */}
        <div className="cloud-card p-5 bg-gradient-to-br from-sky-900 to-slate-900 text-white flex flex-col justify-between">
          <div className="flex items-center justify-between text-sky-200 text-xs font-semibold">
            <span>Sentiment Health</span>
            <Activity className="w-4 h-4 text-sky-400" />
          </div>
          <div className="mt-3">
            <span className="text-2xl font-extrabold text-white tracking-tight">{health_index}</span>
            <p className="text-[11px] text-sky-300 mt-1">Avg Polarity Score: {average_score}</p>
          </div>
        </div>

        {/* Positive Card */}
        <div className="cloud-card p-5 border-emerald-200 bg-emerald-50/60 flex flex-col justify-between">
          <div className="flex items-center justify-between text-emerald-800 text-xs font-bold">
            <span className="flex items-center gap-1.5">
              <Smile className="w-4 h-4 text-emerald-600" /> Positive Sentiment
            </span>
            <span className="badge-pill bg-emerald-200/80 text-emerald-900 text-[10px]">{positive_pct}%</span>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-black text-emerald-950">{positive_count}</span>
            <span className="text-xs text-emerald-700 font-medium ml-1">/ {total_records} records</span>
          </div>
        </div>

        {/* Neutral Card */}
        <div className="cloud-card p-5 border-slate-200 bg-slate-50/60 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-800 text-xs font-bold">
            <span className="flex items-center gap-1.5">
              <Meh className="w-4 h-4 text-slate-500" /> Neutral Sentiment
            </span>
            <span className="badge-pill bg-slate-200/80 text-slate-900 text-[10px]">{neutral_pct}%</span>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-black text-slate-900">{neutral_count}</span>
            <span className="text-xs text-slate-600 font-medium ml-1">/ {total_records} records</span>
          </div>
        </div>

        {/* Negative Card */}
        <div className="cloud-card p-5 border-red-200 bg-red-50/60 flex flex-col justify-between">
          <div className="flex items-center justify-between text-red-800 text-xs font-bold">
            <span className="flex items-center gap-1.5">
              <Frown className="w-4 h-4 text-red-600" /> Negative / Issues
            </span>
            <span className="badge-pill bg-red-200/80 text-red-900 text-[10px]">{negative_pct}%</span>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-black text-red-950">{negative_count}</span>
            <span className="text-xs text-red-700 font-medium ml-1">/ {total_records} records</span>
          </div>
        </div>
      </div>

      {/* Visual Sentiment Stacked Progress Bar */}
      <div className="cloud-card p-4 flex flex-col gap-2">
        <div className="flex items-center justify-between text-xs font-bold text-slate-700">
          <span>Target Column Analyzed: <code className="mono-font bg-sky-50 text-sky-800 px-2 py-0.5 rounded border border-sky-200">`{target_column}`</code></span>
          <span>{total_records} Records Analyzed</span>
        </div>
        <div className="w-full h-3 rounded-full bg-slate-200 overflow-hidden flex">
          <div style={{ width: `${positive_pct}%` }} className="bg-emerald-500 transition-all" title={`Positive: ${positive_pct}%`} />
          <div style={{ width: `${neutral_pct}%` }} className="bg-slate-400 transition-all" title={`Neutral: ${neutral_pct}%`} />
          <div style={{ width: `${negative_pct}%` }} className="bg-red-500 transition-all" title={`Negative: ${negative_pct}%`} />
        </div>
      </div>

      {/* Interactive Sentiment Filter Pills */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mr-1 flex items-center gap-1">
          <Filter className="w-3.5 h-3.5" /> Filter Sentiment:
        </span>
        <button
          onClick={() => setFilterLabel('ALL')}
          className={`badge-pill text-xs py-1.5 px-4 font-bold cursor-pointer transition-all ${
            filterLabel === 'ALL'
              ? 'bg-slate-900 text-white shadow-xs'
              : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          🌐 All ({total_records})
        </button>
        <button
          onClick={() => setFilterLabel('POSITIVE')}
          className={`badge-pill text-xs py-1.5 px-4 font-bold cursor-pointer transition-all ${
            filterLabel === 'POSITIVE'
              ? 'bg-emerald-600 text-white shadow-xs'
              : 'bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100'
          }`}
        >
          🟢 Positive Only ({positive_count})
        </button>
        <button
          onClick={() => setFilterLabel('NEUTRAL')}
          className={`badge-pill text-xs py-1.5 px-4 font-bold cursor-pointer transition-all ${
            filterLabel === 'NEUTRAL'
              ? 'bg-slate-700 text-white shadow-xs'
              : 'bg-slate-100 text-slate-800 border border-slate-200 hover:bg-slate-200'
          }`}
        >
          ⚪ Neutral Only ({neutral_count})
        </button>
        <button
          onClick={() => setFilterLabel('NEGATIVE')}
          className={`badge-pill text-xs py-1.5 px-4 font-bold cursor-pointer transition-all ${
            filterLabel === 'NEGATIVE'
              ? 'bg-red-600 text-white shadow-xs'
              : 'bg-red-50 text-red-800 border border-red-200 hover:bg-red-100'
          }`}
        >
          🔴 Negative Only ({negative_count})
        </button>
      </div>

      {/* Row-by-Row Sentiment Cards List */}
      <div className="flex flex-col gap-3">
        {filteredRows.length === 0 ? (
          <div className="cloud-card p-8 text-center text-slate-400 text-xs">
            No records found for sentiment filter '{filterLabel}'.
          </div>
        ) : (
          filteredRows.map((r, i) => (
            <div key={i} className="cloud-card p-4 hover:shadow-md transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-start gap-3">
                <span className="w-7 h-7 rounded-full bg-slate-100 border border-slate-200 text-slate-600 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                  #{r.row_index + 1}
                </span>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 leading-snug">{r.target_val}</h4>
                  <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-500">
                    <span className="font-semibold text-slate-600">Emotion: {r.emotion}</span>
                    <span>•</span>
                    <span className="mono-font text-slate-400">Polarity Score: {r.score}</span>
                  </div>
                </div>
              </div>

              <div className="shrink-0 flex items-center gap-2">
                {r.label === 'POSITIVE' && (
                  <span className="badge-pill badge-sky text-emerald-800 bg-emerald-100/90 border border-emerald-300 text-xs py-1 px-3 font-bold flex items-center gap-1">
                    <Smile className="w-3.5 h-3.5 text-emerald-600" /> POSITIVE (+{r.score})
                  </span>
                )}
                {r.label === 'NEUTRAL' && (
                  <span className="badge-pill bg-slate-100 text-slate-700 border border-slate-200 text-xs py-1 px-3 font-bold flex items-center gap-1">
                    <Meh className="w-3.5 h-3.5 text-slate-500" /> NEUTRAL (0.0)
                  </span>
                )}
                {r.label === 'NEGATIVE' && (
                  <span className="badge-pill bg-red-100 text-red-800 border border-red-300 text-xs py-1 px-3 font-bold flex items-center gap-1">
                    <Frown className="w-3.5 h-3.5 text-red-600" /> NEGATIVE ({r.score})
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
