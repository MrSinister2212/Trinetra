const API_BASE = '/api/v1';

// Default analyst token or session
let authToken = localStorage.getItem('trinetra_token') || '';

export const setAuthToken = (token) => {
  authToken = token;
  localStorage.setItem('trinetra_token', token);
};

export const getAuthToken = () => authToken;

const request = async (endpoint, options = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network request failed' }));
    throw new Error(errorData.detail || `HTTP Error ${response.status}`);
  }

  // Handle file downloads
  const disposition = response.headers.get('Content-Disposition');
  if (disposition && disposition.includes('attachment')) {
    return response.blob();
  }

  return response.json();
};

export const api = {
  // Auth
  login: (username, password) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  }),
  getMe: () => request('/auth/me'),

  // Risk Assessment
  assessRisk: (target, module) => request(`/search/assess-risk?target=${encodeURIComponent(target)}&module=${module}`),

  // Search Modules
  searchUsername: (data) => request('/search/username', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  searchEmailDomain: (data) => request('/search/email-domain', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  searchPhone: (data) => request('/search/phone', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  searchImage: (data) => request('/search/image', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  searchLocation: (data) => request('/search/location', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  searchDarkWeb: (data) => request('/search/darkweb', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Cases
  getCases: () => request('/cases'),
  createCase: (data) => request('/cases', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getCase: (id) => request(`/cases/${id}`),
  addFindingToCase: (caseId, finding) => request(`/cases/${caseId}/findings`, {
    method: 'POST',
    body: JSON.stringify(finding)
  }),

  // Reports
  createReport: (data) => request('/reports', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getReport: (id) => request(`/reports/${id}`),
  updateReport: (id, data) => request(`/reports/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),
  exportReport: async (reportId, format, filename = 'report') => {
    const blob = await request(`/reports/${reportId}/export/${format}`);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.${format === 'markdown' ? 'md' : format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  },

  // Audit Logs
  getAuditLogs: () => request('/audit'),

  // Real Artificial Intelligence Copilot & Vision
  getAiStatus: () => request('/ai/status'),
  configureAi: (data) => request('/ai/configure', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  chatWithAi: (data) => request('/ai/chat', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  analyzeImageAi: (data) => request('/ai/analyze-image', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  draftAINarrative: (findings, caseInfo, templateType = 'technical_report') => request('/ai/draft-narrative', {
    method: 'POST',
    body: JSON.stringify({ findings, case_info: caseInfo, template_type: templateType })
  }),
  correlateAILeads: (findings) => request('/ai/correlate-leads', {
    method: 'POST',
    body: JSON.stringify({ findings })
  })
};
