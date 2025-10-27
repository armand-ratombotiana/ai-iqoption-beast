import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval } from 'rxjs';
import { switchMap, startWith } from 'rxjs/operators';

export interface BotStatus {
  status: string;
  timestamp: string;
}

export interface PerformanceSummary {
  balance: number;
  daily_pnl: number;
  roi_percent: number;
  win_rate: number;
  total_trades: number;
  wins: number;
  losses: number;
}

export interface Performance {
  summary: PerformanceSummary;
  streaks: {
    current_win_streak: number;
    current_loss_streak: number;
    best_win_streak: number;
    worst_loss_streak: number;
  };
  limits: {
    max_concurrent_instruments: number;
    max_daily_loss: number;
    remaining_loss_budget: number;
  };
  timestamp: string;
}

export interface Trade {
  id: number;
  instrument: string;
  direction: string;
  amount: number;
  entry_time: string;
  exit_time?: string;
  result?: string;
  profit?: number;
  payout_ratio?: number;
  selected_strategy?: string;
}

export interface StrategyStats {
  strategy_name: string;
  total_trades: number;
  wins: number;
  losses: number;
  win_rate: number;
  total_profit: number;
  avg_profit_per_trade: number;
  best_trade: number;
  worst_trade: number;
  avg_payout_percent: number;
}

export interface StrategyStatsResponse {
  strategy_stats: StrategyStats[];
  time_period: string;
  total_strategies: number;
}

export interface Config {
  trading: {
    mode: string;
    min_payout_ratio: number;
    expiration_seconds: number;
  };
  strategy: {
    advanced_strategies_enabled: boolean;
    min_confidence: number | string;
    min_confluence: number | string;
    max_trade_amount: number | string;
  };
}

export interface ActiveTrades {
  active_count: number;
  active_trades: Trade[];
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5001';

  constructor(private http: HttpClient) {}

  // Health check
  getHealth(): Observable<BotStatus> {
    return this.http.get<BotStatus>(`${this.apiUrl}/health`);
  }

  // Performance metrics
  getPerformance(): Observable<Performance> {
    return this.http.get<Performance>(`${this.apiUrl}/performance`);
  }

  // Auto-refreshing performance (every 10 seconds)
  getPerformanceStream(intervalMs: number = 10000): Observable<Performance> {
    return interval(intervalMs).pipe(
      startWith(0),
      switchMap(() => this.getPerformance())
    );
  }

  // Configuration
  getConfig(): Observable<Config> {
    return this.http.get<Config>(`${this.apiUrl}/config`);
  }

  // Active trades
  getActiveTrades(): Observable<ActiveTrades> {
    return this.http.get<ActiveTrades>(`${this.apiUrl}/active_trades`);
  }

  // Recent trades
  getRecentTrades(limit: number = 10): Observable<{trades: Trade[]}> {
    return this.http.get<{trades: Trade[]}>(`${this.apiUrl}/recent_trades?limit=${limit}`);
  }

  // Auto-refreshing recent trades
  getRecentTradesStream(limit: number = 10, intervalMs: number = 10000): Observable<{trades: Trade[]}> {
    return interval(intervalMs).pipe(
      startWith(0),
      switchMap(() => this.getRecentTrades(limit))
    );
  }

  // Strategy statistics
  getStrategyStats(hours?: number): Observable<StrategyStatsResponse> {
    const url = hours
      ? `${this.apiUrl}/strategy_stats?hours=${hours}`
      : `${this.apiUrl}/strategy_stats`;
    return this.http.get<StrategyStatsResponse>(url);
  }

  // Auto-refreshing strategy stats
  getStrategyStatsStream(hours?: number, intervalMs: number = 10000): Observable<StrategyStatsResponse> {
    return interval(intervalMs).pipe(
      startWith(0),
      switchMap(() => this.getStrategyStats(hours))
    );
  }

  // Control actions
  pauseTrading(): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.apiUrl}/pause`, {});
  }

  resumeTrading(): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.apiUrl}/resume`, {});
  }

  stopBot(): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.apiUrl}/stop`, {});
  }
}
