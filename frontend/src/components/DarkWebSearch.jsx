import React, { useState } from 'react';
import { Skull, Search, Loader2, AlertCircle, ShieldAlert, Lock, Unlock } from 'lucide-react';
import { api } from '../api';

export default function DarkWebSearch({ onResults, safetyGateData, onOpenGateModal }) {
  const [query, setQuery] = useState('');
  const [purpose, setPurpose] = useState('Brand Abuse & Monitored Credential Leak Ingestion');
  const [lawfulConfirmation, setLawfulConfirmation] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isUnlocked = Boolean(safetyGateData);

  const handleSearch = async (e) => {
    e.preventDefault();
    setError('');

    if (!isUnlocked) {
      onOpenGateModal();
      return;
    }

    if (!query.trim()) {
      setError('Please provide a search target.');
      return;
    }
    if (!purpose.trim()) {
      setError('Mandatory investigation purpose required.');
      return;
    }

    setLoading(true);
    try {
      const findings = await api.searchDarkWeb({
        query: query.trim(),
        purpose: purpose.trim(),
        lawful_confirmation: lawfulConfirmation,
        safety_gate: safetyGateData
      });
      onResults(findings, 'darkweb', query);
    } catch (err) {
      setError(err.message || 'Dark web search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-dark-900 border-2 border-rose-950 rounded-xl p-5 shadow-2xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-rose-900/60">
        <div>
          <h2 className="text-base font-bold text-rose-200 flex items-center space-x-2">
            <Skull className="w-5 h-5 text-rose-400" />
            <span>Dark Web & Onion Intelligence Module</span>
            <span className={`text-xs px-2 py-0.5 rounded uppercase font-mono font-bold border ${
              isUnlocked ? 'bg-amber-950 text-amber-400 border-amber-800' : 'bg-rose-950 text-rose-400 border-rose-800'
            }`}>
              {isUnlocked ? 'Gate Unlocked' : 'Gated Module'}
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Queries Ahmia onion index and leak-mention monitors with active content sanitization and hard-blocking.
          </p>
        </div>

        {!isUnlocked && (
          <button
            onClick={onOpenGateModal}
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-rose-900 hover:bg-rose-800 text-white font-bold text-xs transition"
          >
            <Lock className="w-3.5 h-3.5" />
            <span>Review & Unlock Safety Gate</span>
          </button>
        )}
      </div>

      {!isUnlocked ? (
        <div className="p-8 text-center bg-dark-850/80 rounded-xl border border-rose-900/50">
          <Lock className="w-10 h-10 text-rose-500 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-slate-200">Dark Web Module is Locked</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 mb-4">
            Under strict institutional safety controls, this module requires re-affirming all 6 isolation protocols and passing server-side Tor network verification.
          </p>
          <button
            onClick={onOpenGateModal}
            className="px-5 py-2.5 rounded-lg bg-rose-700 hover:bg-rose-600 text-white text-xs font-bold transition shadow-lg shadow-rose-950/60"
          >
            Open Safety Gate Verification
          </button>
        </div>
      ) : (
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Onion Search Query / Brand Token <span className="text-rose-400">*</span>
            </label>
            <div className="relative">
              <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. targetcorp.com, brandname, corporate_domain.io"
                className="w-full bg-dark-850 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Investigation Purpose <span className="text-rose-400">* (Mandatory Audit Requirement)</span>
            </label>
            <input
              type="text"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              placeholder="e.g. Brand protection incident triage / Credential leak monitoring"
              className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-rose-500"
            />
          </div>

          <div className="flex items-center space-x-2 pt-1">
            <input
              type="checkbox"
              id="lawful-confirm-dark"
              checked={lawfulConfirmation}
              onChange={(e) => setLawfulConfirmation(e.target.checked)}
              className="rounded bg-dark-900 border-slate-700 text-rose-500 focus:ring-rose-500 h-4 w-4"
            />
            <label htmlFor="lawful-confirm-dark" className="text-xs text-slate-300 font-medium cursor-pointer">
              I certify lawful purpose and confirm results will be viewed strictly as sanitized metadata.
            </label>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-rose-700 hover:bg-rose-600 text-white font-bold text-xs tracking-wide shadow-lg shadow-rose-950/50 disabled:opacity-50 transition"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Querying Sanitized Onion Index...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Execute Gated Dark Web Query</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
