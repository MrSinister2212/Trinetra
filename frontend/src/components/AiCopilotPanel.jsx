import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Brain, Send, Loader2, Settings, Key, CheckCircle2, AlertCircle, Bot, User, RefreshCw, Compass } from 'lucide-react';
import { api } from '../api';

export default function AiCopilotPanel({ findings, activeCase }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello Analyst. I am the TRINETRA Artificial Intelligence Copilot. I analyze collected OSINT evidence, formulate geographic hypotheses, correlate cross-platform handles, and recommend next investigative steps. How can I assist your case today?',
      provider: 'TRINETRA AI'
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [aiStatus, setAiStatus] = useState(null);

  // Configuration state
  const [geminiKey, setGeminiKey] = useState(localStorage.getItem('trinetra_gemini_key') || '');
  const [openaiKey, setOpenaiKey] = useState(localStorage.getItem('trinetra_openai_key') || '');
  const [ollamaUrl, setOllamaUrl] = useState(localStorage.getItem('trinetra_ollama_url') || 'http://localhost:11434');
  const [configSaving, setConfigSaving] = useState(false);
  const [configNotice, setConfigNotice] = useState('');

  const chatEndRef = useRef(null);

  const fetchStatus = async () => {
    try {
      const st = await api.getAiStatus();
      setAiStatus(st);
    } catch (e) {
      console.error('Failed to get AI status:', e);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    setConfigSaving(true);
    setConfigNotice('');
    try {
      localStorage.setItem('trinetra_gemini_key', geminiKey);
      localStorage.setItem('trinetra_openai_key', openaiKey);
      localStorage.setItem('trinetra_ollama_url', ollamaUrl);

      const updated = await api.configureAi({
        gemini_api_key: geminiKey || null,
        openai_api_key: openaiKey || null,
        ollama_url: ollamaUrl || 'http://localhost:11434'
      });
      setAiStatus(updated);
      setConfigNotice('AI configuration updated successfully.');
      setTimeout(() => setShowConfig(false), 1200);
    } catch (err) {
      setConfigNotice(`Configuration failed: ${err.message}`);
    } finally {
      setConfigSaving(false);
    }
  };

  const handleSendMessage = async (textToSend) => {
    const q = textToSend || inputQuery;
    if (!q.trim()) return;

    const userMsg = { role: 'user', content: q };
    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await api.chatWithAi({
        query: q,
        findings: findings || [],
        case_info: activeCase || { title: 'General Investigation' }
      });

      const assistantMsg = {
        role: 'assistant',
        content: res.response,
        provider: res.provider
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `Inquiry failed: ${err.message}`,
          provider: 'Error'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    'Where is this target or image likely located based on current evidence?',
    'Synthesize all findings and identify high-risk security exposures.',
    'Are there cross-platform correlations or handle variances in the evidence?',
    'What are the recommended next 3 OSINT steps I should execute?'
  ];

  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col h-[650px]">
      {/* Header Bar */}
      <div className="p-4 bg-dark-850 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-indigo-950 border border-indigo-800 text-indigo-400">
            <Brain className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
              <span>TRINETRA Artificial Intelligence Copilot</span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-bold ${
                aiStatus?.gemini_available
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : aiStatus?.openai_available
                  ? 'bg-sky-950 text-sky-400 border border-sky-800'
                  : aiStatus?.ollama_available
                  ? 'bg-amber-950 text-amber-400 border border-amber-800'
                  : 'bg-slate-800 text-slate-400 border border-slate-700'
              }`}>
                {aiStatus?.gemini_available ? 'Google Gemini' : aiStatus?.openai_available ? 'OpenAI GPT-4' : aiStatus?.ollama_available ? 'Local Ollama' : 'Offline Engine'}
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Conversational neural intelligence with citation-enforced evidence analysis.
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowConfig(!showConfig)}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-dark-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-xs font-semibold transition"
        >
          <Settings className="w-3.5 h-3.5" />
          <span>Configure AI Models</span>
        </button>
      </div>

      {/* Configuration Drawer */}
      {showConfig && (
        <div className="p-4 bg-dark-950 border-b border-indigo-900/60 text-xs space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="font-bold text-slate-200 flex items-center space-x-2">
              <Key className="w-4 h-4 text-amber-400" />
              <span>Artificial Intelligence Providers & API Keys</span>
            </span>
            <button onClick={() => setShowConfig(false)} className="text-slate-400 hover:text-slate-200">✕</button>
          </div>

          <form onSubmit={handleSaveConfig} className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                  Google Gemini API Key (Recommended)
                </label>
                <input
                  type="password"
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  placeholder="AIzaSy..."
                  className="w-full bg-dark-850 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                  OpenAI API Key (GPT-4o)
                </label>
                <input
                  type="password"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full bg-dark-850 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                  Local Ollama URL (Air-Gapped / Privacy)
                </label>
                <input
                  type="text"
                  value={ollamaUrl}
                  onChange={(e) => setOllamaUrl(e.target.value)}
                  placeholder="http://localhost:11434"
                  className="w-full bg-dark-850 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>
            </div>

            {configNotice && (
              <p className="text-[11px] text-emerald-400 font-semibold">{configNotice}</p>
            )}

            <div className="flex justify-end space-x-2 pt-1">
              <button
                type="submit"
                disabled={configSaving}
                className="px-3.5 py-1.5 rounded bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs transition disabled:opacity-50"
              >
                {configSaving ? 'Testing & Saving...' : 'Save AI Configuration'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3.5 bg-dark-900/60">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex space-x-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-indigo-950 border border-indigo-800 flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="w-4 h-4 text-cyan-400" />
              </div>
            )}
            <div
              className={`max-w-2xl rounded-xl p-3.5 text-xs leading-relaxed ${
                m.role === 'user'
                  ? 'bg-brand-600 text-white shadow-md'
                  : 'bg-dark-850 border border-slate-800 text-slate-200'
              }`}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>
              {m.provider && (
                <div className="mt-2 pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400">
                  <span className="font-mono">Engine: {m.provider}</span>
                  <span>{findings.length} findings in context</span>
                </div>
              )}
            </div>
            {m.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-brand-700 flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center space-x-2 text-xs text-indigo-400 p-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>AI Copilot is synthesizing evidence and formulating analysis...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Sample Inquiry Suggestion Chips */}
      <div className="px-4 py-2 bg-dark-850/80 border-t border-slate-800 flex items-center space-x-2 overflow-x-auto text-[11px]">
        <Compass className="w-3.5 h-3.5 text-slate-500 shrink-0" />
        {samplePrompts.map((p, i) => (
          <button
            key={i}
            onClick={() => handleSendMessage(p)}
            disabled={loading}
            className="px-2.5 py-1 rounded-full bg-dark-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/60 whitespace-nowrap transition disabled:opacity-50"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="p-3 bg-dark-850 border-t border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask the AI Copilot to correlate leads, estimate location, or draft investigative steps..."
            className="flex-1 bg-dark-900 border border-slate-700 rounded-lg px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="flex items-center space-x-1.5 px-4 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs transition disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Ask</span>
          </button>
        </form>
      </div>
    </div>
  );
}
