import React, { useState } from 'react';
import { Image as ImageIcon, Upload, Search, Loader2, AlertCircle, EyeOff, ShieldCheck } from 'lucide-react';
import { api } from '../api';

export default function ImageSearch({ onResults }) {
  const [imageUrl, setImageUrl] = useState('');
  const [base64Image, setBase64Image] = useState('');
  const [fileName, setFileName] = useState('');
  const [purpose, setPurpose] = useState('Image Provenance Verification & Metadata Audit');
  const [lawfulConfirmation, setLawfulConfirmation] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (uploadEvent) => {
      setBase64Image(uploadEvent.target?.result || '');
      setImageUrl('');
    };
    reader.readAsDataURL(file);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setError('');

    if (!imageUrl && !base64Image) {
      setError('Please provide an image URL or upload an image file.');
      return;
    }
    if (!purpose.trim()) {
      setError('Mandatory investigation purpose required.');
      return;
    }
    if (!lawfulConfirmation) {
      setError('You must confirm lawful purpose.');
      return;
    }

    setLoading(true);
    try {
      const findings = await api.searchImage({
        image_url: imageUrl.trim() || null,
        image_base64: base64Image || null,
        filename: fileName || 'investigation_target.jpg',
        purpose: purpose.trim(),
        lawful_confirmation: lawfulConfirmation
      });
      onResults(findings, 'image', fileName || imageUrl);
    } catch (err) {
      setError(err.message || 'Image provenance inquiry failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <span>Image Provenance & Metadata Module</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-400 border border-indigo-800">
              EXIF / GPS / ELA Forensics
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Analyzes camera headers, GPS tags, manipulation indicators (ELA), and reverse web provenance.
          </p>
        </div>
      </div>

      {/* Non-Biometric Guardrail Banner */}
      <div className="p-3.5 rounded-lg bg-dark-850 border border-slate-700/80 mb-4 text-xs">
        <div className="flex items-center space-x-2 font-semibold text-slate-200">
          <EyeOff className="w-4 h-4 text-rose-400" />
          <span>Strict Non-Biometric Architecture:</span>
        </div>
        <p className="text-slate-400 mt-1">
          TRINETRA strictly investigates image provenance, origin metadata, and compression alterations. It <strong>never</strong> performs facial recognition, face matching, or biometric identity inferencing.
        </p>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Option A: Image URL */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Option A: Remote Image URL</label>
            <input
              type="text"
              value={imageUrl}
              onChange={(e) => {
                setImageUrl(e.target.value);
                if (e.target.value) {
                  setBase64Image('');
                  setFileName('');
                }
              }}
              placeholder="https://example.com/photo.jpg"
              className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
            />
          </div>

          {/* Option B: Local File */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Option B: Upload File Artifact</label>
            <label className="flex items-center justify-center space-x-2 w-full bg-dark-850 border border-dashed border-slate-700 rounded-lg py-2 px-3 text-xs text-slate-400 cursor-pointer hover:border-slate-500 transition">
              <Upload className="w-4 h-4 text-brand-400" />
              <span className="truncate">{fileName || 'Choose image (.jpg, .png, .tiff)...'}</span>
              <input type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>
        </div>

        {base64Image && (
          <div className="p-3 bg-dark-850 rounded-lg border border-slate-800 flex items-center space-x-3">
            <img src={base64Image} alt="Upload preview" className="w-12 h-12 object-cover rounded border border-slate-700" />
            <div className="text-xs">
              <p className="font-semibold text-slate-200">{fileName}</p>
              <p className="text-[11px] text-emerald-400">Ready for forensic provenance scan</p>
            </div>
          </div>
        )}

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">
            Investigation Purpose <span className="text-rose-400">* (Mandatory Audit Requirement)</span>
          </label>
          <input
            type="text"
            value={purpose}
            onChange={(e) => setPurpose(e.target.value)}
            placeholder="e.g. Image provenance and copyright verification"
            className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>

        <div className="flex items-center space-x-2 pt-1">
          <input
            type="checkbox"
            id="lawful-confirm-img"
            checked={lawfulConfirmation}
            onChange={(e) => setLawfulConfirmation(e.target.checked)}
            className="rounded bg-dark-900 border-slate-700 text-emerald-500 focus:ring-emerald-500 h-4 w-4"
          />
          <label htmlFor="lawful-confirm-img" className="text-xs text-slate-300 font-medium cursor-pointer">
            I confirm lawful investigation purpose and adhere to digital copyright & evidence rules.
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
                <span>Running ELA & Provenance Analysis...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Execute Image Forensics</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
