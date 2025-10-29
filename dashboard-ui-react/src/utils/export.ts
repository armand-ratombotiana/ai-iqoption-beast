import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { PortfolioStats, StrategyMetrics } from '../types/api';
import { evaluatorApi, downloadBlob } from '../services/api';

/**
 * Export portfolio stats to Excel
 */
export async function exportToExcel(data: PortfolioStats) {
  // Create workbook
  const wb = XLSX.utils.book_new();

  // Portfolio Overview sheet
  const portfolioData = [
    ['Metric', 'Value'],
    ['Initial Balance', `$${data.initial_balance}`],
    ['Current Balance', `$${data.current_balance}`],
    ['Daily P&L', `$${data.daily_pnl}`],
    ['ROI', `${data.roi}%`],
    ['Max Drawdown', `${data.max_drawdown}%`],
    ['Total Trades', data.total_trades],
    ['Total Wins', data.total_wins],
    ['Total Losses', data.total_losses],
    ['Win Rate', `${data.portfolio_win_rate}%`],
    ['Active Strategies', data.active_strategies],
  ];
  const portfolioSheet = XLSX.utils.aoa_to_sheet(portfolioData);
  XLSX.utils.book_append_sheet(wb, portfolioSheet, 'Portfolio');

  // Strategies sheet
  const strategiesData = [
    [
      'Strategy',
      'Trades',
      'Wins',
      'Losses',
      'Win Rate %',
      'Total P&L',
      'Avg Confidence %',
      'Sharpe Ratio',
      'Kelly Fraction',
      'Current Streak',
    ],
  ];

  Object.values(data.strategies).forEach((strategy: StrategyMetrics) => {
    strategiesData.push([
      strategy.strategy_name,
      strategy.total_trades.toString(),
      strategy.wins.toString(),
      strategy.losses.toString(),
      strategy.win_rate.toString(),
      strategy.total_pnl.toString(),
      strategy.avg_confidence.toString(),
      strategy.sharpe_ratio.toString(),
      strategy.kelly_fraction.toString(),
      strategy.current_streak.toString(),
    ]);
  });

  const strategiesSheet = XLSX.utils.aoa_to_sheet(strategiesData);
  XLSX.utils.book_append_sheet(wb, strategiesSheet, 'Strategies');

  // Generate and download
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  XLSX.writeFile(wb, `kael-dashboard-${timestamp}.xlsx`);
}

/**
 * Export portfolio stats to PDF
 */
export async function exportToPDF(data: PortfolioStats) {
  const doc = new jsPDF();

  // Title
  doc.setFontSize(20);
  doc.text('KAEL Ultimate Strategy Evaluator', 14, 22);

  // Timestamp
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);

  // Portfolio Overview
  doc.setFontSize(14);
  doc.text('Portfolio Overview', 14, 42);

  autoTable(doc, {
    startY: 48,
    head: [['Metric', 'Value']],
    body: [
      ['Initial Balance', `$${data.initial_balance.toFixed(2)}`],
      ['Current Balance', `$${data.current_balance.toFixed(2)}`],
      ['Daily P&L', `$${data.daily_pnl.toFixed(2)}`],
      ['ROI', `${data.roi.toFixed(2)}%`],
      ['Max Drawdown', `${data.max_drawdown.toFixed(2)}%`],
      ['Total Trades', data.total_trades.toString()],
      ['Win Rate', `${data.portfolio_win_rate.toFixed(2)}%`],
    ],
  });

  // Strategy Performance
  doc.addPage();
  doc.setFontSize(14);
  doc.text('Strategy Performance', 14, 22);

  const strategyRows = Object.values(data.strategies).map((s: StrategyMetrics) => [
    s.strategy_name,
    s.total_trades.toString(),
    `${s.win_rate.toFixed(1)}%`,
    `$${s.total_pnl.toFixed(2)}`,
    s.sharpe_ratio.toFixed(2),
  ]);

  autoTable(doc, {
    startY: 28,
    head: [['Strategy', 'Trades', 'Win Rate', 'P&L', 'Sharpe']],
    body: strategyRows,
  });

  // Download
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  doc.save(`kael-dashboard-${timestamp}.pdf`);
}

/**
 * Export trades to CSV (from backend)
 */
export async function exportTradesCSV(days: number = 7) {
  try {
    const blob = await evaluatorApi.exportCSV(days);
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    downloadBlob(blob, `kael-trades-${timestamp}.csv`);
  } catch (error) {
    console.error('Failed to export CSV:', error);
    throw error;
  }
}

/**
 * Export performance to JSON (from backend)
 */
export async function exportPerformanceJSON(days: number = 7) {
  try {
    const blob = await evaluatorApi.exportJSON(days);
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    downloadBlob(blob, `kael-performance-${timestamp}.json`);
  } catch (error) {
    console.error('Failed to export JSON:', error);
    throw error;
  }
}
