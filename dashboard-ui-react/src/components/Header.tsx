import { Moon, Sun, RefreshCw, Download, Settings } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import toast from 'react-hot-toast';

interface HeaderProps {
  onRefresh: () => void;
  onExport: () => void;
  isRefreshing: boolean;
  lastUpdate: string;
}

export function Header({ onRefresh, onExport, isRefreshing, lastUpdate }: HeaderProps) {
  const { theme, toggleTheme } = useTheme();

  const handleRefresh = () => {
    onRefresh();
    toast.success('Data refreshed');
  };

  const handleExport = () => {
    onExport();
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">K</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">KAEL Dashboard</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">Ultimate Strategy Evaluator</p>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-2">
            {/* Last Update */}
            {lastUpdate && (
              <div className="hidden sm:flex items-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <span className="text-xs text-gray-600 dark:text-gray-400">Last update:</span>
                <span className="text-xs font-medium text-gray-900 dark:text-white">{lastUpdate}</span>
              </div>
            )}

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Refresh data"
            >
              <RefreshCw className={`h-5 w-5 text-gray-700 dark:text-gray-300 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>

            {/* Export Button */}
            <button
              onClick={handleExport}
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              title="Export data"
            >
              <Download className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            </button>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              title="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              ) : (
                <Moon className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              )}
            </button>

            {/* Settings Button */}
            <button
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              title="Settings"
            >
              <Settings className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
