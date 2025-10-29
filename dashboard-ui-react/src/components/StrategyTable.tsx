import { useMemo, useState } from 'react';
import { ArrowUpDown, TrendingUp, TrendingDown } from 'lucide-react';
import type { StrategyMetrics } from '../types/api';
import { formatCurrency, formatPercentage } from '../utils/format';

interface StrategyTableProps {
  strategies: Record<string, StrategyMetrics>;
}

type SortKey = keyof StrategyMetrics;
type SortDirection = 'asc' | 'desc';

export function StrategyTable({ strategies }: StrategyTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>('total_pnl');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const sortedStrategies = useMemo(() => {
    const strategiesArray = Object.values(strategies);

    return strategiesArray.sort((a, b) => {
      const aValue = a[sortKey];
      const bValue = b[sortKey];

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }

      return 0;
    });
  }, [strategies, sortKey, sortDirection]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('desc');
    }
  };

  const SortButton = ({ column }: { column: SortKey }) => (
    <button
      onClick={() => handleSort(column)}
      className="inline-flex items-center space-x-1 hover:text-primary-500 transition-colors"
    >
      <ArrowUpDown className="h-3 w-3" />
    </button>
  );

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Strategy Performance</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Strategy
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                <div className="flex items-center justify-end space-x-1">
                  <span>Trades</span>
                  <SortButton column="total_trades" />
                </div>
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                <div className="flex items-center justify-end space-x-1">
                  <span>Win Rate</span>
                  <SortButton column="win_rate" />
                </div>
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                <div className="flex items-center justify-end space-x-1">
                  <span>P&L</span>
                  <SortButton column="total_pnl" />
                </div>
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                <div className="flex items-center justify-end space-x-1">
                  <span>Sharpe</span>
                  <SortButton column="sharpe_ratio" />
                </div>
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                <div className="flex items-center justify-end space-x-1">
                  <span>Kelly</span>
                  <SortButton column="kelly_fraction" />
                </div>
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Streak
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {sortedStrategies.map((strategy) => {
              const isPositive = strategy.total_pnl > 0;
              const streakIcon = strategy.current_streak > 0 ? TrendingUp : TrendingDown;
              const StreakIcon = streakIcon;

              return (
                <tr
                  key={strategy.strategy_name}
                  className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {strategy.strategy_name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Confidence: {formatPercentage(strategy.avg_confidence, 1)}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                    {strategy.total_trades}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span
                      className={`text-sm font-medium ${
                        strategy.win_rate >= 60 ? 'text-success-600 dark:text-success-400' :
                        strategy.win_rate >= 50 ? 'text-yellow-600 dark:text-yellow-400' :
                        'text-danger-600 dark:text-danger-400'
                      }`}
                    >
                      {formatPercentage(strategy.win_rate, 1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span
                      className={`text-sm font-semibold ${
                        isPositive ? 'text-success-600 dark:text-success-400' : 'text-danger-600 dark:text-danger-400'
                      }`}
                    >
                      {formatCurrency(strategy.total_pnl, 2)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                    {strategy.sharpe_ratio.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                    {strategy.kelly_fraction.toFixed(3)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <div className="flex items-center justify-center space-x-1">
                      <StreakIcon
                        className={`h-4 w-4 ${
                          strategy.current_streak > 0 ? 'text-success-500' : 'text-danger-500'
                        }`}
                      />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {Math.abs(strategy.current_streak)}
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {sortedStrategies.length === 0 && (
        <div className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
          No strategy data available yet
        </div>
      )}
    </div>
  );
}
