import React, { useState } from 'react';
import { FileText, Download, ShieldCheck, Lock, Eye, AlertCircle, Check, Loader2, Sparkles, Sliders } from 'lucide-react';
import { api } from '../api';

export default function ReportBuilderModal({ isOpen, onClose, activeCase }) {
  const [templateType, setTemplateType] = useState('technical_report');
  const [reportTitle, setReportTitle] = useState(activeCase ? `OSINT Report - ${activeCase.title}` : 'OSINT Investigation Report');
  const [purpose, setPurpose] = useState(activeCase?.purpose || 'Authorized Digital Footprint & Security Investigation');
  const [lockReport, setLockReport] = useState(false);
  
  // Executive Summary text
  const [executiveSummary, setExecutiveSummary] = useState('');
  const [analystNarrative, setAnalystNarrative] = useState('');
  
  // Redaction rules
  const [maskEmails, setMaskEmails] = useState(false);
  const [maskPhones, setMaskPhones] = useState(false);
  const [maskGps, setMaskGps] = useState(false);
  const [maskUrls, setMaskUrls] = useState(false);
  const [maskUsernames, setMaskUsernames] = useState(false);
  const [customTerms, setCustomTerms] = useState('');

  const [loading, setLoading] = useState(false);
  const [generatedReport, setGeneratedReport] = useState(null);
  const [error, setError] = useState('');

  if (!isOpen || !activeCase) return null;

  const findings = activeCase.findings || [];

  // Helper to auto-draft citation-compliant executive summary
  const autoDraftCitationText = () => {
    if (findings.length === 0) {
      setError('Please attach at least one finding to this case first.');
      return;
    }
    const sampleCitations = findings.slice(0, 3).map(f => `[${f.id}]`).join(' and ');
    const draft = `An authorized open-source intelligence scan corroborated high-confidence findings across public directories ${sampleCitations}. Investigation confirmed active profile infrastructure without unauthorized credential access [${findings[0].id}].`;
    setExecutiveSummary(draft);
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const report = await api.createReport({
        case_id: activeCase.id,
        title: reportTitle.trim(),
        template_type: templateType,
        purpose: purpose.trim(),
        executive_summary: executiveSummary.trim(),
        analyst_narrative: analystNarrative.trim(),
        finding_ids: findings.map(f => f.id),
        redaction_rules: {
          mask_emails: maskEmails,
          mask_phones: maskPhones,
          mask_gps: maskGps,
          mask_urls: maskUrls,
          mask_usernames: maskUsernames,
          custom_terms: customTerms.split(',').map(s => s.trim()).filter(Boolean)
        },
        lock_report: lockReport
      });

      setGeneratedReport(report);
    } catch (err) {
      setError(err.message || 'Report synthesis rejected.');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    if (!generatedReport) return;
    try {
      await api.exportReport(generatedReport.id, format, `TRINETRA_${activeCase.id}_v${generatedReport.version}`);
    } catch (err) {
      setError(`Export failed: ${err.message}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
      <div className="bg-dark-900 border border-slate-700 rounded-2xl max-w-3xl w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-brand-600/20 border border-brand-500/40 flex items-center justify-center text-brand-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                <span>Defensible Report Builder</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-brand-950 text-brand-400 font-mono font-bold border border-brand-800">
                  Case: {activeCase.id.slice(0, 8)}
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Transforms {findings.length} findings into an auditable dossier with SHA-256 manifests.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 text-xs px-2.5 py-1 rounded hover:bg-slate-800"
          >
            ✕ Close
          </button>
        </div>

        {/* Integrity Rule Callout */}
        <div className="mt-4 p-3 rounded-lg bg-dark-850 border border-slate-700/80 text-xs">
          <div className="flex items-center space-x-2 font-semibold text-sky-400">
            <ShieldCheck className="w-4 h-4" />
            <span>Integrity Guardrail: Strict Citation Enforcement</span>
          </div>
          <p className="text-slate-400 mt-1">
            Every narrative sentence must cite valid Finding IDs (e.g. <code>[fnd_...]</code>).
            Uncited assertions are rejected by the integrity engine.
          </p>
        </div>

        <form onSubmit={handleGenerate} className="mt-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Report Title</label>
              <input
                type="text"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Select Report Template</label>
              <select
                value={templateType}
                onChange={(e) => setTemplateType(e.target.value)}
                className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
              >
                <option value="technical_report">Full Technical Report (Comprehensive)</option>
                <option value="executive_summary">Executive Summary (Strategic / Risk)</option>
                <option value="personal_footprint">Personal Footprint Audit (Takedowns & Settings)</option>
                <option value="brand_fraud">Brand Protection & Fraud Investigation</option>
              </select>
            </div>
          </div>

          {/* Executive Summary Narrative */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold text-slate-300">
                Executive Narrative <span className="text-slate-500 font-normal">(Must cite [fnd_id])</span>
              </label>
              <button
                type="button"
                onClick={autoDraftCitationText}
                className="text-[11px] text-brand-400 hover:text-brand-300 font-semibold flex items-center space-x-1"
              >
                <Sparkles className="w-3 h-3" />
                <span>Auto-Format Stored Citations</span>
              </button>
            </div>
            <textarea
              value={executiveSummary}
              onChange={(e) => setExecutiveSummary(e.target.value)}
              placeholder="e.g. Subject confirmed registered on GitHub [fnd_usr_01]. DNS exchangers point to corporate infrastructure [fnd_eml_01]."
              rows={3}
              className="w-full bg-dark-850 border border-slate-700 rounded-lg p-3 text-xs text-slate-100 font-mono focus:outline-none focus:border-brand-500"
            />
          </div>

          {/* Redaction Controls Panel */}
          <div className="p-3.5 bg-dark-850 border border-slate-800 rounded-xl space-y-2.5">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-200">
              <Sliders className="w-3.5 h-3.5 text-brand-400" />
              <span>Privacy & Redaction Controls (Pre-Export Masking)</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-slate-300">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={maskEmails}
                  onChange={(e) => setMaskEmails(e.target.checked)}
                  className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-3.5 w-3.5"
                />
                <span>Mask Emails</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={maskPhones}
                  onChange={(e) => setMaskPhones(e.target.checked)}
                  className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-3.5 w-3.5"
                />
                <span>Mask Phones</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={maskGps}
                  onChange={(e) => setMaskGps(e.target.checked)}
                  className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-3.5 w-3.5"
                />
                <span>Mask GPS Coordinates</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={maskUrls}
                  onChange={(e) => setMaskUrls(e.target.checked)}
                  className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-3.5 w-3.5"
                />
                <span>Mask Host URLs</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={maskUsernames}
                  onChange={(e) => setMaskUsernames(e.target.checked)}
                  className="rounded bg-dark-900 border-slate-700 text-brand-500 focus:ring-brand-500 h-3.5 w-3.5"
                />
                <span>Mask Usernames</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={lockReport}
                  onChange={(e) => setLockReport(e.target.checked)}
                  className="rounded bg-dark-900 border-slate-700 text-amber-500 focus:ring-amber-500 h-3.5 w-3.5"
                />
                <span className="font-semibold text-amber-400">Lock Final Version</span>
              </label>
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Generation Failure:</span>
                <p className="mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {/* Compile Button */}
          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-bold text-xs shadow-lg shadow-brand-900/50 disabled:opacity-50 transition"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Validating Citations & Compiling...</span>
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  <span>Compile Defensible Dossier</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Export Panel (Once compiled) */}
        {generatedReport && (
          <div className="mt-6 pt-5 border-t border-slate-800 bg-dark-850 p-4 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Check className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold text-emerald-400">
                  Dossier Compiled & Verified (Version {generatedReport.version})
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-400">
                SHA-256 Manifest: {generatedReport.hash_manifest?.length || 0} Artifacts
              </span>
            </div>

            <p className="text-xs text-slate-400">
              Download the finalized investigation report in any standard format:
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
              <button
                onClick={() => handleExport('pdf')}
                className="flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-rose-950/70 hover:bg-rose-900 border border-rose-800 text-rose-200 text-xs font-semibold transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>PDF Document</span>
              </button>

              <button
                onClick={() => handleExport('docx')}
                className="flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-sky-950/70 hover:bg-sky-900 border border-sky-800 text-sky-200 text-xs font-semibold transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>DOCX Word</span>
              </button>

              <button
                onClick={() => handleExport('html')}
                className="flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-cyan-950/70 hover:bg-cyan-900 border border-cyan-800 text-cyan-200 text-xs font-semibold transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>HTML Standalone</span>
              </button>

              <button
                onClick={() => handleExport('md')}
                className="flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-indigo-950/70 hover:bg-indigo-900 border border-indigo-800 text-indigo-200 text-xs font-semibold transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Markdown (GFM)</span>
              </button>

              <button
                onClick={() => handleExport('json')}
                className="flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-dark-900 hover:bg-dark-800 border border-slate-700 text-slate-300 text-xs font-semibold transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>JSON Schema</span>
              </button>

              <button
                onClick={() => handleExport('csv')}
                className="flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-dark-900 hover:bg-dark-800 border border-slate-700 text-slate-300 text-xs font-semibold transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>CSV Table</span>
              </button>

              <button
                onClick={() => handleExport('sha256')}
                className="col-span-2 flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-emerald-950/70 hover:bg-emerald-900 border border-emerald-800 text-emerald-200 text-xs font-semibold transition"
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Tamper-Evident SHA-256 Checksum</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
