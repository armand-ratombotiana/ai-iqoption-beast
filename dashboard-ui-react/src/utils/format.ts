/**
 * Format currency value
 */
export function formatCurrency(value: number, decimals: number = 2): string {
  return `$${value.toFixed(decimals)}`;
}

/**
 * Format percentage value
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Format large numbers with K, M, B suffixes
 */
export function formatNumber(value: number): string {
  if (value >= 1_000_000_000) {
    return (value / 1_000_000_000).toFixed(1) + 'B';
  }
  if (value >= 1_000_000) {
    return (value / 1_000_000).toFixed(1) + 'M';
  }
  if (value >= 1_000) {
    return (value / 1_000).toFixed(1) + 'K';
  }
  return value.toFixed(0);
}

/**
 * Get color class based on value (positive/negative)
 */
export function getValueColor(value: number): string {
  if (value > 0) return 'text-success-500';
  if (value < 0) return 'text-danger-500';
  return 'text-gray-500 dark:text-gray-400';
}

/**
 * Get trend icon based on value
 */
export function getTrendIcon(value: number): string {
  if (value > 0) return '↗';
  if (value < 0) return '↘';
  return '→';
}

/**
 * Format timestamp to relative time
 */
export function formatRelativeTime(timestamp: string): string {
  const now = new Date();
  const time = new Date(timestamp);
  const diff = now.getTime() - time.getTime();

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return `${seconds}s ago`;
}

/**
 * Clamp value between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Calculate win rate from wins and total trades
 */
export function calculateWinRate(wins: number, total: number): number {
  return total > 0 ? (wins / total) * 100 : 0;
}
