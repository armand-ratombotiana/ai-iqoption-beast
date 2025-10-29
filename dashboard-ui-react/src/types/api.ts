export interface StrategyMetrics {
  strategy_name: string;
  total_trades: number;
  wins: number;
  losses: number;
  win_rate: number; // percentage
  total_pnl: number;
  avg_confidence: number; // percentage
  avg_payout: number;
  sharpe_ratio: number;
  kelly_fraction: number;
  max_consecutive_losses: number;
  current_streak: number;
  confidence_multiplier: number;
}

export interface PortfolioStats {
  initial_balance: number;
  current_balance: number;
  daily_pnl: number;
  roi: number; // percentage
  max_drawdown: number; // percentage
  total_trades: number;
  total_wins: number;
  total_losses: number;
  portfolio_win_rate: number; // percentage
  active_strategies: number;
  strategies: Record<string, StrategyMetrics>;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
}

export interface StrategiesResponse {
  strategies: Record<string, StrategyMetrics>;
  total: number;
}

export interface ErrorResponse {
  error: string;
}

export type Theme = 'light' | 'dark';

export interface DashboardSettings {
  theme: Theme;
  autoRefresh: boolean;
  refreshInterval: number; // seconds
  showAdvancedMetrics: boolean;
}
