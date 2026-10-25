import React from 'react';
import { UserSearch, Mail, Phone, Image as ImageIcon, Skull, Network, Briefcase, History } from 'lucide-react';

export default function ModuleSelector({ activeModule, onSelectModule, darkWebUnlocked }) {
  const modules = [
    { id: 'username', label: 'Username Search', icon: UserSearch, badge: '500+ Sites' },
    { id: 'email_domain', label: 'Email & Domain', icon: Mail, badge: 'MX/HIBP/CT' },
    { id: 'phone', label: 'Phone Footprint', icon: Phone, badge: 'Public E.164' },
    { id: 'image', label: 'Image Provenance', icon: ImageIcon, badge: 'EXIF / ELA' },
    {
      id: 'darkweb',
      label: 'Dark Web Search',
      icon: Skull,
      badge: darkWebUnlocked ? 'UNLOCKED' : 'GATED',
      isGated: true
    },
    { id: 'graph', label: 'Link Graph', icon: Network },
    { id: 'cases', label: 'Case Dossiers', icon: Briefcase },
    { id: 'audit', label: 'Audit Trail', icon: History },
  ];

  return (
    <nav className="flex space-x-1.5 overflow-x-auto pb-1 border-b border-slate-800">
      {modules.map((m) => {
        const Icon = m.icon;
        const isActive = activeModule === m.id;
        return (
          <button
            key={m.id}
            onClick={() => onSelectModule(m.id)}
            className={`flex items-center space-x-2 px-3.5 py-2.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
              isActive
                ? 'bg-brand-600 text-white shadow-lg shadow-brand-900/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-dark-850'
            }`}
          >
            <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
            <span>{m.label}</span>
            {m.badge && (
              <span
                className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold tracking-tight ${
                  m.id === 'darkweb'
                    ? darkWebUnlocked
                      ? 'bg-amber-950 text-amber-400 border border-amber-800/80'
                      : 'bg-rose-950 text-rose-400 border border-rose-800/80'
                    : isActive
                    ? 'bg-brand-700/80 text-white'
                    : 'bg-slate-800 text-slate-300'
                }`}
              >
                {m.badge}
              </span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
