import React, { useState } from 'react';
import { Image as ImageIcon, Upload, Search, Loader2, AlertCircle, EyeOff, ShieldCheck, MapPin, ExternalLink, Sparkles, Navigation, Globe } from 'lucide-react';
import { api } from '../api';

export default function ImageSearch({ onResults }) {
  const [imageUrl, setImageUrl] = useState('');
  const [base64Image, setBase64Image] = useState('');
  const [fileName, setFileName] = useState('');
  const [purpose, setPurpose] = useState('Image Provenance Verification & Metadata Audit');
  const [lawfulConfirmation, setLawfulConfirmation] = useState(true);
  const [loading, setLoading] = useState(false);
  const [aiVisionLoading, setAiVisionLoading] = useState(false);
  const [error, setError] = useState('');
  const [latestGpsResult, setLatestGpsResult] = useState(null);
  const [reverseEngines, setReverseEngines] = useState(null);
  const [aiVisionResult, setAiVisionResult] = useState(null);

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setLatestGpsResult(null);
    setReverseEngines(null);
    setAiVisionResult(null);
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

      // Extract GPS & Reverse engines if present
      const gpsFinding = findings.find(f => f.category === 'Geolocation' && f.raw_metadata?.latitude);
      if (gpsFinding) {
        setLatestGpsResult(gpsFinding.raw_metadata);
      } else {
        setLatestGpsResult(null);
      }

      const provFinding = findings.find(f => f.raw_metadata?.engines);
      if (provFinding) {
        setReverseEngines(provFinding.raw_metadata.engines);
      }

      const aiFinding = findings.find(f => f.category === 'AI Visual Geolocation');
      if (aiFinding) {
        setAiVisionResult(aiFinding.raw_metadata?.full_ai_analysis || aiFinding.evidence_snippet);
      }

      onResults(findings, 'image', fileName || imageUrl);
    } catch (err) {
      setError(err.message || 'Image provenance inquiry failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDeepAiVision = async () => {
    if (!imageUrl && !base64Image) {
      setError('Upload an image first before requesting an AI Vision scan.');
      return;
    }
    setAiVisionLoading(true);
    setError('');
    try {
      const res = await api.analyzeImageAi({
        image_base64: base64Image || null,
        image_url: imageUrl.trim() || null,
        filename: fileName || 'target_image.jpg'
      });
      if (res.analysis) {
        setAiVisionResult(res.analysis);
      }
    } catch (err) {
      setError(err.message || 'AI Vision analysis failed');
    } finally {
      setAiVisionLoading(false);
    }
  };

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <span>Image Provenance & Geolocation Module</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-400 border border-indigo-800">
              EXIF / GPS / ELA / Reverse / AI Vision
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Analyzes camera headers, GPS tags, OpenStreetMap reverse geocoding, manipulation indicators (ELA), and reverse visual web provenance.
          </p>
        </div>
      </div>

      {/* Non-Biometric Guardrail Banner */}
      <div className="p-3 rounded-lg bg-dark-850 border border-slate-700/80 text-xs flex items-center space-x-3">
        <EyeOff className="w-5 h-5 text-rose-400 shrink-0" />
        <p className="text-slate-400">
          <strong>Strict Non-Biometric Architecture:</strong> TRINETRA strictly investigates image provenance, camera metadata, and geographic landmarks. It <strong>never</strong> performs facial recognition or biometric identity tracking.
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
            <label className="block text-xs font-semibold text-slate-300 mb-1">Option B: Upload Image File</label>
            <label className="flex items-center justify-center space-x-2 w-full bg-dark-850 border border-dashed border-slate-700 rounded-lg py-2.5 px-3 text-xs text-slate-400 cursor-pointer hover:border-slate-500 transition">
              <Upload className="w-4 h-4 text-brand-400" />
              <span className="truncate">{fileName || 'Choose image (.jpg, .png, .webp)...'}</span>
              <input type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>
        </div>

        {base64Image && (
          <div className="p-3 bg-dark-850 rounded-lg border border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img src={base64Image} alt="Upload preview" className="w-12 h-12 object-cover rounded border border-slate-700" />
              <div className="text-xs">
                <p className="font-semibold text-slate-200">{fileName}</p>
                <p className="text-[11px] text-emerald-400">Ready for forensic provenance scan</p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleDeepAiVision}
              disabled={aiVisionLoading}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-800 text-xs font-semibold transition"
            >
              {aiVisionLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-cyan-400" />}
              <span>AI Vision Geolocation Scan</span>
            </button>
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
            placeholder="e.g. Image provenance and geographic origin verification"
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
            I confirm this image provenance inquiry complies with applicable legal authority and copyright standards.
          </label>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-xs text-rose-300">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="flex items-center justify-center space-x-2 w-full py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition shadow-lg shadow-indigo-950/50 disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Extracting EXIF, GPS, ELA & Reverse Web Indexes...</span>
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              <span>Execute Image Forensics & Provenance Scan</span>
            </>
          )}
        </button>
      </form>

      {/* Actionable Reverse Visual Engines Bar */}
      {reverseEngines && (
        <div className="p-3 rounded-xl bg-dark-850 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
            <span className="flex items-center space-x-1.5">
              <Globe className="w-4 h-4 text-sky-400" />
              <span>Global Reverse Image Search Queries:</span>
            </span>
            <span className="text-[11px] text-slate-400">Click to trace image across engines</span>
          </div>
          <div className="flex flex-wrap gap-2 pt-1">
            {Object.entries(reverseEngines).map(([engineName, engineUrl]) => (
              <a
                key={engineName}
                href={engineUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-dark-900 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700 text-xs font-medium transition"
              >
                <span>{engineName}</span>
                <ExternalLink className="w-3 h-3 text-brand-400" />
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Embedded GPS Geolocation & Map Pin Card */}
      {latestGpsResult && (
        <div className="p-4 rounded-xl bg-dark-850 border border-emerald-900/60 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Navigation className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold text-slate-100">
                EXIF GPS Coordinates: {latestGpsResult.latitude}, {latestGpsResult.longitude}
              </span>
            </div>
            <div className="flex items-center space-x-2 text-xs">
              {latestGpsResult.osm_url && (
                <a
                  href={latestGpsResult.osm_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center space-x-1 text-emerald-400 hover:text-emerald-300 underline font-mono text-[11px]"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>OpenStreetMap</span>
                </a>
              )}
              {latestGpsResult.google_maps_url && (
                <a
                  href={latestGpsResult.google_maps_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center space-x-1 text-sky-400 hover:text-sky-300 underline font-mono text-[11px]"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>Google Maps</span>
                </a>
              )}
            </div>
          </div>

          {latestGpsResult.display_name && (
            <p className="text-xs text-emerald-300 font-medium bg-emerald-950/40 p-2.5 rounded-lg border border-emerald-900/50">
              Resolved Address: {latestGpsResult.display_name}
            </p>
          )}

          {/* Embedded OpenStreetMap Preview */}
          <div className="relative w-full h-56 rounded-lg overflow-hidden border border-slate-700 bg-slate-900">
            <iframe
              title="Image GPS Map"
              width="100%"
              height="100%"
              frameBorder="0"
              scrolling="no"
              marginHeight="0"
              marginWidth="0"
              src={`https://www.openstreetmap.org/export/embed.html?bbox=${latestGpsResult.longitude - 0.03}%2C${latestGpsResult.latitude - 0.02}%2C${latestGpsResult.longitude + 0.03}%2C${latestGpsResult.latitude + 0.02}&layer=mapnik&marker=${latestGpsResult.latitude}%2C${latestGpsResult.longitude}`}
              className="w-full h-full opacity-90 hover:opacity-100 transition"
            />
          </div>
        </div>
      )}

      {/* AI Vision Geolocation & Scene Findings */}
      {aiVisionResult && (
        <div className="p-4 rounded-xl bg-dark-850 border border-indigo-900/60 space-y-2">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold text-slate-100">
              Artificial Intelligence Vision Assessment:
            </span>
          </div>
          <div className="p-3 rounded-lg bg-dark-900 border border-slate-800 text-xs text-slate-300 whitespace-pre-wrap font-mono leading-relaxed max-h-72 overflow-y-auto">
            {aiVisionResult}
          </div>
        </div>
      )}
    </div>
  );
}
