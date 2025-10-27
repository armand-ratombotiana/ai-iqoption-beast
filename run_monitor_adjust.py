#!/usr/bin/env python3
"""
🔄 KAEL Trading Bot - Run, Monitor, and Adjust Workflow
Automated monitoring and adjustment based on performance
"""

import subprocess
import requests
import time
import json
from datetime import datetime
import sys
import os

API_URL = "http://localhost:5001"
MONITORING_DURATION = 300  # 5 minutes per cycle


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 100)
    print(f"🤖 {title}")
    print("=" * 100)


def check_docker():
    """Check if Docker is running"""
    print_header("CHECKING DOCKER")
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker Desktop is running")
            return True
        else:
            print("❌ Docker Desktop is not running")
            print("\n🔧 ACTION REQUIRED:")
            print("   1. Open Docker Desktop")
            print("   2. Wait for it to fully start (green icon)")
            print("   3. Run this script again")
            return False
    except Exception as e:
        print(f"❌ Docker check failed: {e}")
        return False


def stop_containers():
    """Stop existing containers"""
    print_header("STOPPING EXISTING CONTAINERS")
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.parallel.yml', 'down'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ Containers stopped")
        else:
            print("⚠️ No containers to stop or error occurred")
        return True
    except Exception as e:
        print(f"⚠️ Error stopping containers: {e}")
        return True


def build_containers():
    """Build Docker containers"""
    print_header("BUILDING DOCKER IMAGES")
    print("⏳ Building... (this may take 2-5 minutes)")
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.parallel.yml', 'build'],
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            print("✅ Docker images built successfully")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False


def start_containers():
    """Start Docker containers"""
    print_header("STARTING CONTAINERS")
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.parallel.yml', 'up', '-d'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ Containers started")
            print("\n⏳ Waiting 30 seconds for initialization...")
            time.sleep(30)
            return True
        else:
            print(f"❌ Start failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Start error: {e}")
        return False


def check_health():
    """Check bot health"""
    print_header("CHECKING BOT HEALTH")
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bot is healthy")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   API Connected: {data.get('api_connected', False)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to bot: {e}")
        print("\n💡 Checking container logs...")
        show_recent_logs()
        return False


def show_recent_logs():
    """Show recent container logs"""
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.parallel.yml', 'logs', '--tail=50', 'parallel-trading-bot'],
            capture_output=True,
            text=True,
            timeout=10
        )
        print("\n📋 RECENT LOGS:")
        print("-" * 100)
        print(result.stdout)
    except Exception as e:
        print(f"⚠️ Could not fetch logs: {e}")


