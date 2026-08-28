import React, { useState, useRef } from 'react';
import { Database, Table, ChevronRight, ChevronDown, Key, Columns, Upload, FileSpreadsheet, CheckCircle2, FileText, Hash, Calendar, Globe } from 'lucide-react';

export default function Sidebar({ schema, selectedTable, onSelectTable, onUpload, uploading }) {
  const [openTables, setOpenTables] = useState({});
  const fileInputRef = useRef(null);

  const toggleTable = (tableName) => {
    setOpenTables((prev) => ({
      ...prev,
      [tableName]: !prev[tableName]
    }));
  };

  const handleSelect = (tName) => {
    if (onSelectTable) {
      if (selectedTable === tName) {
        onSelectTable(''); // Deselect / Switch back to Auto AI Detect
      } else {
        onSelectTable(tName);
      }
    }
    setOpenTables((prev) => ({
      ...prev,
      [tName]: true
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onUpload(file);
    }
  };

  const tables = schema ? Object.entries(schema) : [];

  const getTypeIcon = (typeStr) => {
    const t = (typeStr || '').toUpperCase();
    if (t.includes('INT') || t.includes('FLOAT') || t.includes('DECIMAL') || t.includes('NUMBER')) {
      return <Hash className="w-3 h-3 text-indigo-500 shrink-0" />;
    }
    if (t.includes('DATE') || t.includes('TIME')) {
      return <Calendar className="w-3 h-3 text-amber-500 shrink-0" />;
    }
    return <FileText className="w-3 h-3 text-sky-500 shrink-0" />;
  };

  return (
    <aside className="cloud-card p-5 h-full flex flex-col gap-4">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <div className="p-2 rounded-xl bg-sky-100 text-sky-700">
          <Database className="w-4 h-4" />
        </div>
        <div>
          <h2 className="text-xs font-bold tracking-wider text-slate-800 uppercase">
            Schema Inspector
          </h2>
          <p className="text-[11px] text-slate-500">{tables.length} connected tables</p>
        </div>
      </div>

      {/* Upload Custom Dataset Box */}
      <div className="p-3.5 rounded-2xl bg-gradient-to-b from-sky-50 to-white border border-sky-100 flex flex-col gap-2 shadow-sm">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
          <FileSpreadsheet className="w-4 h-4 text-sky-600" />
          Custom Dataset
        </div>
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Import your own <span className="font-semibold text-slate-700">.CSV</span> or <span className="font-semibold text-slate-700">.DB</span> files.
        </p>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".csv,.db,.sqlite,.sqlite3"
          className="hidden"
        />

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="w-full btn-white-pill text-xs py-2 justify-center shadow-sm hover:bg-white text-slate-800 font-semibold"
        >
          <Upload className="w-3.5 h-3.5 text-sky-600" />
          {uploading ? 'Uploading File...' : 'Browse File (.csv / .db)'}
        </button>
      </div>

      {/* Table list with All Datasets Auto option */}
      <div className="flex flex-col gap-2.5 overflow-y-auto max-h-[650px] pr-1">
        {/* All Datasets Auto Option */}
        <div
          onClick={() => onSelectTable && onSelectTable('')}
          className={`rounded-2xl border px-3.5 py-2.5 flex items-center justify-between cursor-pointer select-none transition-all ${
            !selectedTable
              ? 'border-sky-400 bg-sky-50/80 shadow-xs ring-2 ring-sky-300/40'
              : 'border-slate-100 bg-white/70 hover:border-sky-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-sky-600 shrink-0" />
            <span className={`text-xs ${!selectedTable ? 'font-black text-sky-950' : 'font-semibold text-slate-800'}`}>
              All Datasets (Auto AI Detect)
            </span>
          </div>
          {!selectedTable && (
            <span className="badge-pill bg-sky-600 text-white text-[10px] font-bold px-2 py-0.5 shadow-xs">
              ✓ Active
            </span>
          )}
        </div>
        {tables.length === 0 ? (
          <div className="text-xs text-slate-400 py-6 text-center">Loading schema...</div>
        ) : (
          tables.map(([tName, tMeta]) => {
            const isSelected = selectedTable === tName;
            const isOpen = !!openTables[tName] || isSelected;
            const cols = tMeta.columns || [];

            return (
              <div
                key={tName}
                className={`rounded-2xl border transition-all overflow-hidden ${
                  isSelected
                    ? 'border-emerald-400 bg-emerald-50/60 shadow-sm ring-2 ring-emerald-400/40'
                    : 'border-slate-100 bg-white/70 hover:border-sky-200'
                }`}
              >
                <div
                  onClick={() => handleSelect(tName)}
                  className="w-full flex items-center justify-between px-3.5 py-3 text-left text-xs font-semibold cursor-pointer select-none"
                >
                  <div className="flex items-center gap-2 min-w-0 flex-1 pr-2">
                    {isSelected ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 animate-pulse" />
                    ) : (
                      <Table className="w-3.5 h-3.5 text-sky-600 shrink-0" />
                    )}
                    <span
                      className={`mono-font font-bold text-xs truncate ${
                        isSelected ? 'text-emerald-950 font-black' : 'text-slate-800'
                      }`}
                      title={tName}
                    >
                      {tName}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    {isSelected && (
                      <span className="badge-pill bg-emerald-600 text-white text-[10px] font-bold px-2 py-0.5 shadow-xs">
                        ✓ Selected
                      </span>
                    )}
                    <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 shrink-0">
                      {cols.length} cols
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleTable(tName);
                      }}
                      className="text-slate-400 hover:text-slate-600 p-0.5"
                    >
                      {isOpen ? <ChevronDown className="w-3.5 h-3.5 shrink-0" /> : <ChevronRight className="w-3.5 h-3.5 shrink-0" />}
                    </button>
                  </div>
                </div>

                {isOpen && (
                  <div className="px-3.5 py-2.5 border-t border-slate-100/80 bg-white/80 flex flex-col gap-1.5 max-h-60 overflow-y-auto">
                    {cols.map((col, idx) => (
                      <div key={idx} className="flex items-center justify-between text-[11px] py-1 border-b border-slate-50 last:border-0 min-w-0">
                        <div className="flex items-center gap-1.5 min-w-0 flex-1 pr-2">
                          {col.primary_key ? (
                            <Key className="w-3 h-3 text-amber-500 shrink-0" />
                          ) : (
                            getTypeIcon(col.type)
                          )}
                          <span className="mono-font font-semibold text-slate-800 truncate" title={col.name}>
                            {col.name}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full font-mono shrink-0">
                          {col.type || 'TEXT'}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
