import React, { useState } from 'react';
import { Mail, Search, Loader2, AlertCircle, ShieldAlert, Server, Network } from 'lucide-react';
import { api } from '../api';

export default function EmailDomainSearch({ onResults }) {
  const [query, setQuery] = useState('');
  const [purpose, setPurpose] = useState('Infrastructure Audit & Authorized Incident Investigation');
  const [lawfulConfirmation, setLawfulConfirmation] = useState(true);
  const [checkBreaches, setCheckBreaches] = useState(true);
  const [checkSubdomains, setCheckSubdomains] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [riskAlert, setRiskAlert] = useState(null);

  const handleTargetChange = async (val) => {
    setQuery(val);
    if (val.includes('@')) {
      try {
        const assessment = await api.assessRisk(val, 'email_domain');
        if (assessment.is_individual) {
          setRiskAlert(assessment.warning_reason);
        } else {
          setRiskAlert(null);
        }
      } catch (e) {
        // ignore
      }
    } else {
      setRiskAlert(null);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setError('');

    if (!query.trim()) {
      setError('Please provide an email or domain target.');
      return;
    }
    if (!purpose.trim()) {
      setError('Mandatory investigation purpose required.');
      return;
    }
    if (!lawfulConfirmation) {
      setError('You must confirm lawful purpose and privacy compliance.');
      return;
    }

    setLoading(true);
    try {
      const findings = await api.searchEmailDomain({
        query: query.trim(),
        check_breaches: checkBreaches,
        check_subdomains: checkSubdomains,
        check_ct_logs: true,
        purpose: purpose.trim(),
        lawful_confirmation: lawfulConfirmation
      });
      onResults(findings, 'email_domain', query);
    } catch (err) {
      setError(err.message || 'Email/Domain inquiry failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <span>Email & Domain Infrastructure Module</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
              DNS / RDAP / CT / HIBP
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Parses MX routing, audits incident exposures without credentials, and queries CT certificate logs.
          </p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">
            Target Email or Domain <span className="text-rose-400">*</span>
          </label>
          <div className="relative">
            <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => handleTargetChange(e.target.value)}
              placeholder="e.g. security@targetcorp.com or targetcorp.com"
              className="w-full bg-dark-850 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
            />
          </div>
        </div>

        {riskAlert && (
          <div className="p-3 rounded-lg bg-amber-950/40 border border-amber-800/80 text-amber-300 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Consumer Email Provider Detected:</p>
              <p className="text-amber-200/90 mt-0.5">{riskAlert}</p>
            </div>
          </div>
        )}

        {/* Feature Checkboxes */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <label className="flex items-center space-x-2.5 p-2.5 rounded-lg bg-dark-850 border border-slate-800 cursor-pointer hover:border-slate-700">
            <input
              type="checkbox"
              checked={checkBreaches}
              onChange={(e) => setCheckBreaches(e.target.checked)}
              className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-4 w-4"
            />
            <div className="text-xs">
              <span className="font-semibold text-slate-200 flex items-center">
                <ShieldAlert className="w-3.5 h-3.5 mr-1 text-rose-400" /> HIBP Incident Check
              </span>
              <p className="text-[11px] text-slate-400">Reports breach occurrence (passwords never queried)</p>
            </div>
          </label>

          <label className="flex items-center space-x-2.5 p-2.5 rounded-lg bg-dark-850 border border-slate-800 cursor-pointer hover:border-slate-700">
            <input
              type="checkbox"
              checked={checkSubdomains}
              onChange={(e) => setCheckSubdomains(e.target.checked)}
              className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-4 w-4"
            />
            <div className="text-xs">
              <span className="font-semibold text-slate-200 flex items-center">
                <Network className="w-3.5 h-3.5 mr-1 text-cyan-400" /> Certificate Transparency (crt.sh)
              </span>
              <p className="text-[11px] text-slate-400">Discovers active subdomains from TLS logs</p>
            </div>
          </label>
        </div>

        {/* Purpose */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">
            Investigation Purpose <span className="text-rose-400">* (Mandatory Audit Requirement)</span>
          </label>
          <input
            type="text"
            value={purpose}
            onChange={(e) => setPurpose(e.target.value)}
            placeholder="e.g. Authorized domain audit / Security hygiene verification"
            className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>

        <div className="flex items-center space-x-2 pt-1">
          <input
            type="checkbox"
            id="lawful-confirm-email"
            checked={lawfulConfirmation}
            onChange={(e) => setLawfulConfirmation(e.target.checked)}
            className="rounded bg-dark-900 border-slate-700 text-emerald-500 focus:ring-emerald-500 h-4 w-4"
          />
          <label htmlFor="lawful-confirm-email" className="text-xs text-slate-300 font-medium cursor-pointer">
            I confirm lawful purpose and acknowledge that no private credentials will be processed.
          </label>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-rose-950/50 border border-rose-800 text-rose-300 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs tracking-wide shadow-lg shadow-brand-900/50 disabled:opacity-50 transition"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Auditing Infrastructure...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Run Email & Domain Scan</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
