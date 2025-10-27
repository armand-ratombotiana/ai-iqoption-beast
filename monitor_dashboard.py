#!/usr/bin/env python3
"""
🔍 KAEL TRADING BOT - LIVE MONITORING DASHBOARD
Real-time monitoring of the trading bot's performance
"""

import requests
import time
import json
from datetime import datetime
import os
import sys

API_URL = "http://localhost:5001"
REFRESH_INTERVAL = 5  # seconds


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_statistics():
    """Fetch bot statistics"""
    try:
        response = requests.get(f"{API_URL}/statistics", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return {"error": str(e)}


def get_recent_trades(limit=10):
    """Fetch recent trades"""
    try:
        response = requests.get(f"{API_URL}/recent_trades?limit={limit}", timeout=5)
        if response.status_code == 200:
            return response.json().get('trades', [])
        return []
    except Exception:
        return []


def get_strategy_stats():
    """Fetch strategy statistics"""
    try:
        response = requests.get(f"{API_URL}/strategy_stats?limit=100", timeout=5)
        if response.status_code == 200:
            return response.json().get('strategy_stats', [])
        return []
    except Exception:
        return []


def format_pnl(value):
    """Format P&L with color"""
    if value > 0:
        return f"+${value:.2f}"
    elif value < 0:
        return f"-${abs(value):.2f}"
    else:
        return f"${value:.2f}"


def display_dashboard():
    """Display live monitoring dashboard"""
    while True:
        clear_screen()

        print("=" * 100)
        print("🤖 KAEL AUTONOMOUS PARALLEL TRADING BOT - LIVE MONITOR")
        print("=" * 100)
        print(f"⏰ Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)

        # Get statistics
        stats = get_statistics()

        if stats and 'error' not in stats:
            # Portfolio Overview
            print("\n📊 PORTFOLIO OVERVIEW")
            print("-" * 100)
            print(f"Status:            {stats.get('status', 'Unknown').upper()}")
            print(f"Mode:              {stats.get('mode', 'Unknown').upper()}")
            print(f"Balance:           ${stats.get('balance', 0):.2f}")
            print(f"Start Balance:     ${stats.get('start_balance', 0):.2f}")

            # Fictitious balance mode
            if stats.get('fictitious_balance_mode'):
                print(f"\n💰 FICTITIOUS BALANCE MODE (Testing)")
                print(f"Testing Balance:   ${stats.get('fictitious_balance', 0):.2f}")
                print(f"Testing P&L:       {format_pnl(stats.get('fictitious_pnl', 0))}")
                print(f"Testing ROI:       {stats.get('fictitious_pnl_percent', 0):.2f}%")
                print(f"Real Balance:      ${stats.get('real_balance', 0):.2f}")

            # Daily Performance
            print(f"\n📈 TODAY'S PERFORMANCE")
            print("-" * 100)
            daily_profit = stats.get('daily_profit', 0)
            daily_loss = stats.get('daily_loss', 0)
            daily_net = stats.get('daily_net', 0)
            print(f"Trades:            {stats.get('trades_today', 0)}")
            print(f"Wins:              {stats.get('wins_today', 0)}")
            print(f"Losses:            {stats.get('losses_today', 0)}")
            print(f"Win Rate:          {stats.get('win_rate', 0):.2f}%")
            print(f"Gross Profit:      {format_pnl(daily_profit)}")
            print(f"Gross Loss:        {format_pnl(-daily_loss)}")
            print(f"Net P&L:           {format_pnl(daily_net)}")

            # Active Trading
            print(f"\n🔥 ACTIVE TRADING")
            print("-" * 100)
            print(f"Active Instruments: {stats.get('active_count', 0)}/{stats.get('instruments_traded', 0)}")
            active_instruments = stats.get('active_instruments', [])
            if active_instruments:
                print(f"Trading:           {', '.join(active_instruments)}")
            print(f"Risk Allocated:    ${stats.get('total_risk_allocated', 0):.2f}")

            # Performance Metrics
            print(f"\n⚡ PERFORMANCE METRICS")
            print("-" * 100)
            print(f"Avg Scan Time:     {stats.get('avg_scan_time_ms', 0):.0f}ms")
            print(f"Avg Execution:     {stats.get('avg_execution_time_ms', 0):.0f}ms")
            print(f"Total Trades:      {stats.get('total_trades_all_time', 0)}")
            print(f"Reconnects:        {stats.get('reconnect_count', 0)}")
            if stats.get('uptime_hours'):
                print(f"Uptime:            {stats.get('uptime_hours', 0):.2f} hours")

            # Top Performing Instruments
            instrument_stats = stats.get('instrument_stats', [])
            if instrument_stats:
                print(f"\n🏆 TOP PERFORMING INSTRUMENTS")
                print("-" * 100)
                print(f"{'Instrument':<12} {'Trades':<8} {'Win Rate':<10} {'Profit':<12} {'Sharpe':<8} {'Kelly':<8}")
                print("-" * 100)
                for inst in instrument_stats[:5]:
                    print(f"{inst['instrument']:<12} "
                          f"{inst['total_trades']:<8} "
                          f"{inst['win_rate']:.1f}%{'':<5} "
                          f"{format_pnl(inst['profit']):<12} "
                          f"{inst.get('sharpe_ratio', 0):.2f}{'':<5} "
                          f"{inst.get('kelly_fraction', 0):.3f}")

            # Recent Trades
            recent_trades = get_recent_trades(5)
            if recent_trades:
                print(f"\n📋 RECENT TRADES (Last 5)")
                print("-" * 100)
                print(f"{'Time':<20} {'Instrument':<12} {'Dir':<6} {'Amount':<8} {'Result':<8} {'P&L':<10}")
                print("-" * 100)
                for trade in recent_trades:
                    try:
                        entry_time = datetime.fromisoformat(trade['entry_time'].replace('Z', '+00:00'))
                        time_str = entry_time.strftime('%H:%M:%S')
                    except:
                        time_str = trade.get('entry_time', '')[:19]

                    print(f"{time_str:<20} "
                          f"{trade.get('instrument', 'N/A'):<12} "
                          f"{trade.get('direction', 'N/A'):<6} "
                          f"${trade.get('amount', 0):<7.2f} "
                          f"{trade.get('result', 'N/A'):<8} "
                          f"{format_pnl(trade.get('profit', 0)):<10}")

            # Strategy Performance
            strategy_stats = get_strategy_stats()
            if strategy_stats:
                print(f"\n🎯 STRATEGY PERFORMANCE")
                print("-" * 100)
                print(f"{'Strategy':<30} {'Trades':<8} {'Wins':<8} {'Win Rate':<10} {'Avg P&L':<12}")
                print("-" * 100)
                for strat in strategy_stats[:5]:
                    win_rate = (strat['wins'] / strat['trades'] * 100) if strat['trades'] > 0 else 0
                    print(f"{strat['strategy']:<30} "
                          f"{strat['trades']:<8} "
                          f"{strat['wins']:<8} "
                          f"{win_rate:.1f}%{'':<5} "
                          f"{format_pnl(strat['avg_profit']):<12}")

        else:
            print("\n❌ ERROR: Unable to connect to trading bot")
            print(f"   {stats.get('error', 'Unknown error')}")
            print("\n💡 Make sure the bot is running:")
            print("   docker-compose -f docker-compose.parallel.yml up -d")

        print("\n" + "=" * 100)
        print(f"🔄 Auto-refresh in {REFRESH_INTERVAL}s | Press Ctrl+C to exit")
        print("=" * 100)

        try:
            time.sleep(REFRESH_INTERVAL)
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped. Bot continues running in background.")
            sys.exit(0)


if __name__ == "__main__":
    print("🚀 Starting live monitoring...")
    print("📡 Connecting to bot API...")
    time.sleep(2)

    try:
        display_dashboard()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
