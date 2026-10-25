import React, { useState } from 'react';
import { ExternalLink, PlusCircle, CheckCircle, ShieldCheck, Filter, ArrowUpDown, Copy, Check } from 'lucide-react';

export default function FindingsTable({ findings, activeCase, onAddToCase }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [moduleFilter, setModuleFilter] = useState('all');
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [sortBy, setSortBy] = useState('confidence'); // confidence, timestamp, source
  const [sortOrder, setSortOrder] = useState('desc');
  const [copiedId, setCopiedId] = useState(null);

  const copyFindingId = (id) => {
    navigator.clipboard.writeText(`[${id}]`);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Filter logic
  const filtered = findings.filter(f => {
    if (moduleFilter !== 'all' && f.module !== moduleFilter) return false;
    if (verifiedOnly && !f.verified) return false;
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      const matchText = `${f.target} ${f.source} ${f.evidence_snippet} ${f.exact_url}`.toLowerCase();
      if (!matchText.includes(q)) return false;
    }
    return true;
  });

  // Sort logic
  const sorted = [...filtered].sort((a, b) => {
    let comparison = 0;
    if (sortBy === 'confidence') {
      comparison = a.confidence - b.confidence;
    } else if (sortBy === 'source') {
      comparison = a.source.localeCompare(b.source);
    } else if (sortBy === 'timestamp') {
      comparison = (a.timestamp || '').localeCompare(b.timestamp || '');
    }
    return sortOrder === 'desc' ? -comparison : comparison;
  });

  const modules = Array.from(new Set(findings.map(f => f.module)));

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
      {/* Controls Bar */}
      <div className="p-4 bg-dark-850 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3 flex-1 min-w-[240px]">
          <div className="relative flex-1 max-w-sm">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter findings by keyword, URL, or target..."
              className="w-full bg-dark-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
            />
          </div>

          <select
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
            className="bg-dark-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
          >
            <option value="all">All Modules ({findings.length})</option>
            {modules.map(m => (
              <option key={m} value={m}>{m.toUpperCase()}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <label className="flex items-center space-x-1.5 cursor-pointer text-slate-300">
            <input
              type="checkbox"
              checked={verifiedOnly}
              onChange={(e) => setVerifiedOnly(e.target.checked)}
              className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-3.5 w-3.5"
            />
            <span>Verified Only</span>
          </label>

          <div className="flex items-center space-x-1 border-l border-slate-700 pl-3">
            <button
              onClick={() => {
                if (sortBy === 'confidence') {
                  setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
                } else {
                  setSortBy('confidence');
                  setSortOrder('desc');
                }
              }}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded text-xs font-semibold ${
                sortBy === 'confidence' ? 'bg-brand-600/30 text-brand-400 border border-brand-500/50' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <ArrowUpDown className="w-3 h-3" />
              <span>Confidence</span>
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-dark-950 text-slate-400 border-b border-slate-800">
              <th className="py-3 px-4 font-semibold w-24">Finding ID</th>
              <th className="py-3 px-4 font-semibold w-28">Target</th>
              <th className="py-3 px-4 font-semibold w-36">Source / Module</th>
              <th className="py-3 px-4 font-semibold w-24">Confidence</th>
              <th className="py-3 px-4 font-semibold">Evidence Snippet & Exact URL</th>
              <th className="py-3 px-4 font-semibold w-28 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80">
            {sorted.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500">
                  No findings match current filters or no search executed yet.
                </td>
              </tr>
            ) : (
              sorted.map((f) => (
                <tr key={f.id} className="hover:bg-dark-850/60 transition group">
                  {/* Finding ID with Copy for Report Citation */}
                  <td className="py-3 px-4 align-top">
                    <button
                      onClick={() => copyFindingId(f.id)}
                      title="Click to copy Citation ID for Report Writer"
                      className="flex items-center space-x-1 font-mono text-[11px] font-bold text-sky-400 bg-sky-950/60 hover:bg-sky-900 px-1.5 py-0.5 rounded border border-sky-800/70 transition"
                    >
                      {copiedId === f.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      <span>[{f.id.slice(0, 9)}]</span>
                    </button>
                    {f.verified && (
                      <span className="mt-1 inline-flex items-center text-[9px] px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">
                        VERIFIED
                      </span>
                    )}
                  </td>

                  {/* Target */}
                  <td className="py-3 px-4 align-top font-mono text-slate-300 font-medium">
                    {f.target}
                  </td>

                  {/* Source */}
                  <td className="py-3 px-4 align-top">
                    <span className="font-semibold text-slate-200 block">{f.source}</span>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider">{f.module}</span>
                  </td>

                  {/* Confidence */}
                  <td className="py-3 px-4 align-top">
                    <div className="flex items-center space-x-1.5">
                      <div className="w-12 bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${
                            f.confidence >= 0.85
                              ? 'bg-emerald-500'
                              : f.confidence >= 0.65
                              ? 'bg-cyan-500'
                              : 'bg-amber-500'
                          }`}
                          style={{ width: `${Math.round(f.confidence * 100)}%` }}
                        />
                      </div>
                      <span className="font-mono text-slate-300 font-bold">{Math.round(f.confidence * 100)}%</span>
                    </div>
                  </td>

                  {/* Evidence & URL */}
                  <td className="py-3 px-4 align-top">
                    <p className="text-slate-300 leading-relaxed">{f.evidence_snippet}</p>
                    <div className="mt-1 flex items-center space-x-1.5">
                      <ExternalLink className="w-3 h-3 text-brand-400 shrink-0" />
                      <a
                        href={f.exact_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-brand-400 hover:text-brand-300 underline font-mono text-[11px] truncate max-w-lg"
                      >
                        {f.exact_url}
                      </a>
                    </div>
                  </td>

                  {/* Action: Add to Case */}
                  <td className="py-3 px-4 align-top text-right">
                    <button
                      onClick={() => onAddToCase(f)}
                      className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-dark-800 hover:bg-brand-600 text-slate-300 hover:text-white border border-slate-700 hover:border-brand-500 font-medium text-xs transition"
                    >
                      <PlusCircle className="w-3.5 h-3.5" />
                      <span>Add to Case</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
