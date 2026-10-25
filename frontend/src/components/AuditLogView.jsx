import React, { useEffect, useState } from 'react';
import { History, Shield, RefreshCw, Loader2, CheckCircle2 } from 'lucide-react';
import { api } from '../api';

export default function AuditLogView() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs();
      setLogs(data);
    } catch (e) {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
      <div className="p-4 bg-dark-850 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <History className="w-5 h-5 text-emerald-400" />
            <span>Immutable Investigation Audit Trail</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Every inquiry, case action, and report export is cryptographically recorded with stated purpose.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          disabled={loading}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-dark-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Audit Trail</span>
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-dark-950 text-slate-400 border-b border-slate-800">
              <th className="py-3 px-4 font-semibold w-40">Timestamp (UTC)</th>
              <th className="py-3 px-4 font-semibold w-28">Investigator</th>
              <th className="py-3 px-4 font-semibold w-36">Action / Module</th>
              <th className="py-3 px-4 font-semibold w-36">Target</th>
              <th className="py-3 px-4 font-semibold">Mandatory Stated Purpose</th>
              <th className="py-3 px-4 font-semibold w-24">IP Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80 font-mono text-[11px]">
            {logs.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500 font-sans text-xs">
                  {loading ? 'Loading immutable audit logs...' : 'No audit records logged yet.'}
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id} className="hover:bg-dark-850/60 transition">
                  <td className="py-2.5 px-4 text-slate-400">
                    {new Date(log.timestamp).toISOString().replace('T', ' ').slice(0, 19)}
                  </td>
                  <td className="py-2.5 px-4 text-slate-200 font-bold font-sans">
                    {log.username}
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="px-1.5 py-0.5 rounded bg-dark-950 text-cyan-400 border border-cyan-900/60 font-sans font-semibold text-[10px]">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-slate-300">
                    {log.target}
                  </td>
                  <td className="py-2.5 px-4 text-slate-300 font-sans">
                    {log.purpose}
                  </td>
                  <td className="py-2.5 px-4 text-slate-500">
                    {log.ip_address}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
