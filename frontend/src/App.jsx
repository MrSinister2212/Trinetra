import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ModuleSelector from './components/ModuleSelector';
import UsernameSearch from './components/UsernameSearch';
import EmailDomainSearch from './components/EmailDomainSearch';
import PhoneSearch from './components/PhoneSearch';
import ImageSearch from './components/ImageSearch';
import LocationSearch from './components/LocationSearch';
import DarkWebSearch from './components/DarkWebSearch';
import DarkWebGateModal from './components/DarkWebGateModal';
import FindingsTable from './components/FindingsTable';
import CaseManager from './components/CaseManager';
import LinkGraphView from './components/LinkGraphView';
import AuditLogView from './components/AuditLogView';
import AiCopilotPanel from './components/AiCopilotPanel';
import ReportBuilderModal from './components/ReportBuilderModal';
import { api, setAuthToken } from './api';
import { ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';

export default function App() {
  const [user, setUser] = useState(null);
  const [activeModule, setActiveModule] = useState('username');
  const [cases, setCases] = useState([]);
  const [activeCase, setActiveCase] = useState(null);
  const [allFindings, setAllFindings] = useState([]);
  const [darkWebUnlocked, setDarkWebUnlocked] = useState(false);
  const [darkWebSafetyData, setDarkWebSafetyData] = useState(null);
  const [showGateModal, setShowGateModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [bannerNotice, setBannerNotice] = useState(null);

  // Initialize and auto-authenticate default analyst
  useEffect(() => {
    const initApp = async () => {
      try {
        const loginRes = await api.login('analyst', 'trinetra2026');
        setAuthToken(loginRes.access_token);
        setUser(loginRes.user);

        // Fetch initial cases
        const caseList = await api.getCases();
        setCases(caseList);
        if (caseList.length > 0) {
          setActiveCase(caseList[0]);
          if (caseList[0].findings) {
            setAllFindings(caseList[0].findings);
          }
        }
      } catch (e) {
        console.error('Initialization error:', e);
      }
    };
    initApp();
  }, []);

  const showNotification = (msg, type = 'success') => {
    setBannerNotice({ msg, type });
    setTimeout(() => setBannerNotice(null), 4000);
  };

  const handleSearchResults = (newFindings, moduleName, queryTarget) => {
    setAllFindings(prev => [...newFindings, ...prev]);
    showNotification(`Discovered ${newFindings.length} findings for target "${queryTarget}" in ${moduleName.toUpperCase()}.`);
  };

  const handleAddToCase = async (finding) => {
    if (!activeCase) {
      showNotification('Please select or create an active Case Dossier first.', 'error');
      return;
    }

    try {
      await api.addFindingToCase(activeCase.id, finding);
      // Refresh case
      const updatedCase = await api.getCase(activeCase.id);
      setActiveCase(updatedCase);
      setCases(prev => prev.map(c => c.id === updatedCase.id ? updatedCase : c));
      showNotification(`Added Finding [${finding.id.slice(0, 9)}] to Case "${activeCase.title}".`);
    } catch (e) {
      showNotification(`Failed to attach evidence: ${e.message}`, 'error');
    }
  };

  const handleCreateCase = async (caseData) => {
    try {
      const created = await api.createCase(caseData);
      setCases(prev => [created, ...prev]);
      setActiveCase(created);
      showNotification(`Created Case Dossier: "${created.title}".`);
    } catch (e) {
      showNotification(`Failed to create case: ${e.message}`, 'error');
    }
  };

  const handleSelectModule = (modId) => {
    if (modId === 'darkweb' && !darkWebUnlocked) {
      setShowGateModal(true);
    }
    setActiveModule(modId);
  };

  const handleUnlockDarkWeb = (gates) => {
    setDarkWebUnlocked(true);
    setDarkWebSafetyData(gates);
    setShowGateModal(false);
    setActiveModule('darkweb');
    showNotification('Dark Web Safety Gate verified: Tor proxy access unlocked for current session.');
  };

  return (
    <div className="min-h-screen bg-dark-950 text-slate-100 flex flex-col">
      {/* Navigation Bar */}
      <Navbar
        activeCase={activeCase}
        cases={cases}
        onSelectCase={setActiveCase}
        user={user}
      />

      {/* Floating Notification Banner */}
      {bannerNotice && (
        <div className="fixed top-20 right-6 z-50 animate-bounce">
          <div className={`px-4 py-2.5 rounded-xl shadow-2xl flex items-center space-x-2 text-xs font-semibold border ${
            bannerNotice.type === 'error'
              ? 'bg-rose-950 text-rose-200 border-rose-800'
              : 'bg-emerald-950 text-emerald-200 border-emerald-800'
          }`}>
            {bannerNotice.type === 'error' ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
            <span>{bannerNotice.msg}</span>
          </div>
        </div>
      )}

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Navigation Tabs */}
        <ModuleSelector
          activeModule={activeModule}
          onSelectModule={handleSelectModule}
          darkWebUnlocked={darkWebUnlocked}
        />

        {/* Active Module Panel */}
        <div>
          {activeModule === 'username' && (
            <UsernameSearch onResults={handleSearchResults} activeCase={activeCase} />
          )}

          {activeModule === 'email_domain' && (
            <EmailDomainSearch onResults={handleSearchResults} />
          )}

          {activeModule === 'phone' && (
            <PhoneSearch onResults={handleSearchResults} />
          )}

          {activeModule === 'image' && (
            <ImageSearch onResults={handleSearchResults} />
          )}

          {activeModule === 'location' && (
            <LocationSearch onResults={handleSearchResults} />
          )}

          {activeModule === 'darkweb' && (
            <DarkWebSearch
              onResults={handleSearchResults}
              safetyGateData={darkWebSafetyData}
              onOpenGateModal={() => setShowGateModal(true)}
            />
          )}

          {activeModule === 'ai_copilot' && (
            <AiCopilotPanel findings={activeCase?.findings?.length ? activeCase.findings : allFindings} activeCase={activeCase} />
          )}

          {activeModule === 'graph' && (
            <LinkGraphView findings={activeCase?.findings?.length ? activeCase.findings : allFindings} />
          )}

          {activeModule === 'cases' && (
            <CaseManager
              cases={cases}
              activeCase={activeCase}
              onSelectCase={setActiveCase}
              onCreateCase={handleCreateCase}
              onOpenReportBuilder={(c) => {
                setActiveCase(c);
                setShowReportModal(true);
              }}
            />
          )}

          {activeModule === 'audit' && (
            <AuditLogView />
          )}
        </div>

        {/* Findings Table Section (Always available when search modules are active) */}
        {!['graph', 'cases', 'audit', 'ai_copilot'].includes(activeModule) && (
          <div className="pt-2">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-slate-200">
                Active Discovery Stream ({allFindings.length} Items)
              </h3>
              {activeCase && (
                <button
                  onClick={() => setShowReportModal(true)}
                  className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs tracking-wide shadow-lg shadow-emerald-950 transition"
                >
                  Compile Dossier Report ({activeCase.findings?.length || 0} Saved)
                </button>
              )}
            </div>

            <FindingsTable
              findings={allFindings}
              activeCase={activeCase}
              onAddToCase={handleAddToCase}
            />
          </div>
        )}
      </main>

      {/* Dark Web Safety Gate Modal */}
      <DarkWebGateModal
        isOpen={showGateModal}
        onClose={() => setShowGateModal(false)}
        onUnlock={handleUnlockDarkWeb}
      />

      {/* Report Builder Modal */}
      <ReportBuilderModal
        isOpen={showReportModal}
        onClose={() => setShowReportModal(false)}
        activeCase={activeCase}
      />

      {/* Institutional Legal & Ethics Footer */}
      <footer className="border-t border-slate-900 bg-dark-950 py-5 mt-auto">
        <div className="max-w-7xl mx-auto px-4 text-center text-[11px] text-slate-500 space-y-1">
          <p className="font-semibold text-slate-400">
            TRINETRA OSINT PLATFORM — Ethical, Defensible Open-Source Intelligence
          </p>
          <p>
            Operating strictly within public indexing boundaries. Compliant with GDPR, DPDP Act 2023, and CCPA guidelines.
            All searches are logged immutably with stated purpose. Zero private hacking, credential stuffing, or biometric facial tracking.
          </p>
        </div>
      </footer>
    </div>
  );
}
