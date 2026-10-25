import React, { useState } from 'react';
import { Search, Loader2, AlertCircle, ShieldCheck, Sparkles, Globe } from 'lucide-react';
import { api } from '../api';

export default function UsernameSearch({ onResults, activeCase }) {
  const [username, setUsername] = useState('');
  const [purpose, setPurpose] = useState('Authorized Identity Corroboration & Public Footprint Audit');
  const [lawfulConfirmation, setLawfulConfirmation] = useState(true);
  const [generateVariants, setGenerateVariants] = useState(true);
  const [checkWebMentions, setCheckWebMentions] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [riskAlert, setRiskAlert] = useState(null);

  const handleTargetChange = async (val) => {
    setUsername(val);
    if (val.length >= 3) {
      try {
        const assessment = await api.assessRisk(val, 'username');
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

    if (!username.trim()) {
      setError('Please provide a username target.');
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
      const findings = await api.searchUsername({
        username: username.trim(),
        generate_variants: generateVariants,
        check_web_mentions: checkWebMentions,
        purpose: purpose.trim(),
        lawful_confirmation: lawfulConfirmation,
        max_sites: 500
      });
      onResults(findings, 'username', username);
    } catch (err) {
      setError(err.message || 'Username query failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <span>Username Reconnaissance Module</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-sky-950 text-sky-400 border border-sky-800">
              766 Sites Configured
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Cross-checks handles across 500+ social, forum, code host, and gaming registries.
          </p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        {/* Username input */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">
            Target Username / Handle <span className="text-rose-400">*</span>
          </label>
          <div className="relative">
            <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={username}
              onChange={(e) => handleTargetChange(e.target.value)}
              placeholder="e.g. batman, alex-devsec, satoshi"
              className="w-full bg-dark-850 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
            />
          </div>
        </div>

        {/* Risk Warning Alert */}
        {riskAlert && (
          <div className="p-3 rounded-lg bg-amber-950/40 border border-amber-800/80 text-amber-300 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Privacy Awareness Alert (GDPR/DPDP/CCPA):</p>
              <p className="text-amber-200/90 mt-0.5">{riskAlert}</p>
            </div>
          </div>
        )}

        {/* Options */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <label className="flex items-center space-x-2.5 p-2.5 rounded-lg bg-dark-850 border border-slate-800 cursor-pointer hover:border-slate-700">
            <input
              type="checkbox"
              checked={generateVariants}
              onChange={(e) => setGenerateVariants(e.target.checked)}
              className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-4 w-4"
            />
            <div className="text-xs">
              <span className="font-semibold text-slate-200 flex items-center">
                <Sparkles className="w-3.5 h-3.5 mr-1 text-cyan-400" /> Generate Leetspeak & Affix Variants
              </span>
              <p className="text-[11px] text-slate-400">Generates b4tman, batman_, batman123</p>
            </div>
          </label>

          <label className="flex items-center space-x-2.5 p-2.5 rounded-lg bg-dark-850 border border-slate-800 cursor-pointer hover:border-slate-700">
            <input
              type="checkbox"
              checked={checkWebMentions}
              onChange={(e) => setCheckWebMentions(e.target.checked)}
              className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-4 w-4"
            />
            <div className="text-xs">
              <span className="font-semibold text-slate-200 flex items-center">
                <Globe className="w-3.5 h-3.5 mr-1 text-sky-400" /> Web Mentions & Wayback Archive
              </span>
              <p className="text-[11px] text-slate-400">Queries Wayback CDX and search indices</p>
            </div>
          </label>
        </div>

        {/* Mandatory Purpose Field */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">
            Investigation Purpose <span className="text-rose-400">* (Mandatory Audit Requirement)</span>
          </label>
          <input
            type="text"
            value={purpose}
            onChange={(e) => setPurpose(e.target.value)}
            placeholder="e.g. Brand protection inquiry / Defensible forensic timeline"
            className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>

        {/* Lawful Declaration Toggle */}
        <div className="flex items-center space-x-2 pt-1">
          <input
            type="checkbox"
            id="lawful-confirm-user"
            checked={lawfulConfirmation}
            onChange={(e) => setLawfulConfirmation(e.target.checked)}
            className="rounded bg-dark-900 border-slate-700 text-emerald-500 focus:ring-emerald-500 h-4 w-4"
          />
          <label htmlFor="lawful-confirm-user" className="text-xs text-slate-300 font-medium cursor-pointer">
            I confirm lawful investigation purpose and adhere to applicable privacy protections.
          </label>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-3 rounded-lg bg-rose-950/50 border border-rose-800 text-rose-300 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Submit */}
        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs tracking-wide shadow-lg shadow-brand-900/50 disabled:opacity-50 transition"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Scanning 500+ Platforms...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Run Username Scan</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