def get_statistics():
    """Get bot statistics"""
    try:
        response = requests.get(f"{API_URL}/statistics", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def monitor_cycle(duration=300):
    """Monitor bot for specified duration"""
    print_header(f"MONITORING FOR {duration//60} MINUTES")

    start_time = time.time()
    end_time = start_time + duration

    initial_stats = get_statistics()
    if not initial_stats:
        print("❌ Cannot get statistics")
        return None

    print(f"\n📊 INITIAL STATE:")
    print(f"   Balance: ${initial_stats.get('balance', 0):.2f}")
    print(f"   Mode: {initial_stats.get('mode', 'unknown').upper()}")
    print(f"   Trades Today: {initial_stats.get('trades_today', 0)}")
    print(f"   Win Rate: {initial_stats.get('win_rate', 0):.1f}%")

    # Collect metrics during monitoring
    metrics = {
        'trades_executed': 0,
        'wins': 0,
        'losses': 0,
        'total_profit': 0,
        'errors': 0,
        'avg_execution_time': [],
        'instruments_traded': set()
    }

    last_trade_count = initial_stats.get('trades_today', 0)

    while time.time() < end_time:
        remaining = int(end_time - time.time())

        # Get current stats
        stats = get_statistics()
        if stats:
            current_trades = stats.get('trades_today', 0)
            new_trades = current_trades - last_trade_count

            if new_trades > 0:
                metrics['trades_executed'] += new_trades
                metrics['wins'] = stats.get('wins_today', 0)
                metrics['losses'] = stats.get('losses_today', 0)
                last_trade_count = current_trades

                print(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] NEW TRADE! Total today: {current_trades}")
                print(f"   Win Rate: {stats.get('win_rate', 0):.1f}% | "
                      f"P&L: ${stats.get('daily_net', 0):.2f} | "
                      f"Active: {stats.get('active_count', 0)}")

        # Progress indicator
        print(f"\r⏳ Monitoring... {remaining}s remaining | "
              f"Trades: {metrics['trades_executed']} | "
              f"Wins: {metrics['wins']} | Losses: {metrics['losses']}", end='', flush=True)

        time.sleep(10)  # Check every 10 seconds

    print("\n")

    # Get final stats
    final_stats = get_statistics()
    if final_stats:
        metrics['final_balance'] = final_stats.get('balance', 0)
        metrics['final_win_rate'] = final_stats.get('win_rate', 0)
        metrics['final_daily_net'] = final_stats.get('daily_net', 0)
        metrics['active_instruments'] = final_stats.get('active_instruments', [])

    return metrics


def analyze_performance(metrics):
    """Analyze performance and suggest adjustments"""
    print_header("PERFORMANCE ANALYSIS")

    if not metrics:
        print("❌ No metrics available")
        return None

    print(f"\n📊 MONITORING RESULTS:")
    print(f"   Trades Executed: {metrics['trades_executed']}")
    print(f"   Wins: {metrics['wins']}")
    print(f"   Losses: {metrics['losses']}")
    print(f"   Final Win Rate: {metrics.get('final_win_rate', 0):.1f}%")
    print(f"   Final P&L: ${metrics.get('final_daily_net', 0):.2f}")

    # Analysis and recommendations
    recommendations = []

    if metrics['trades_executed'] == 0:
        print("\n⚠️ NO TRADES EXECUTED")
        recommendations.append({
            'issue': 'No trades',
            'action': 'Lower MIN_AI_CONFIDENCE from 60 to 50',
            'env_var': 'MIN_AI_CONFIDENCE',
            'new_value': '50'
        })
        recommendations.append({
            'issue': 'No trades',
            'action': 'Increase MAX_CONCURRENT_INSTRUMENTS to 5',
            'env_var': 'MAX_CONCURRENT_INSTRUMENTS',
            'new_value': '5'
        })

    elif metrics['trades_executed'] < 5:
        print("\n⚠️ LOW TRADING ACTIVITY")
        recommendations.append({
            'issue': 'Low activity',
            'action': 'Lower MIN_AI_CONFIDENCE to 55',
            'env_var': 'MIN_AI_CONFIDENCE',
            'new_value': '55'
        })

    if metrics['wins'] > 0:
        win_rate = (metrics['wins'] / (metrics['wins'] + metrics['losses'])) * 100 if (metrics['wins'] + metrics['losses']) > 0 else 0

        if win_rate < 50:
            print("\n⚠️ LOW WIN RATE")
            recommendations.append({
                'issue': f'Win rate too low ({win_rate:.1f}%)',
                'action': 'Increase MIN_AI_CONFIDENCE to 70',
                'env_var': 'MIN_AI_CONFIDENCE',
                'new_value': '70'
            })
        elif win_rate > 70:
            print("\n✅ EXCELLENT WIN RATE")
            print("   Consider being more aggressive")
            recommendations.append({
                'issue': f'Win rate very high ({win_rate:.1f}%)',
                'action': 'Increase MAX_TRADE_AMOUNT to 2.0',
                'env_var': 'MAX_TRADE_AMOUNT',
                'new_value': '2.0'
            })

    if metrics.get('final_daily_net', 0) < -10:
        print("\n⚠️ SIGNIFICANT LOSSES")
        recommendations.append({
            'issue': 'Daily loss exceeds -$10',
            'action': 'Increase MIN_AI_CONFIDENCE to 70',
            'env_var': 'MIN_AI_CONFIDENCE',
            'new_value': '70'
        })
        recommendations.append({
            'issue': 'Daily loss exceeds -$10',
            'action': 'Reduce MAX_TRADE_AMOUNT to 0.5',
            'env_var': 'MAX_TRADE_AMOUNT',
            'new_value': '0.5'
        })

    return recommendations


def apply_adjustments(recommendations):
    """Apply recommended adjustments to .env file"""
    if not recommendations:
        print("\n✅ No adjustments needed")
        return False

    print_header("RECOMMENDED ADJUSTMENTS")

    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['issue']}")
        print(f"   Action: {rec['action']}")
        print(f"   Change: {rec['env_var']}={rec['new_value']}")

    response = input("\n❓ Apply these adjustments? (y/n): ").lower().strip()

    if response == 'y':
        print("\n🔧 Applying adjustments to .env file...")

        # Read current .env
        env_file = '.env'
        with open(env_file, 'r') as f:
            lines = f.readlines()

        # Apply changes
        for rec in recommendations:
            var_name = rec['env_var']
            new_value = rec['new_value']

            found = False
            for i, line in enumerate(lines):
                if line.startswith(f"{var_name}="):
                    lines[i] = f"{var_name}={new_value}\n"
                    found = True
                    print(f"   ✅ Updated {var_name}={new_value}")
                    break

            if not found:
                lines.append(f"\n{var_name}={new_value}\n")
                print(f"   ✅ Added {var_name}={new_value}")

        # Write back
        with open(env_file, 'w') as f:
            f.writelines(lines)

        print("\n✅ Adjustments applied!")
        return True
    else:
        print("\n⏭️ Skipping adjustments")
        return False


