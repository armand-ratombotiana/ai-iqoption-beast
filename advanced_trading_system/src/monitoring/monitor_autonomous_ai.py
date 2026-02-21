#!/usr/bin/env python3
"""
Autonomous AI Monitoring Dashboard
Real-time monitoring and control interface
"""
import os
import sys
import asyncio
import curses
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))


class AutonomousAIMonitor:
    """
    Real-time monitoring dashboard for autonomous AI
    
    Features:
    - Live status updates
    - Performance metrics
    - Health monitoring
    - Decision history
    - Interactive controls
    """
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        self.status_data = {}
        self.refresh_interval = 2  # seconds
        
        # Initialize curses
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(1)  # Non-blocking input
        
        # Colors
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    
    async def run(self):
        """Run monitoring dashboard"""
        while self.running:
            try:
                # Clear screen
                self.stdscr.clear()
                
                # Get status
                await self.update_status()
                
                # Draw dashboard
                self.draw_dashboard()
                
                # Handle input
                self.handle_input()
                
                # Refresh
                self.stdscr.refresh()
                
                # Wait
                await asyncio.sleep(self.refresh_interval)
                
            except Exception as e:
                self.draw_error(str(e))
                await asyncio.sleep(5)
    
    async def update_status(self):
        """Update status data"""
        try:
            # Read status from file (written by autonomous AI)
            status_file = 'data/autonomous_status.json'
            if Path(status_file).exists():
                with open(status_file, 'r') as f:
                    self.status_data = json.load(f)
            else:
                self.status_data = self.get_default_status()
                
        except Exception as e:
            self.status_data = self.get_default_status()
    
    def get_default_status(self) -> Dict:
        """Get default status"""
        return {
            'is_running': False,
            'autonomy_level': 'unknown',
            'decisions_made': 0,
            'is_learning': False,
            'health_status': {'status': 'unknown'},
            'current_performance': {},
            'learning_metrics': {}
        }
    
    def draw_dashboard(self):
        """Draw monitoring dashboard"""
        height, width = self.stdscr.getmaxyx()
        
        # Header
        self.draw_header(width)
        
        # System Status
        self.draw_system_status(3, width)
        
        # Performance Metrics
        self.draw_performance(10, width)
        
        # Health Status
        self.draw_health(17, width)
        
        # Recent Decisions
        self.draw_decisions(24, width)
        
        # Controls
        self.draw_controls(height - 3, width)
    
    def draw_header(self, width):
        """Draw header"""
        title = "🤖 AUTONOMOUS AI MONITORING DASHBOARD"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(4))
        self.stdscr.addstr(1, (width - len(timestamp)) // 2, timestamp, curses.color_pair(4))
    
    def draw_system_status(self, start_row, width):
        """Draw system status section"""
        self.stdscr.addstr(start_row, 2, "="*76, curses.color_pair(4))
        self.stdscr.addstr(start_row + 1, 2, "SYSTEM STATUS", curses.A_BOLD)
        self.stdscr.addstr(start_row + 2, 2, "="*76, curses.color_pair(4))
        
        is_running = self.status_data.get('is_running', False)
        autonomy = self.status_data.get('autonomy_level', 'unknown').upper()
        is_learning = self.status_data.get('is_learning', False)
        
        # Running status
        status_color = curses.color_pair(1) if is_running else curses.color_pair(2)
        status_text = "✅ RUNNING" if is_running else "❌ STOPPED"
        self.stdscr.addstr(start_row + 4, 4, f"Status: {status_text}", status_color | curses.A_BOLD)
        
        # Autonomy level
        self.stdscr.addstr(start_row + 5, 4, f"Autonomy: {autonomy}", curses.color_pair(4))
        
        # Learning status
        learning_color = curses.color_pair(1) if is_learning else curses.color_pair(3)
        learning_text = "✅ ACTIVE" if is_learning else "⚠️  INACTIVE"
        self.stdscr.addstr(start_row + 6, 4, f"Learning: {learning_text}", learning_color)
    
    def draw_performance(self, start_row, width):
        """Draw performance metrics"""
        self.stdscr.addstr(start_row, 2, "="*76, curses.color_pair(4))
        self.stdscr.addstr(start_row + 1, 2, "PERFORMANCE METRICS", curses.A_BOLD)
        self.stdscr.addstr(start_row + 2, 2, "="*76, curses.color_pair(4))
        
        decisions = self.status_data.get('decisions_made', 0)
        
        perf = self.status_data.get('current_performance', {})
        trades = perf.get('total_trades', 0)
        wins = perf.get('wins', 0)
        losses = perf.get('losses', 0)
        total_pnl = perf.get('total_pnl', 0.0)
        
        self.stdscr.addstr(start_row + 4, 4, f"Decisions Made: {decisions}", curses.color_pair(4))
        self.stdscr.addstr(start_row + 5, 4, f"Trades Executed: {trades}", curses.color_pair(4))
        
        if trades > 0:
            win_rate = (wins / trades) * 100
            win_color = curses.color_pair(1) if win_rate >= 50 else curses.color_pair(2)
            self.stdscr.addstr(start_row + 5, 40, f"Win Rate: {win_rate:.1f}%", win_color)
        
        pnl_color = curses.color_pair(1) if total_pnl >= 0 else curses.color_pair(2)
        self.stdscr.addstr(start_row + 6, 4, f"Total P&L: ${total_pnl:+.2f}", pnl_color | curses.A_BOLD)
    
    def draw_health(self, start_row, width):
        """Draw health status"""
        self.stdscr.addstr(start_row, 2, "="*76, curses.color_pair(4))
        self.stdscr.addstr(start_row + 1, 2, "HEALTH STATUS", curses.A_BOLD)
        self.stdscr.addstr(start_row + 2, 2, "="*76, curses.color_pair(4))
        
        health = self.status_data.get('health_status', {})
        status = health.get('status', 'unknown')
        
        # Health status
        if status == 'healthy':
            health_color = curses.color_pair(1)
            health_text = "✅ HEALTHY"
        elif status == 'warning':
            health_color = curses.color_pair(3)
            health_text = "⚠️  WARNING"
        elif status == 'critical':
            health_color = curses.color_pair(2)
            health_text = "🚨 CRITICAL"
        else:
            health_color = curses.color_pair(3)
            health_text = "❓ UNKNOWN"
        
        self.stdscr.addstr(start_row + 4, 4, f"Status: {health_text}", health_color | curses.A_BOLD)
        
        # Issues
        issues = health.get('issues', [])
        if issues:
            self.stdscr.addstr(start_row + 5, 4, f"Issues: {len(issues)}", curses.color_pair(3))
            for i, issue in enumerate(issues[:2]):  # Show first 2
                issue_text = issue.get('issue', 'Unknown')[:60]
                self.stdscr.addstr(start_row + 6 + i, 6, f"• {issue_text}", curses.color_pair(3))
    
    def draw_decisions(self, start_row, width):
        """Draw recent decisions"""
        self.stdscr.addstr(start_row, 2, "="*76, curses.color_pair(4))
        self.stdscr.addstr(start_row + 1, 2, "RECENT ACTIVITY", curses.A_BOLD)
        self.stdscr.addstr(start_row + 2, 2, "="*76, curses.color_pair(4))
        
        # Read recent decisions from log
        try:
            log_files = sorted(Path('logs').glob('autonomous_ai_*.log'), reverse=True)
            if log_files:
                with open(log_files[0], 'r') as f:
                    lines = f.readlines()[-5:]  # Last 5 lines
                    for i, line in enumerate(lines):
                        if len(line) > 75:
                            line = line[:75] + "..."
                        self.stdscr.addstr(start_row + 4 + i, 4, line.strip()[:74])
        except:
            self.stdscr.addstr(start_row + 4, 4, "No recent activity", curses.color_pair(3))
    
    def draw_controls(self, start_row, width):
        """Draw control instructions"""
        controls = "Controls: [Q]uit | [R]efresh | [P]ause | [S]tatus | [H]elp"
        self.stdscr.addstr(start_row, (width - len(controls)) // 2, controls, curses.color_pair(5))
    
    def draw_error(self, error_msg: str):
        """Draw error message"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        error_text = f"❌ Error: {error_msg}"
        self.stdscr.addstr(height // 2, (width - len(error_text)) // 2, error_text, curses.color_pair(2))
        self.stdscr.refresh()
    
    def handle_input(self):
        """Handle keyboard input"""
        try:
            key = self.stdscr.getch()
            
            if key == ord('q') or key == ord('Q'):
                self.running = False
            elif key == ord('r') or key == ord('R'):
                # Force refresh
                pass
            elif key == ord('p') or key == ord('P'):
                # Pause/resume
                pass
            elif key == ord('h') or key == ord('H'):
                self.show_help()
                
        except:
            pass
    
    def show_help(self):
        """Show help screen"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        help_text = [
            "AUTONOMOUS AI MONITORING - HELP",
            "",
            "Keyboard Controls:",
            "  Q - Quit monitoring",
            "  R - Force refresh",
            "  P - Pause/Resume updates",
            "  H - Show this help",
            "",
            "Press any key to return..."
        ]
        
        start_row = (height - len(help_text)) // 2
        for i, line in enumerate(help_text):
            self.stdscr.addstr(start_row + i, (width - len(line)) // 2, line)
        
        self.stdscr.refresh()
        self.stdscr.getch()


def run_monitor(stdscr):
    """Run monitoring dashboard"""
    monitor = AutonomousAIMonitor(stdscr)
    asyncio.run(monitor.run())


def main():
    """Main entry point"""
    print("🚀 Starting Autonomous AI Monitor...")
    print("Press Ctrl+C to exit")
    
    try:
        curses.wrapper(run_monitor)
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()