import { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  Target,
  Activity,
  AlertCircle,
} from 'lucide-react';
import { Header } from './components/Header';
import { KPICard } from './components/KPICard';
import { StrategyTable } from './components/StrategyTable';
import { PerformanceChart } from './components/PerformanceChart';
import { usePortfolioStats } from './hooks/usePortfolioStats';
import { exportToExcel, exportToPDF } from './utils/export';
import { formatRelativeTime } from './utils/format';

function App() {
  const [autoRefresh] = useState(true);
  const { data, loading, error, refetch } = usePortfolioStats(autoRefresh, 5000);

  const handleExport = async () => {
    if (!data) {
      toast.error('No data available to export');
      return;
    }

    // Simple export for now - in production, you'd show a menu
    try {
      await exportToExcel(data);
      toast.success('Data exported to Excel successfully');
    } catch (err) {
      toast.error('Failed to export data');
      console.error(err);
    }
  };

  const lastUpdate = data ? formatRelativeTime(new Date().toISOString()) : '';

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="h-12 w-12 text-danger-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Connection Error</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
          <button
            onClick={refetch}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const roi = data.roi;
  const dailyChange = data.daily_pnl;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Toaster position="top-right" />

      <Header
        onRefresh={refetch}
        onExport={handleExport}
        isRefreshing={loading}
        lastUpdate={lastUpdate}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KPICard
            title="Current Balance"
            value={data.current_balance}
            format="currency"
            icon={Wallet}
            trend={roi}
            subtitle={`Start: $${data.initial_balance.toFixed(2)}`}
          />
          <KPICard
            title="Daily P&L"
            value={data.daily_pnl}
            format="currency"
            icon={dailyChange >= 0 ? TrendingUp : TrendingDown}
            trend={dailyChange}
            subtitle="Today's performance"
          />
          <KPICard
            title="Win Rate"
            value={data.portfolio_win_rate}
            format="percentage"
            icon={Target}
            subtitle={`${data.total_wins}W / ${data.total_losses}L`}
          />
          <KPICard
            title="Total Trades"
            value={data.total_trades}
            format="number"
            icon={Activity}
            decimals={0}
            subtitle={`${data.active_strategies} active strategies`}
          />
        </div>

        {/* Additional KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <KPICard
            title="ROI"
            value={data.roi}
            format="percentage"
            icon={TrendingUp}
            subtitle="Return on investment"
          />
          <KPICard
            title="Max Drawdown"
            value={data.max_drawdown}
            format="percentage"
            icon={TrendingDown}
            subtitle="Peak to trough decline"
          />
          <KPICard
            title="Active Strategies"
            value={data.active_strategies}
            format="number"
            icon={Activity}
            decimals={0}
            subtitle="Currently evaluating"
          />
        </div>

        {/* Performance Chart */}
        <div className="mb-8">
          <PerformanceChart strategies={data.strategies} />
        </div>

        {/* Strategy Table */}
        <StrategyTable strategies={data.strategies} />

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>KAEL Ultimate Strategy Evaluator v1.0.0</p>
          <p className="mt-1">
            Auto-refresh: {autoRefresh ? 'ON' : 'OFF'} • Update interval: 5s
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
