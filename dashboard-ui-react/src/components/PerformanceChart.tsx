import { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { StrategyMetrics } from '../types/api';

interface PerformanceChartProps {
  strategies: Record<string, StrategyMetrics>;
}

export function PerformanceChart({ strategies }: PerformanceChartProps) {
  const chartData = useMemo(() => {
    return Object.values(strategies)
      .map((strategy) => ({
        name: strategy.strategy_name.replace(/_/g, ' ').slice(0, 15),
        'Win Rate': strategy.win_rate,
        'P&L': strategy.total_pnl,
        'Sharpe': strategy.sharpe_ratio * 10, // Scale for visibility
        wins: strategy.wins,
        losses: strategy.losses,
      }))
      .sort((a, b) => b['P&L'] - a['P&L']);
  }, [strategies]);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">{data.name}</p>
          <div className="space-y-1">
            <p className="text-xs text-success-600 dark:text-success-400">
              Win Rate: {data['Win Rate'].toFixed(1)}%
            </p>
            <p className="text-xs text-primary-600 dark:text-primary-400">
              P&L: ${data['P&L'].toFixed(2)}
            </p>
            <p className="text-xs text-purple-600 dark:text-purple-400">
              Sharpe: {(data['Sharpe'] / 10).toFixed(2)}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              W/L: {data.wins}/{data.losses}
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Strategy Comparison</h2>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
            <XAxis
              dataKey="name"
              angle={-45}
              textAnchor="end"
              height={100}
              className="text-xs fill-gray-600 dark:fill-gray-400"
            />
            <YAxis className="text-xs fill-gray-600 dark:fill-gray-400" />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Bar dataKey="Win Rate" fill="#22c55e" radius={[8, 8, 0, 0]} />
            <Bar dataKey="P&L" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
            <Bar dataKey="Sharpe" fill="#a855f7" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex items-center justify-center space-x-6 text-xs text-gray-600 dark:text-gray-400">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-success-500 rounded"></div>
          <span>Win Rate (%)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-primary-500 rounded"></div>
          <span>P&L ($)</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-purple-500 rounded"></div>
          <span>Sharpe (×10)</span>
        </div>
      </div>
    </div>
  );
}
