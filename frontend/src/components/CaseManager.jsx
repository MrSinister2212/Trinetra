import React, { useState } from 'react';
import { Briefcase, Plus, FileText, CheckCircle2, Shield, Calendar, Tag, ArrowRight } from 'lucide-react';

export default function CaseManager({ cases, activeCase, onSelectCase, onCreateCase, onOpenReportBuilder }) {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [classification, setClassification] = useState('Confidential');
  const [tags, setTags] = useState('osint, intelligence, audit');

  const handleCreate = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    onCreateCase({
      title: title.trim(),
      description: description.trim(),
      investigator: 'Analyst',
      classification,
      tags: tags.split(',').map(t => t.trim()).filter(Boolean)
    });

    setTitle('');
    setDescription('');
    setShowCreateModal(false);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Create Button */}
      <div className="flex items-center justify-between bg-dark-900 border border-slate-800 p-5 rounded-xl">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <Briefcase className="w-5 h-5 text-brand-500" />
            <span>Investigation Dossiers & Case Management</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Collect findings, tag artifacts, maintain chain-of-custody, and compile defensible reports.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-lg shadow-brand-900/50 transition"
        >
          <Plus className="w-4 h-4" />
          <span>New Case Dossier</span>
        </button>
      </div>

      {/* Cases Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cases.map((c) => {
          const isActive = activeCase?.id === c.id;
          const findingsCount = c.findings?.length || 0;

          return (
            <div
              key={c.id}
              className={`p-5 rounded-xl border transition-all ${
                isActive
                  ? 'bg-dark-850 border-brand-500 shadow-xl shadow-brand-950/50 ring-1 ring-brand-500'
                  : 'bg-dark-900 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-[11px] text-slate-500">{c.id.slice(0, 13)}</span>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                    c.classification === 'Confidential'
                      ? 'bg-rose-950 text-rose-300 border border-rose-800'
                      : c.classification === 'Internal'
                      ? 'bg-amber-950 text-amber-300 border border-amber-800'
                      : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  }`}
                >
                  {c.classification}
                </span>
              </div>

              <h3 className="text-sm font-bold text-slate-100 line-clamp-1">{c.title}</h3>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2 min-h-[32px]">
                {c.description || 'No description provided.'}
              </p>

              {/* Tags */}
              <div className="flex flex-wrap gap-1 mt-3">
                {c.tags?.map((t, i) => (
                  <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-dark-950 text-slate-400 border border-slate-800">
                    #{t}
                  </span>
                ))}
              </div>

              {/* Stats & Actions */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-slate-400">
                  <strong className="text-slate-200">{findingsCount}</strong> Attached Findings
                </span>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => onSelectCase(c)}
                    className={`px-3 py-1 rounded text-xs font-semibold transition ${
                      isActive
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-dark-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {isActive ? 'Active Case ✓' : 'Set Active'}
                  </button>

                  <button
                    onClick={() => {
                      onSelectCase(c);
                      onOpenReportBuilder(c);
                    }}
                    className="p-1.5 rounded bg-brand-600 hover:bg-brand-500 text-white"
                    title="Build Report from Case"
                  >
                    <FileText className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Create Case Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-dark-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center space-x-2">
              <Briefcase className="w-5 h-5 text-brand-500" />
              <span>Create New Investigation Case</span>
            </h3>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Case Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Operation Horizon - Threat Footprint"
                  className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Scope & Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Scope of inquiry, target entities, and initial intelligence leads..."
                  rows={3}
                  className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Classification Label</label>
                <select
                  value={classification}
                  onChange={(e) => setClassification(e.target.value)}
                  className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                >
                  <option value="Confidential">Confidential (Default)</option>
                  <option value="Internal">Internal Use Only</option>
                  <option value="Public">Public Disclosure</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Tags (Comma-separated)</label>
                <input
                  type="text"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold"
                >
                  Create Dossier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
