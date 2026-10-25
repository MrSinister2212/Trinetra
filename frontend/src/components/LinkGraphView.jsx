import React from 'react';
import { Network, ShieldCheck, Share2, Globe, Link2, ExternalLink } from 'lucide-react';

export default function LinkGraphView({ findings }) {
  if (!findings || findings.length === 0) {
    return (
      <div className="bg-dark-900 border border-slate-800 rounded-xl p-8 text-center">
        <Network className="w-10 h-10 text-slate-600 mx-auto mb-2" />
        <h3 className="text-sm font-bold text-slate-300">No Interconnected Nodes Yet</h3>
        <p className="text-xs text-slate-500 mt-1">
          Execute OSINT searches across modules to discover and map target linkages.
        </p>
      </div>
    );
  }

  // Derive unique nodes and connection groups
  const targets = Array.from(new Set(findings.map(f => f.target)));
  const sources = Array.from(new Set(findings.map(f => f.source)));

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 shadow-2xl space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <Network className="w-5 h-5 text-brand-400" />
            <span>Relational Evidence Link Graph</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Demonstrates corroborated connections between targets, infrastructure, handles, and public listings.
          </p>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className="px-2 py-0.5 rounded bg-dark-850 text-slate-300 border border-slate-800">
            {targets.length} Targets
          </span>
          <span className="px-2 py-0.5 rounded bg-dark-850 text-slate-300 border border-slate-800">
            {sources.length} Sources
          </span>
          <span className="px-2 py-0.5 rounded bg-brand-950 text-brand-400 border border-brand-800">
            {findings.length} Edges
          </span>
        </div>
      </div>

      {/* Visual Target Cluster Cards */}
      <div className="space-y-4">
        {targets.map((target, idx) => {
          const targetFindings = findings.filter(f => f.target === target);
          return (
            <div key={idx} className="bg-dark-850 border border-slate-800 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-brand-500 animate-pulse" />
                  <span className="font-mono text-xs font-bold text-slate-100">{target}</span>
                </div>
                <span className="text-[11px] text-slate-400 font-mono">
                  {targetFindings.length} Evidence Links
                </span>
              </div>

              {/* Edge Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {targetFindings.map((f) => (
                  <div
                    key={f.id}
                    className="p-3 rounded-lg bg-dark-900 border border-slate-800/80 hover:border-slate-700 transition text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sky-300">{f.source}</span>
                      <span className="font-mono text-[10px] text-slate-400">
                        {Math.round(f.confidence * 100)}% Conf
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-300 line-clamp-2">
                      {f.evidence_snippet}
                    </p>

                    <div className="pt-1 flex items-center justify-between text-[10px] text-slate-500 border-t border-slate-800">
                      <span className="uppercase">{f.module}</span>
                      <a
                        href={f.exact_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-brand-400 hover:text-brand-300 flex items-center space-x-1"
                      >
                        <span className="truncate max-w-[140px] font-mono">{f.exact_url}</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
