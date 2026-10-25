import React from 'react';
import { Eye, Shield, Key, FolderGit2, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function Navbar({ activeCase, cases, onSelectCase, user, purpose }) {
  return (
    <header className="border-b border-slate-800 bg-dark-900/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 to-cyan-500 flex items-center justify-center glow-blue">
            <Eye className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-extrabold tracking-wider bg-gradient-to-r from-sky-400 to-cyan-200 bg-clip-text text-transparent">
                TRINETRA
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded uppercase font-bold tracking-widest bg-cyan-950/80 text-cyan-400 border border-cyan-800/60">
                OSINT v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 tracking-tight">Defensible Intelligence & Digital Footprint Auditor</p>
          </div>
        </div>

        {/* Center: Case Indicator */}
        <div className="flex items-center space-x-3 bg-dark-850 px-3.5 py-1.5 rounded-lg border border-slate-800">
          <FolderGit2 className="w-4 h-4 text-brand-500" />
          <span className="text-xs text-slate-400 font-medium">Active Case:</span>
          <select
            value={activeCase?.id || ''}
            onChange={(e) => {
              const selected = cases.find(c => c.id === e.target.value);
              onSelectCase(selected || null);
            }}
            className="bg-dark-900 text-xs text-slate-200 font-semibold px-2 py-1 rounded border border-slate-700 focus:outline-none focus:border-brand-500"
          >
            <option value="">-- No Case Selected --</option>
            {cases.map((c) => (
              <option key={c.id} value={c.id}>
                {c.title} ({c.classification})
              </option>
            ))}
          </select>
        </div>

        {/* Right Info: Purpose & Security */}
        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 text-xs">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-400">Compliance:</span>
            <span className="text-emerald-400 font-semibold flex items-center">
              Audited <CheckCircle2 className="w-3 h-3 ml-1" />
            </span>
          </div>

          <div className="flex items-center space-x-2 pl-4 border-l border-slate-800 text-xs">
            <div className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center font-bold text-sky-400 text-xs border border-slate-700">
              {user?.username ? user.username[0].toUpperCase() : 'A'}
            </div>
            <div className="text-left hidden sm:block">
              <p className="text-slate-200 font-medium leading-none">{user?.username || 'Analyst'}</p>
              <p className="text-[10px] text-slate-500 leading-none mt-1">Role: {user?.role || 'Investigator'}</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
