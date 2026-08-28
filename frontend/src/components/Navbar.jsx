import React, { useRef } from 'react';
import { Cloud, Sparkles, FolderPlus, RefreshCw, ChevronDown } from 'lucide-react';

export default function Navbar({ dialect, onSeed, seeding, onUpload, uploading }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div className="w-full flex justify-center pt-6 px-4 mb-8">
      <header className="pill-header max-w-5xl w-full px-6 py-3 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-full bg-sky-500 text-white flex items-center justify-center shadow-md shadow-sky-500/30">
            <Cloud className="w-5 h-5 fill-current" />
          </div>
          <span className="text-lg font-bold tracking-tight text-slate-900">
            Cloudkit <span className="text-sky-600 font-medium text-xs ml-1 px-2 py-0.5 rounded-full bg-sky-100 border border-sky-200">AI SQL</span>
          </span>
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
          <a href="#hero" className="text-slate-900 font-semibold hover:text-sky-600 transition-colors">Home</a>
          <a href="#dashboard" className="hover:text-sky-600 transition-colors">Queries</a>
          <a href="#schema" className="hover:text-sky-600 transition-colors flex items-center gap-1">
            Schema <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </a>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-sky-50 border border-sky-200 text-xs font-semibold text-sky-700">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="mono-font uppercase">{dialect || 'sqlite'} Engine</span>
          </div>
        </nav>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
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
            className="btn-dark-pill text-xs py-2 px-4 flex items-center gap-1.5"
          >
            <FolderPlus className="w-3.5 h-3.5 text-sky-400" />
            {uploading ? 'Uploading...' : 'Import Dataset'}
          </button>

          <button
            onClick={onSeed}
            disabled={seeding}
            className="btn-white-pill text-xs py-2 px-3 flex items-center gap-1"
            title="Reset to default benchmark dataset"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${seeding ? 'animate-spin' : ''}`} />
            {seeding ? 'Resetting...' : 'Reset'}
          </button>
        </div>
      </header>
    </div>
  );
}
