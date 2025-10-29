import { useState, useEffect, useCallback } from 'react';
import { evaluatorApi } from '../services/api';
import type { PortfolioStats } from '../types/api';

interface UsePortfolioStatsReturn {
  data: PortfolioStats | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function usePortfolioStats(autoRefresh: boolean = true, interval: number = 5000): UsePortfolioStatsReturn {
  const [data, setData] = useState<PortfolioStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const stats = await evaluatorApi.getStatistics();
      setData(stats);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch portfolio stats';
      setError(message);
      console.error('Error fetching portfolio stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const intervalId = setInterval(fetchData, interval);
    return () => clearInterval(intervalId);
  }, [autoRefresh, interval, fetchData]);

  return { data, loading, error, refetch: fetchData };
}