def restart_containers():
    """Restart containers"""
    print_header("RESTARTING CONTAINERS")

    # Stop
    print("⏳ Stopping containers...")
    subprocess.run(['docker-compose', '-f', 'docker-compose.parallel.yml', 'down'],
                   capture_output=True, timeout=60)

    # Start
    print("⏳ Starting containers...")
    result = subprocess.run(
        ['docker-compose', '-f', 'docker-compose.parallel.yml', 'up', '-d'],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode == 0:
        print("✅ Containers restarted")
        print("⏳ Waiting 30 seconds for initialization...")
        time.sleep(30)
        return True
    else:
        print(f"❌ Restart failed: {result.stderr}")
        return False


def main():
    """Main workflow"""
    print_header("KAEL TRADING BOT - RUN, MONITOR, ADJUST WORKFLOW")

    # Check Docker
    if not check_docker():
        sys.exit(1)

    # Stop existing containers
    stop_containers()

    # Build
    if not build_containers():
        sys.exit(1)

    # Start
    if not start_containers():
        sys.exit(1)

    # Check health
    if not check_health():
        print("\n⚠️ Bot health check failed, but continuing to monitor...")

    # Initial monitoring cycle
    cycle = 1
    while True:
        print_header(f"MONITORING CYCLE #{cycle}")

        # Monitor
        metrics = monitor_cycle(MONITORING_DURATION)

        # Analyze
        recommendations = analyze_performance(metrics)

        # Ask to continue or adjust
        if recommendations:
            if apply_adjustments(recommendations):
                # Restart with new settings
                if restart_containers():
                    if not check_health():
                        print("⚠️ Health check failed after restart")
                cycle += 1
                continue

        # Ask if user wants to continue monitoring
        print("\n" + "=" * 100)
        response = input("❓ Continue monitoring? (y/n/adjust): ").lower().strip()

        if response == 'n':
            print("\n✅ Monitoring complete. Bot continues running.")
            print("\n💡 Useful commands:")
            print("   View logs:  docker-compose -f docker-compose.parallel.yml logs -f")
            print("   Statistics: curl http://localhost:5001/statistics")
            print("   Stop bot:   docker-compose -f docker-compose.parallel.yml down")
            break
        elif response == 'adjust':
            # Manual adjustment
            print("\n🔧 Manual adjustment mode")
            print("Edit .env file manually, then I'll restart the bot")
            input("Press Enter when ready to restart...")
            if restart_containers():
                check_health()

        cycle += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted. Bot continues running in background.")
        print("   Stop with: docker-compose -f docker-compose.parallel.yml down")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
