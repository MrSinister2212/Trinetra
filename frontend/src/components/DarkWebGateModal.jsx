import React, { useState } from 'react';
import { Skull, AlertTriangle, ShieldAlert, CheckSquare, Square, Lock, KeyRound, Loader2 } from 'lucide-react';

export default function DarkWebGateModal({ isOpen, onClose, onUnlock }) {
  const [gates, setGates] = useState({
    amnesic_os_or_isolated_vm: false,
    hardware_devices_disabled: false,
    tor_connection_active: false,
    no_personal_accounts_logged: false,
    no_file_downloads_agreed: false,
    lawful_purpose_accepted: false
  });

  if (!isOpen) return null;

  const allChecked = Object.values(gates).every(Boolean);

  const toggleGate = (key) => {
    setGates(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleConfirm = () => {
    if (allChecked) {
      onUnlock(gates);
    }
  };

  const gateItems = [
    {
      id: 'amnesic_os_or_isolated_vm',
      label: 'Amnesic or Isolated Environment',
      desc: 'I am running Tails/Whonix or another amnesic or isolated OS/VM.'
    },
    {
      id: 'hardware_devices_disabled',
      label: 'Hardware Isolation',
      desc: 'Webcam and microphone are physically disabled or covered.'
    },
    {
      id: 'tor_connection_active',
      label: 'Active Tor Verification',
      desc: 'I am connecting through Tor (the backend strictly verifies via check.torproject.org and refuses otherwise).'
    },
    {
      id: 'no_personal_accounts_logged',
      label: 'Credential Isolation',
      desc: 'No personal or corporate accounts are logged in on this machine/session.'
    },
    {
      id: 'no_file_downloads_agreed',
      label: 'Prohibited Downloads Policy',
      desc: 'I will not download, render media, or open executable files from results.'
    },
    {
      id: 'lawful_purpose_accepted',
      label: 'Lawful Jurisdiction & Responsibility',
      desc: 'I have a lawful purpose (brand protection / breach mitigation) and accept full legal responsibility for my queries.'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="bg-dark-900 border-2 border-rose-800/80 rounded-2xl max-w-xl w-full p-6 shadow-2xl text-slate-100 glow-blue">
        {/* Header */}
        <div className="flex items-center space-x-3 pb-4 border-b border-rose-900/60">
          <div className="w-12 h-12 rounded-xl bg-rose-950 border border-rose-800 flex items-center justify-center text-rose-400">
            <Skull className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-rose-200 flex items-center space-x-2">
              <span>MANDATORY DARK WEB SAFETY GATE</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-rose-900 text-rose-200 uppercase font-mono font-bold tracking-wider">
                Gated
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Server-side verified gate. All 6 conditions must be affirmed.
            </p>
          </div>
        </div>

        {/* Hard Block Notice */}
        <div className="mt-4 p-3 rounded-lg bg-rose-950/40 border border-rose-900/80 text-rose-300 text-xs flex items-start space-x-2.5">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Hard-Blocked Content Categories:</span>
            <p className="text-rose-200/80 mt-0.5">
              CSAM, weapons, drug markets, hitman services, and hacking-for-hire are strictly blocked and filtered. Results return metadata only; scripts are stripped and all media downloads are blocked.
            </p>
          </div>
        </div>

        {/* Checkbox Gates */}
        <div className="mt-4 space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
          {gateItems.map((item) => {
            const isChecked = gates[item.id];
            return (
              <div
                key={item.id}
                onClick={() => toggleGate(item.id)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition flex items-start space-x-3 ${
                  isChecked
                    ? 'bg-rose-950/30 border-rose-700/80 text-slate-200'
                    : 'bg-dark-850 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="mt-0.5 shrink-0">
                  {isChecked ? (
                    <CheckSquare className="w-4 h-4 text-rose-400" />
                  ) : (
                    <Square className="w-4 h-4 text-slate-600" />
                  )}
                </div>
                <div>
                  <span className={`font-semibold block ${isChecked ? 'text-rose-300' : 'text-slate-300'}`}>
                    {item.label}
                  </span>
                  <span className="text-[11px] leading-relaxed opacity-90">{item.desc}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer actions */}
        <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          >
            Cancel & Return to Clearnet
          </button>

          <button
            onClick={handleConfirm}
            disabled={!allChecked}
            className={`flex items-center space-x-2 px-5 py-2.5 rounded-lg text-xs font-bold transition shadow-lg ${
              allChecked
                ? 'bg-rose-700 hover:bg-rose-600 text-white shadow-rose-900/50 cursor-pointer'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
            }`}
          >
            <KeyRound className="w-4 h-4" />
            <span>Verify & Unlock Dark Web Module</span>
          </button>
        </div>
      </div>
    </div>
  );
}
