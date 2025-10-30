import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ApiService, Performance, Trade, StrategyStatsResponse, Config } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  // Data properties
  performance: Performance | null = null;
  config: Config | null = null;
  recentTrades: Trade[] = [];
  strategyStats: StrategyStatsResponse | null = null;
  lastUpdated: Date | null = null;
  botStatus: string = 'Loading...';

  // Filter states
  selectedTimeFilter: number | null = null;
  timeFilters = [
    { label: 'All Time', value: null },
    { label: 'Last Hour', value: 1 },
    { label: 'Last 24h', value: 24 },
    { label: 'Last 7 Days', value: 168 }
  ];

  // Loading states
  isLoading = true;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadInitialData();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadInitialData(): void {
    // Load configuration (doesn't change often)
    this.apiService.getConfig()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (config) => {
          this.config = config;
          this.botStatus = 'Active';
        },
        error: (err) => {
          this.error = 'Failed to load configuration';
          console.error(err);
        }
      });

    // Load strategy stats
    this.filterStrategies(null);
  }

  private startAutoRefresh(): void {
    // Auto-refresh performance every 10 seconds
    this.apiService.getPerformanceStream(10000)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (perf) => {
          this.performance = perf;
          this.lastUpdated = new Date();
          this.isLoading = false;
        },
        error: (err) => {
          this.error = 'Failed to load performance data';
          console.error(err);
          this.isLoading = false;
        }
      });

    // Auto-refresh recent trades every 10 seconds
    this.apiService.getRecentTradesStream(10, 10000)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.recentTrades = data.trades;
        },
        error: (err) => {
          console.error('Failed to load trades:', err);
        }
      });
  }

  filterStrategies(hours: number | null): void {
    this.selectedTimeFilter = hours;

    // Use stream for auto-refresh
    this.apiService.getStrategyStatsStream(hours || undefined, 10000)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (stats) => {
          this.strategyStats = stats;
        },
        error: (err) => {
          console.error('Failed to load strategy stats:', err);
        }
      });
  }

  // Control actions
  pauseTrading(): void {
    if (confirm('Pause trading?')) {
      this.apiService.pauseTrading().subscribe({
        next: (response) => {
          alert(response.message);
          this.botStatus = 'Paused';
        },
        error: (err) => {
          alert('Failed to pause trading');
          console.error(err);
        }
      });
    }
  }

  resumeTrading(): void {
    this.apiService.resumeTrading().subscribe({
      next: (response) => {
        alert(response.message);
        this.botStatus = 'Active';
      },
      error: (err) => {
        alert('Failed to resume trading');
        console.error(err);
      }
    });
  }

  stopBot(): void {
    if (confirm('Are you sure you want to stop the bot? This will shut down the system.')) {
      this.apiService.stopBot().subscribe({
        next: (response) => {
          alert(response.message);
          this.botStatus = 'Stopped';
        },
        error: (err) => {
          alert('Failed to stop bot');
          console.error(err);
        }
      });
    }
  }

  refreshData(): void {
    this.lastUpdated = new Date();
    // The streams will automatically refresh
  }

  // Utility methods
  formatCurrency(value: number | undefined): string {
    if (value === undefined) return '$0.00';
    return `$${value.toFixed(2)}`;
  }

  formatPercent(value: number | undefined): string {
    if (value === undefined) return '0%';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  }

  formatTime(timestamp: string | undefined): string {
    if (!timestamp) return '-';
    return new Date(timestamp).toLocaleTimeString();
  }

  getColorClass(value: number | undefined): string {
    if (value === undefined) return 'neutral';
    return value >= 0 ? 'positive' : 'negative';
  }

  // New methods for enhanced dashboard features

  getTopStrategies(count: number): any[] {
    if (!this.strategyStats || !this.strategyStats.strategy_stats) {
      return [];
    }
    return this.strategyStats.strategy_stats
      .sort((a, b) => b.total_profit - a.total_profit)
      .slice(0, count);
  }

  getBestStrategy(): string {
    const top = this.getTopStrategies(1);
    return top.length > 0 ? top[0].strategy_name : 'N/A';
  }

  getHighestWinRate(): number {
    if (!this.strategyStats || !this.strategyStats.strategy_stats) {
      return 0;
    }
    const rates = this.strategyStats.strategy_stats.map(s => s.win_rate);
    return rates.length > 0 ? Math.max(...rates) : 0;
  }

  getBestTrade(): string {
    if (!this.strategyStats || !this.strategyStats.strategy_stats) {
      return '$0.00';
    }
    const best = Math.max(...this.strategyStats.strategy_stats.map(s => s.best_trade || 0));
    return this.formatCurrency(best);
  }

  getAvgPayout(): number {
    if (!this.strategyStats || !this.strategyStats.strategy_stats) {
      return 0;
    }
    const payouts = this.strategyStats.strategy_stats
      .filter(s => s.avg_payout_percent)
      .map(s => s.avg_payout_percent);
    if (payouts.length === 0) return 0;
    const avg = payouts.reduce((a, b) => a + b, 0) / payouts.length;
    return Math.round(avg * 100) / 100;
  }

  getRiskPercentage(): number {
    if (!this.performance?.limits?.max_daily_loss || !this.performance?.summary?.daily_pnl) {
      return 0;
    }
    const used = Math.abs(this.performance.summary.daily_pnl);
    const limit = this.performance.limits.max_daily_loss;
    return Math.min(100, (used / limit) * 100);
  }

  isDailyLossReached(): boolean {
    if (!this.performance?.limits?.max_daily_loss || !this.performance?.summary?.daily_pnl) {
      return false;
    }
    return Math.abs(this.performance.summary.daily_pnl) >= this.performance.limits.max_daily_loss;
  }

  // Export and Analysis methods

  exportCSV(): void {
    const days = 7;
    window.open(`http://localhost:5001/export/csv?days=${days}`, '_blank');
  }

  exportJSON(): void {
    window.open('http://localhost:5001/export/json', '_blank');
  }

  viewPrometheus(): void {
    window.open('http://localhost:5001/metrics', '_blank');
  }

  showStrategyComparison(): void {
    alert('Strategy Comparison: This feature displays side-by-side comparison of all strategies with their metrics, Sharpe ratios, and Kelly fractions.');
    // TODO: Implement modal or separate view
  }

  showRiskAnalysis(): void {
    alert('Risk Analysis: This feature shows detailed risk metrics including drawdown analysis, volatility measurements, and position sizing recommendations.');
    // TODO: Implement modal or separate view
  }

  showBacktestData(): void {
    alert('Historical Data: This feature provides access to historical performance data and backtesting results for strategy validation.');
    // TODO: Implement modal or separate view
  }
}
