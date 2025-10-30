import { Activity, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';

interface Trade {
  instrument: string;
  direction: string;
  result: string | null;
  selected_strategy: string;
  payout_ratio: number;
}

interface MarketConditionsPanelProps {
  trades: Trade[];
}

export function MarketConditionsPanel({ trades }: MarketConditionsPanelProps) {
  // Analyze market conditions from recent trades
  const instrumentCount = new Map<string, number>();
  const directionCount = { CALL: 0, PUT: 0 };
  const winRateByInstrument = new Map<string, { wins: number; total: number }>();

  trades.forEach(trade => {
    // Count instruments
    instrumentCount.set(
      trade.instrument,
      (instrumentCount.get(trade.instrument) || 0) + 1
    );

    // Count directions
    if (trade.direction === 'CALL') directionCount.CALL++;
    else if (trade.direction === 'PUT') directionCount.PUT++;

    // Calculate win rates
    if (trade.result) {
      const current = winRateByInstrument.get(trade.instrument) || { wins: 0, total: 0 };
      winRateByInstrument.set(trade.instrument, {
        wins: current.wins + (trade.result === 'WIN' ? 1 : 0),
        total: current.total + 1
      });
    }
  });

  const mostTradedInstrument = Array.from(instrumentCount.entries())
    .sort((a, b) => b[1] - a[1])[0];

  const bestPerformingInstrument = Array.from(winRateByInstrument.entries())
    .filter(([, stats]) => stats.total >= 3)
    .sort((a, b) => (b[1].wins / b[1].total) - (a[1].wins / a[1].total))[0];

  const marketBias = directionCount.CALL > directionCount.PUT ? 'Bullish' : 'Bearish';
  const biasStrength = Math.abs(directionCount.CALL - directionCount.PUT) / trades.length;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
        <BarChart3 className="h-5 w-5" />
        Market Conditions Analysis
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Market Bias */}
        <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            {marketBias === 'Bullish' ? (
              <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-600 dark:text-red-400" />
            )}
            <h3 className="font-medium text-gray-900 dark:text-white">Market Bias</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{marketBias}</p>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
            {(biasStrength * 100).toFixed(0)}% strength
          </p>
          <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
            CALL: {directionCount.CALL} | PUT: {directionCount.PUT}
          </div>
        </div>

        {/* Most Active Instrument */}
        <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900 dark:to-purple-800 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-5 w-5 text-purple-600 dark:text-purple-400" />
            <h3 className="font-medium text-gray-900 dark:text-white">Most Active</h3>
          </div>
          {mostTradedInstrument ? (
            <>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {mostTradedInstrument[0]}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                {mostTradedInstrument[1]} trades
              </p>
              <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                {((mostTradedInstrument[1] / trades.length) * 100).toFixed(0)}% of total
              </div>
            </>
          ) : (
            <p className="text-sm text-gray-500">No data</p>
          )}
        </div>

        {/* Best Performing */}
        <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
            <h3 className="font-medium text-gray-900 dark:text-white">Top Performer</h3>
          </div>
          {bestPerformingInstrument ? (
            <>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {bestPerformingInstrument[0]}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                {((bestPerformingInstrument[1].wins / bestPerformingInstrument[1].total) * 100).toFixed(1)}% win rate
              </p>
              <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                {bestPerformingInstrument[1].wins}W / {bestPerformingInstrument[1].total - bestPerformingInstrument[1].wins}L
              </div>
            </>
          ) : (
            <p className="text-sm text-gray-500">Insufficient data</p>
          )}
        </div>
      </div>

      {/* Instrument Win Rates */}
      <div className="mt-6">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Win Rate by Instrument
        </h3>
        <div className="space-y-2">
          {Array.from(winRateByInstrument.entries())
            .sort((a, b) => (b[1].wins / b[1].total) - (a[1].wins / a[1].total))
            .slice(0, 5)
            .map(([instrument, stats]) => {
              const winRate = (stats.wins / stats.total) * 100;
              return (
                <div key={instrument} className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 w-24">
                    {instrument}
                  </span>
                  <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-4">
                    <div
                      className={`h-4 rounded-full transition-all ${
                        winRate >= 60 ? 'bg-green-500' : winRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(winRate, 100)}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white w-16 text-right">
                    {winRate.toFixed(0)}%
                  </span>
                  <span className="text-xs text-gray-500 w-12 text-right">
                    {stats.total}
                  </span>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}

export default MarketConditionsPanel;
