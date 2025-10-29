import { LucideIcon } from 'lucide-react';
import { formatCurrency, formatPercentage, getValueColor, getTrendIcon } from '../utils/format';

interface KPICardProps {
  title: string;
  value: number;
  format: 'currency' | 'percentage' | 'number';
  icon: LucideIcon;
  trend?: number;
  subtitle?: string;
  decimals?: number;
}

export function KPICard({ title, value, format, icon: Icon, trend, subtitle, decimals = 2 }: KPICardProps) {
  const formattedValue =
    format === 'currency' ? formatCurrency(value, decimals) :
    format === 'percentage' ? formatPercentage(value, decimals) :
    value.toFixed(decimals);

  const valueColorClass = trend !== undefined ? getValueColor(trend) : 'text-gray-900 dark:text-white';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow duration-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</h3>
        <Icon className="h-5 w-5 text-primary-500" />
      </div>

      <div className="space-y-2">
        <div className="flex items-baseline justify-between">
          <p className={`text-2xl font-bold ${valueColorClass}`}>
            {formattedValue}
          </p>
          {trend !== undefined && (
            <span className={`text-sm font-medium ${getValueColor(trend)}`}>
              {getTrendIcon(trend)} {formatPercentage(Math.abs(trend), 1)}
            </span>
          )}
        </div>

        {subtitle && (
          <p className="text-xs text-gray-500 dark:text-gray-400">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
