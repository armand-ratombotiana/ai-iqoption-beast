import axios from 'axios';
import type { PortfolioStats, HealthResponse, StrategiesResponse, StrategyMetrics } from '../types/api';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
      throw new Error(error.response.data.error || 'API request failed');
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
      throw new Error('Network error - please check if the evaluator is running');
    } else {
      // Something else happened
      console.error('Error:', error.message);
      throw new Error(error.message);
    }
  }
);

export const evaluatorApi = {
  // Health check
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  },

  // Get portfolio statistics
  async getStatistics(): Promise<PortfolioStats> {
    const response = await api.get<PortfolioStats>('/statistics');
    return response.data;
  },

  // Get all strategies
  async getStrategies(): Promise<StrategiesResponse> {
    const response = await api.get<StrategiesResponse>('/strategies');
    return response.data;
  },

  // Get specific strategy details
  async getStrategy(strategyName: string): Promise<StrategyMetrics> {
    const response = await api.get<StrategyMetrics>(`/strategy/${strategyName}`);
    return response.data;
  },

  // Export trades to CSV
  async exportCSV(days: number = 7): Promise<Blob> {
    const response = await api.get('/export/csv', {
      params: { days },
      responseType: 'blob',
    });
    return response.data;
  },

  // Export performance to JSON
  async exportJSON(days: number = 7): Promise<Blob> {
    const response = await api.get('/export/json', {
      params: { days },
      responseType: 'blob',
    });
    return response.data;
  },

  // Stop the evaluator
  async stop(): Promise<{ message: string }> {
    const response = await api.post('/stop');
    return response.data;
  },
};

// Helper function to download blob as file
export function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
