import React, { useState } from 'react';
import { MapPin, Search, Loader2, Globe, Server, Navigation, ExternalLink, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { api } from '../api';

export default function LocationSearch({ onResults }) {
  const [query, setQuery] = useState('');
  const [purpose, setPurpose] = useState('Geographic Infrastructure & Regional Footprint Audit');
  const [lawfulConfirmation, setLawfulConfirmation] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastLocationResult, setLastLocationResult] = useState(null);

  const quickTargets = [
    { label: 'GPS Coords', val: '48.8584, 2.2945' },
    { label: 'Public DNS IP', val: '8.8.8.8' },
    { label: 'Domain Host', val: 'cloudflare.com' },
    { label: 'Landmark', val: 'Eiffel Tower, Paris' }
  ];

  const handleSearch = async (e) => {
    e.preventDefault();
    setError('');
    const cleanQuery = query.trim();

    if (!cleanQuery) {
      setError('Please provide an IP address, domain, coordinates (lat, lon), or address.');
      return;
    }
    if (!purpose.trim()) {
      setError('Investigation purpose is mandatory.');
      return;
    }
    if (!lawfulConfirmation) {
      setError('You must confirm lawful purpose.');
      return;
    }

    setLoading(true);
    try {
      const findings = await api.searchLocation({
        query: cleanQuery,
        purpose: purpose.trim(),
        lawful_confirmation: lawfulConfirmation
      });

      // Find primary location metadata if available
      const primaryLoc = findings.find(f => f.raw_metadata?.latitude && f.raw_metadata?.longitude);
      if (primaryLoc) {
        setLastLocationResult(primaryLoc.raw_metadata);
      } else {
        setLastLocationResult(null);
      }

      onResults(findings, 'location', cleanQuery);
    } catch (err) {
      setError(err.message || 'Geointelligence inquiry failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <span>Location & Geointelligence Module</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
              IP / GPS / OpenStreetMap / BGP
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Geolocates public IP addresses, domain servers, GPS coordinate pairs, and addresses using OpenStreetMap and regional telecommunication registries.
          </p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-semibold text-slate-300">
              Target Identifier (IP Address, Hostname, GPS Coordinates, or Physical Place)
            </label>
            <div className="flex space-x-1.5 text-[11px]">
              {quickTargets.map((qt) => (
                <button
                  type="button"
                  key={qt.label}
                  onClick={() => setQuery(qt.val)}
                  className="px-2 py-0.5 rounded bg-dark-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700/60 font-mono transition"
                >
                  {qt.label}
                </button>
              ))}
            </div>
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <MapPin className="w-4 h-4 text-emerald-400" />
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. 104.244.42.1  OR  37.7749, -122.4194  OR  example.com  OR  Times Square, NY"
              className="w-full bg-dark-850 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono"
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
            placeholder="e.g. Server infrastructure and routing verification"
            className="w-full bg-dark-850 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>

        <div className="flex items-center space-x-2 pt-1">
          <input
            type="checkbox"
            id="lawful-confirm-loc"
            checked={lawfulConfirmation}
            onChange={(e) => setLawfulConfirmation(e.target.checked)}
            className="rounded bg-dark-900 border-slate-700 text-emerald-500 focus:ring-emerald-500 h-4 w-4"
          />
          <label htmlFor="lawful-confirm-loc" className="text-xs text-slate-300 font-medium cursor-pointer">
            I confirm this geointelligence inquiry complies with applicable legal authority, telecommunication privacy laws, and ethical intelligence standards.
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
          className="flex items-center justify-center space-x-2 w-full py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition shadow-lg shadow-emerald-950/50 disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Querying Spatial & Telecommunication Registries...</span>
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              <span>Execute Geolocation Audit</span>
            </>
          )}
        </button>
      </form>

      {/* Interactive Map & Telemetry Details Card */}
      {lastLocationResult && (
        <div className="mt-4 p-4 rounded-xl bg-dark-850 border border-emerald-900/60 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Navigation className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold text-slate-100">
                Spatial Coordinates: {lastLocationResult.latitude}, {lastLocationResult.longitude}
              </span>
            </div>
            <div className="flex items-center space-x-2 text-xs">
              {lastLocationResult.osm_url && (
                <a
                  href={lastLocationResult.osm_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center space-x-1 text-emerald-400 hover:text-emerald-300 underline font-mono text-[11px]"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>OpenStreetMap</span>
                </a>
              )}
              {lastLocationResult.google_maps_url && (
                <a
                  href={lastLocationResult.google_maps_url}
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

          {/* Embedded OpenStreetMap View */}
          <div className="relative w-full h-56 rounded-lg overflow-hidden border border-slate-700 bg-slate-900">
            <iframe
              title="OpenStreetMap View"
              width="100%"
              height="100%"
              frameBorder="0"
              scrolling="no"
              marginHeight="0"
              marginWidth="0"
              src={`https://www.openstreetmap.org/export/embed.html?bbox=${lastLocationResult.longitude - 0.03}%2C${lastLocationResult.latitude - 0.02}%2C${lastLocationResult.longitude + 0.03}%2C${lastLocationResult.latitude + 0.02}&layer=mapnik&marker=${lastLocationResult.latitude}%2C${lastLocationResult.longitude}`}
              className="w-full h-full opacity-90 hover:opacity-100 transition"
            />
          </div>

          {/* Telemetry Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs pt-1">
            <div className="p-2 rounded bg-dark-900 border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block font-semibold">City & Country</span>
              <span className="text-slate-200 font-medium truncate block">
                {lastLocationResult.city || lastLocationResult.address?.city || 'N/A'}, {lastLocationResult.country || lastLocationResult.address?.country || 'N/A'}
              </span>
            </div>
            <div className="p-2 rounded bg-dark-900 border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block font-semibold">Postal / Region</span>
              <span className="text-slate-200 font-medium truncate block">
                {lastLocationResult.postal_code || lastLocationResult.postcode || lastLocationResult.region || 'N/A'}
              </span>
            </div>
            <div className="p-2 rounded bg-dark-900 border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block font-semibold">ISP / Network</span>
              <span className="text-slate-200 font-medium truncate block">
                {lastLocationResult.isp || lastLocationResult.place_type || 'N/A'}
              </span>
            </div>
            <div className="p-2 rounded bg-dark-900 border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase block font-semibold">Autonomous System</span>
              <span className="text-slate-200 font-medium truncate block">
                {lastLocationResult.as || lastLocationResult.category || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
