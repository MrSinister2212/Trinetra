import React, { useState } from 'react';
import { Phone, Search, Loader2, AlertCircle, ShieldCheck, Lock } from 'lucide-react';
import { api } from '../api';

export default function PhoneSearch({ onResults }) {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [region, setRegion] = useState('US');
  const [purpose, setPurpose] = useState('Public Footprint & Corporate Contact Audit');
  const [lawfulConfirmation, setLawfulConfirmation] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    setError('');

    if (!phoneNumber.trim()) {
      setError('Please provide a phone number.');
      return;
    }
    if (!purpose.trim()) {
      setError('Mandatory investigation purpose required.');
      return;
    }
    if (!lawfulConfirmation) {
      setError('You must affirm lawful purpose confirmation.');
      return;
    }

    setLoading(true);
    try {
      const findings = await api.searchPhone({
        phone_number: phoneNumber.trim(),
        default_region: region,
        purpose: purpose.trim(),
        lawful_confirmation: lawfulConfirmation
      });
      onResults(findings, 'phone', phoneNumber);
    } catch (err) {
      setError(err.message || 'Phone inquiry failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <span>Phone Footprint Module</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
              ITU-T Telecommunication
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Parses carrier, line type, and open web public listings without querying personal broker databases.
          </p>
        </div>
      </div>

      {/* Strict Ethical Guardrail Banner */}
      <div className="p-3.5 rounded-lg bg-dark-850 border border-slate-700/80 mb-4 text-xs">
        <div className="flex items-center space-x-2 font-semibold text-slate-200">
          <Lock className="w-4 h-4 text-cyan-400" />
          <span>Non-Intrusive Public Footprint Guardrails Active:</span>
        </div>
        <p className="text-slate-400 mt-1">
          TRINETRA validates numbering plans and public corporate web mentions. It <strong>never</strong> queries consumer people-search brokers, leaked contact books, or cellular location trackers.
        </p>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="sm:col-span-3">
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Target Phone Number <span className="text-rose-400">*</span>
            </label>
            <div className="relative">
              <Phone className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="e.g. +1 650 253 0000 or (415) 555-2671"
                className="w-full bg-dark-850 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Default Region</label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-brand-500"
            >
              <option value="US">US / North America (+1)</option>
              <option value="GB">United Kingdom (+44)</option>
              <option value="IN">India (+91)</option>
              <option value="DE">Germany (+49)</option>
              <option value="FR">France (+33)</option>
              <option value="AU">Australia (+61)</option>
              <option value="CA">Canada (+1)</option>
            </select>
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
            placeholder="e.g. Public company listing verification / Authorized security inquiry"
            className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>

        <div className="flex items-center space-x-2 pt-1">
          <input
            type="checkbox"
            id="lawful-confirm-phone"
            checked={lawfulConfirmation}
            onChange={(e) => setLawfulConfirmation(e.target.checked)}
            className="rounded bg-dark-900 border-slate-700 text-emerald-500 focus:ring-emerald-500 h-4 w-4"
          />
          <label htmlFor="lawful-confirm-phone" className="text-xs text-slate-300 font-medium cursor-pointer">
            I confirm lawful investigation basis (e.g. corporate verification or authorized subject audit).
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
                <span>Auditing Telecom Registry...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Analyze Phone Footprint</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
