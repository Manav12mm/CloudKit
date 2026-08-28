import React, { useState } from 'react';
import { Code2, Copy, Check, ShieldCheck, Cpu } from 'lucide-react';

export default function SqlViewer({ sql, plan, verifier }) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Generated SQL Box */}
      <div className="cloud-card p-5 flex flex-col gap-3">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Code2 className="w-4 h-4 text-sky-600" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Executable SQL Output
            </h3>
            <span className="badge-pill badge-emerald text-[11px]">
              <ShieldCheck className="w-3 h-3" /> Validated Query
            </span>
          </div>

          <button onClick={copyToClipboard} className="btn-white-pill text-xs py-1.5 px-3 flex items-center gap-1.5">
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-sky-600" />}
            {copied ? 'Copied!' : 'Copy SQL'}
          </button>
        </div>

        <pre className="cloud-code-block">{sql}</pre>
      </div>

      {/* Query Plan & Intent */}
      {plan && (
        <div className="cloud-card p-5 flex flex-col gap-3">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <Cpu className="w-4 h-4 text-sky-600" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Decomposed Query Plan & Intent
            </h3>
            <span className="badge-pill badge-sky text-[11px]">
              Level {plan.complexity_level || 1} Complexity
            </span>
            <span className="badge-pill bg-slate-100 text-slate-700 border border-slate-200 text-[11px]">
              Intent: {plan.intent || 'SELECTION'}
            </span>
          </div>

          <div className="flex flex-col gap-2">
            <h4 className="text-xs font-semibold text-slate-600">Step-by-Step Analytical Plan:</h4>
            <div className="flex flex-col gap-2">
              {(plan.plan_steps || ["Direct table query and filter."]).map((step, idx) => (
                <div key={idx} className="flex items-center gap-3 text-xs text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-100 shadow-xs">
                  <span className="w-6 h-6 rounded-full bg-sky-500 text-white flex items-center justify-center font-bold text-[10px] shrink-0 shadow-sm">
                    {idx + 1}
                  </span>
                  <span className="font-medium">{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
