import React, { useState } from 'react';
import { Download, Search, Layers, Clock, AlertTriangle } from 'lucide-react';

export default function ResultsTable({ data, columns, rowCount, executionTime, error }) {
  const [filterText, setFilterText] = useState('');

  if (error) {
    return (
      <div className="cloud-card p-6 border-red-200 bg-red-50/80 text-red-700 flex items-start gap-3">
        <AlertTriangle className="w-6 h-6 text-red-500 shrink-0 mt-0.5" />
        <div>
          <h3 className="font-bold text-sm text-red-900 mb-1">Execution Error</h3>
          <p className="text-xs text-red-700 mono-font">{error}</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="cloud-card p-12 text-center flex flex-col items-center justify-center gap-3">
        <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-200 text-slate-400 flex items-center justify-center">
          <Search className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-800">No Records Found</h3>
          <p className="text-xs text-slate-500 max-w-md mt-1">
            0 dataset records matching your query criteria. Try asking a different question or clicking one of the sample query chips above!
          </p>
        </div>
        {executionTime > 0 && (
          <span className="badge-pill badge-sky text-[11px] mono-font mt-1">
            Execution Time: {executionTime} ms
          </span>
        )}
      </div>
    );
  }

  const filteredData = data.filter((row) =>
    Object.values(row).some((val) =>
      String(val).toLowerCase().includes(filterText.toLowerCase())
    )
  );

  const exportCSV = () => {
    if (!columns || !data) return;
    const header = columns.join(',');
    const rows = data.map((row) =>
      columns.map((c) => `"${row[c] !== undefined ? row[c] : ''}"`).join(',')
    );
    const csvContent = 'data:text/csv;charset=utf-8,' + [header, ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'query_result.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="cloud-card p-5 flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2 text-xs font-semibold">
          <span className="badge-pill badge-sky">
            <Layers className="w-3.5 h-3.5" />
            {rowCount} Records
          </span>
          <span className="badge-pill badge-emerald mono-font">
            <Clock className="w-3.5 h-3.5" />
            {executionTime} ms
          </span>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 absolute left-3 text-slate-400" />
            <input
              type="text"
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              placeholder="Filter dataset..."
              className="pill-input pl-8 pr-3 py-1.5 text-xs w-48 shadow-none border-slate-200"
            />
          </div>

          <button onClick={exportCSV} className="btn-white-pill text-xs py-1.5 px-3 flex items-center gap-1.5">
            <Download className="w-3.5 h-3.5 text-sky-600" />
            Export CSV
          </button>
        </div>
      </div>

      <div className="cloud-table-container">
        <table className="cloud-table">
          <thead>
            <tr>
              <th className="w-12 text-center">#</th>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredData.map((row, rIdx) => (
              <tr key={rIdx}>
                <td className="text-center text-slate-400 text-xs mono-font font-medium">{rIdx + 1}</td>
                {columns.map((col) => (
                  <td key={col} className="mono-font text-xs text-slate-800">
                    {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-slate-300">NULL</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
