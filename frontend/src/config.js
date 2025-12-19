/**
 * API Configuration
 * Automatically switches between development and production
 */

const isDevelopment = import.meta.env.DEV;

// Backend URLs
export const API_BASE_URL = isDevelopment 
  ? 'http://127.0.0.1:8001'  // Local development
  : 'https://financial-intelligence-backend-production.up.railway.app';  // Production (update after Railway deployment)

// API Endpoints
export const API_ENDPOINTS = {
  // Health & Stats
  health: `${API_BASE_URL}/api/health`,
  stats: `${API_BASE_URL}/api/stats`,
  
  // Companies
  companies: `${API_BASE_URL}/api/companies`,
  company: (name) => `${API_BASE_URL}/api/company/${name}`,
  search: `${API_BASE_URL}/api/search`,
  
  // Documents
  documents: `${API_BASE_URL}/api/documents`,
  upload: `${API_BASE_URL}/api/documents/upload`,
  
  // Alerts
  alerts: `${API_BASE_URL}/api/alerts`,
};

// Helper function to build URL with query params
export const buildUrl = (endpoint, params = {}) => {
  const url = new URL(endpoint);
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null) {
      url.searchParams.append(key, params[key]);
    }
  });
  return url.toString();
};

export default {
  API_BASE_URL,
  API_ENDPOINTS,
  buildUrl,
};