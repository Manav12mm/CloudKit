import React from 'react';
import { Sparkles, ArrowRight, CornerDownLeft } from 'lucide-react';

export default function QueryInput({ question, setQuestion, onExecute, loading }) {
  const sampleQueries = [
    "har department mai m se naam chalu hone wale ka with salary greater than 1000",
    "What is the average salary by department?",
    "Show total sales revenue by region excluding cancelled orders",
    "How many employees are in the company?"
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim() && !loading) {
      onExecute(question);
    }
  };

  return (
    <div className="flex flex-col gap-4 max-w-4xl mx-auto w-full">
      <form onSubmit={handleSubmit} className="relative flex items-center shadow-lg rounded-full">
        <div className="absolute left-5 text-sky-500">
          <Sparkles className="w-5 h-5" />
        </div>

        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask any question in English or Hinglish (e.g. 'har department mai m se naam chalu...')"
          className="pill-input w-full pl-14 pr-36 py-4 text-sm font-medium placeholder-slate-400 text-slate-900"
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="btn-dark-pill absolute right-2 py-2.5 px-5 text-xs flex items-center gap-2"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Processing...
            </span>
          ) : (
            <>
              Run Query
              <ArrowRight className="w-3.5 h-3.5 text-sky-400" />
            </>
          )}
        </button>
      </form>

      {/* Query Suggestions */}
      <div className="flex items-center justify-center gap-2 flex-wrap pt-1">
        <span className="text-xs font-semibold text-slate-500">
          Try Asking:
        </span>
        {sampleQueries.map((sample, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setQuestion(sample);
              onExecute(sample);
            }}
            className="text-xs px-3.5 py-1.5 rounded-full bg-white/80 border border-sky-100 text-slate-600 hover:text-sky-700 hover:border-sky-300 hover:bg-sky-50 transition-all shadow-sm font-medium"
          >
            {sample}
          </button>
        ))}
      </div>
    </div>
  );
}
