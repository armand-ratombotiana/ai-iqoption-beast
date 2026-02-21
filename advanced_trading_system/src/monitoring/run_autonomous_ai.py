#!/usr/bin/env python3
"""
Autonomous AI Trading System - Runner and Monitor
Complete system for running and monitoring autonomous AI trading

Usage:
    python run_autonomous_ai.py --mode demo --autonomy-level semi_autonomous
    python run_autonomous_ai.py --mode demo --autonomy-level supervised --monitor
    python run_autonomous_ai.py --mode live --autonomy-level fully_autonomous --confirm
"""
import os
import sys
import asyncio
import argparse
import logging
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Setup logging
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

log_file = f'logs/autonomous_ai_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global shutdown flag
SHUTDOWN_FLAG = False


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global SHUTDOWN_FLAG
    SHUTDOWN_FLAG = True
    print("\n⚠️  Shutdown signal received. Stopping gracefully...")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class AutonomousAIRunner:
    """
    Autonomous AI Trading System Runner
    Manages execution and monitoring
    """
    
    def __init__(self, args):
        self.args = args
        self.autonomous_system = None
        self.start_time = None
        self.stats = {
            'decisions_made': 0,
            'trades_executed': 0,
            'trades_won': 0,
            'trades_lost': 0,
            'total_profit': 0.0,
            'learning_updates': 0,
            'strategy_adaptations': 0,
            'health_checks': 0,
            'errors': 0
        }
    
    async def initialize(self):
        """Initialize autonomous AI system"""
        logger.info("🚀 Initializing Autonomous AI System...")
        
        try:
            # Import autonomous AI components
            from ai.autonomous.core_system import AutonomousAISystem, AutonomousConfig, AutonomyLevel
            
            # Create configuration
            config = AutonomousConfig(
                autonomy_level=AutonomyLevel[self.args.autonomy_level.upper()],
                max_trades_per_hour=self.args.max_trades_per_hour,
                max_daily_trades=self.args.max_daily_trades,
                learning_rate=self.args.learning_rate,
                exploration_rate=self.args.exploration_rate,
                confidence_threshold=self.args.confidence_threshold,
                risk_tolerance=self.args.risk_tolerance,
                enable_self_learning=self.args.enable_learning,
                enable_strategy_adaptation=self.args.enable_adaptation,
                enable_autonomous_risk_management=self.args.enable_risk_management,
                enable_market_regime_detection=self.args.enable_regime_detection,
                emergency_stop_loss=self.args.emergency_stop_loss
            )
            
            # Validate configuration
            config.validate()
            
            # Create autonomous system
            self.autonomous_system = AutonomousAISystem(config)
            
            logger.info("✅ Autonomous AI System initialized successfully")
            return True
            
        except ImportError as e:
            logger.error(f"❌ Failed to import autonomous AI: {e}")
            logger.error("Please ensure all autonomous AI files are in place")
            return False
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def run(self):
        """Run autonomous AI system with monitoring"""
        global SHUTDOWN_FLAG
        
        # Display banner
        self.display_banner()
        
        # Initialize
        if not await self.initialize():
            logger.error("❌ Failed to initialize. Exiting.")
            return
        
        # Safety confirmation for live trading
        if self.args.mode == 'live':
            if not self.confirm_live_trading():
                logger.info("❌ Live trading cancelled by user")
                return
        
        # Start time
        self.start_time = datetime.now()
        
        # Start autonomous system
        logger.info("🚀 Starting Autonomous AI System...")
        
        # Create tasks
        tasks = [
            asyncio.create_task(self.autonomous_system.start()),
            asyncio.create_task(self.monitor_loop()),
            asyncio.create_task(self.status_display_loop())
        ]
        
        try:
            # Run until shutdown
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error in main run: {e}")
        finally:
            # Cleanup
            await self.shutdown()
    
    async def monitor_loop(self):
        """Monitor autonomous AI system"""
        global SHUTDOWN_FLAG
        
        while not SHUTDOWN_FLAG:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Get system status
                status = await self.autonomous_system.get_status()
                
                # Update stats
                self.stats['decisions_made'] = status.get('decisions_made', 0)
                self.stats['health_checks'] += 1
                
                # Check health
                health = status.get('health_status', {})
                if health.get('status') == 'critical':
                    logger.critical("🚨 CRITICAL HEALTH ISSUE DETECTED!")
                    logger.critical(f"Issues: {health.get('issues', [])}")
                    
                    if self.args.auto_stop_on_critical:
                        logger.critical("🛑 Auto-stopping due to critical issue")
                        SHUTDOWN_FLAG = True
                
                # Log metrics
                if self.args.verbose:
                    self.log_metrics(status)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                self.stats['errors'] += 1
                await asyncio.sleep(60)
    
    async def status_display_loop(self):
        """Display status updates"""
        global SHUTDOWN_FLAG
        
        display_interval = self.args.status_interval
        
        while not SHUTDOWN_FLAG:
            try:
                await asyncio.sleep(display_interval)
                
                # Get status
                status = await self.autonomous_system.get_status()
                
                # Display
                self.display_status(status)
                
            except Exception as e:
                logger.error(f"Error in status display: {e}")
                await asyncio.sleep(display_interval)
    
    def display_banner(self):
        """Display startup banner"""
        print("\n" + "="*80)
        print("🤖 AUTONOMOUS AI TRADING SYSTEM")
        print("="*80)
        print(f"\nMode: {self.args.mode.upper()}")
        print(f"Autonomy Level: {self.args.autonomy_level.upper()}")
        print(f"Max Trades/Hour: {self.args.max_trades_per_hour}")
        print(f"Confidence Threshold: {self.args.confidence_threshold * 100:.0f}%")
        print(f"Risk Tolerance: {self.args.risk_tolerance * 100:.0f}%")
        print(f"Emergency Stop Loss: {self.args.emergency_stop_loss * 100:.0f}%")
        
        print(f"\n🎛️  Features:")
        print(f"   Self-Learning: {'✅ Enabled' if self.args.enable_learning else '❌ Disabled'}")
        print(f"   Strategy Adaptation: {'✅ Enabled' if self.args.enable_adaptation else '❌ Disabled'}")
        print(f"   Autonomous Risk: {'✅ Enabled' if self.args.enable_risk_management else '❌ Disabled'}")
        print(f"   Regime Detection: {'✅ Enabled' if self.args.enable_regime_detection else '❌ Disabled'}")
        
        print(f"\n📊 Monitoring:")
        print(f"   Status Updates: Every {self.args.status_interval}s")
        print(f"   Log File: {log_file}")
        print(f"   Verbose Mode: {'✅' if self.args.verbose else '❌'}")
        
        print("\n" + "="*80)
    
    def confirm_live_trading(self) -> bool:
        """Confirm live trading"""
        if not self.args.confirm:
            print("\n❌ ERROR: Live trading requires --confirm flag")
            print("Example: python run_autonomous_ai.py --mode live --confirm")
            return False
        
        print("\n" + "!"*80)
        print("⚠️  WARNING: LIVE TRADING MODE - REAL MONEY AT RISK")
        print("!"*80)
        print("\nYou are about to enable AUTONOMOUS AI trading with REAL MONEY.")
        print("The AI will make trading decisions based on its algorithms.")
        print("\nRisks:")
        print("  • You can lose your entire investment")
        print("  • AI decisions may not always be profitable")
        print("  • Market conditions can change rapidly")
        print("  • Past performance does not guarantee future results")
        
        if self.args.autonomy_level == 'fully_autonomous':
            print("\n⚠️  FULLY AUTONOMOUS MODE:")
            print("  • AI will trade WITHOUT human approval")
            print("  • Trades will execute automatically")
            print("  • You must monitor the system")
        
        print("\nType 'I ACCEPT THE RISKS' to continue:")
        response = input("> ")
        
        if response != 'I ACCEPT THE RISKS':
            print("\n❌ Live trading cancelled")
            return False
        
        print("\n✅ Live trading confirmed")
        return True
    
    def display_status(self, status: Dict):
        """Display current status"""
        uptime = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        print("\n" + "="*80)
        print(f"📊 STATUS UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        print(f"\n⏱️  Uptime: {uptime}")
        print(f"🤖 Running: {'✅ Yes' if status.get('is_running', False) else '❌ No'}")
        print(f"📚 Learning: {'✅ Active' if status.get('is_learning', False) else '❌ Inactive'}")
        print(f"🎯 Autonomy: {status.get('autonomy_level', 'unknown').upper()}")
        
        print(f"\n📈 Performance:")
        print(f"   Decisions Made: {status.get('decisions_made', 0)}")
        print(f"   Trades Executed: {self.stats['trades_executed']}")
        print(f"   Wins: {self.stats['trades_won']}")
        print(f"   Losses: {self.stats['trades_lost']}")
        
        if self.stats['trades_executed'] > 0:
            win_rate = (self.stats['trades_won'] / self.stats['trades_executed']) * 100
            print(f"   Win Rate: {win_rate:.1f}%")
        
        print(f"   Total P&L: ${self.stats['total_profit']:+.2f}")
        
        # Learning metrics
        learning_metrics = status.get('learning_metrics', {})
        if learning_metrics:
            print(f"\n📚 Learning:")
            print(f"   Updates: {self.stats['learning_updates']}")
            print(f"   Success Rate: {learning_metrics.get('success_rate', 0)*100:.1f}%")
        
        # Health status
        health = status.get('health_status', {})
        if health:
            health_emoji = '✅' if health.get('status') == 'healthy' else '⚠️' if health.get('status') == 'warning' else '🚨'
            print(f"\n🏥 Health: {health_emoji} {health.get('status', 'unknown').upper()}")
            
            if health.get('issues'):
                print(f"   Issues: {len(health['issues'])}")
                for issue in health['issues'][:3]:  # Show first 3
                    print(f"      • {issue.get('issue', 'Unknown')}")
        
        print("\n" + "="*80)
    
    def log_metrics(self, status: Dict):
        """Log detailed metrics"""
        logger.info("="*60)
        logger.info("METRICS UPDATE")
        logger.info("="*60)
        logger.info(f"Decisions Made: {status.get('decisions_made', 0)}")
        logger.info(f"Learning Active: {status.get('is_learning', False)}")
        logger.info(f"Health Status: {status.get('health_status', {}).get('status', 'unknown')}")
        logger.info("="*60)
    
    async def shutdown(self):
        """Shutdown autonomous AI system"""
        logger.info("🛑 Shutting down Autonomous AI System...")
        
        if self.autonomous_system:
            try:
                await self.autonomous_system.stop()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
        
        # Generate final report
        self.generate_final_report()
        
        logger.info("✅ Shutdown complete")
    
    def generate_final_report(self):
        """Generate final session report"""
        duration = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        print("\n" + "="*80)
        print("📊 FINAL SESSION REPORT")
        print("="*80)
        
        print(f"\n⏱️  Session Duration: {duration}")
        print(f"📅 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else 'N/A'}")
        print(f"📅 End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📈 Trading Statistics:")
        print(f"   Decisions Made: {self.stats['decisions_made']}")
        print(f"   Trades Executed: {self.stats['trades_executed']}")
        print(f"   Wins: {self.stats['trades_won']}")
        print(f"   Losses: {self.stats['trades_lost']}")
        
        if self.stats['trades_executed'] > 0:
            win_rate = (self.stats['trades_won'] / self.stats['trades_executed']) * 100
            print(f"   Win Rate: {win_rate:.1f}%")
        
        print(f"   Total P&L: ${self.stats['total_profit']:+.2f}")
        
        print(f"\n🤖 AI Activity:")
        print(f"   Learning Updates: {self.stats['learning_updates']}")
        print(f"   Strategy Adaptations: {self.stats['strategy_adaptations']}")
        print(f"   Health Checks: {self.stats['health_checks']}")
        
        print(f"\n⚠️  Errors: {self.stats['errors']}")
        
        print(f"\n📁 Files:")
        print(f"   Log File: {log_file}")
        print(f"   Database: data/autonomous_trades.db")
        print(f"   Models: models/")
        
        print("\n" + "="*80)
        
        # Save report to file
        report = {
            'session_info': {
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': datetime.now().isoformat(),
                'duration_seconds': duration.total_seconds(),
                'mode': self.args.mode,
                'autonomy_level': self.args.autonomy_level
            },
            'statistics': self.stats,
            'configuration': {
                'max_trades_per_hour': self.args.max_trades_per_hour,
                'confidence_threshold': self.args.confidence_threshold,
                'risk_tolerance': self.args.risk_tolerance,
                'emergency_stop_loss': self.args.emergency_stop_loss
            }
        }
        
        report_file = f'data/session_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Session report saved: {report_file}")
        print("="*80)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Autonomous AI Trading System - Runner and Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Demo mode with semi-autonomous AI
  python run_autonomous_ai.py --mode demo --autonomy-level semi_autonomous
  
  # Demo mode with full monitoring
  python run_autonomous_ai.py --mode demo --autonomy-level supervised --verbose
  
  # Live trading (requires confirmation)
  python run_autonomous_ai.py --mode live --autonomy-level semi_autonomous --confirm
  
  # Fully autonomous (advanced users only)
  python run_autonomous_ai.py --mode live --autonomy-level fully_autonomous --confirm
        """
    )
    
    # Core settings
    parser.add_argument(
        '--mode',
        choices=['demo', 'live'],
        default='demo',
        help='Trading mode (default: demo)'
    )
    
    parser.add_argument(
        '--autonomy-level',
        choices=['supervised', 'semi_autonomous', 'fully_autonomous'],
        default='semi_autonomous',
        help='Autonomy level (default: semi_autonomous)'
    )
    
    # Trading limits
    parser.add_argument(
        '--max-trades-per-hour',
        type=int,
        default=10,
        help='Maximum trades per hour (default: 10)'
    )
    
    parser.add_argument(
        '--max-daily-trades',
        type=int,
        default=100,
        help='Maximum trades per day (default: 100)'
    )
    
    # AI parameters
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.001,
        help='Learning rate for RL agent (default: 0.001)'
    )
    
    parser.add_argument(
        '--exploration-rate',
        type=float,
        default=0.1,
        help='Exploration rate for RL agent (default: 0.1)'
    )
    
    # Risk settings
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.75,
        help='Minimum confidence threshold (default: 0.75)'
    )
    
    parser.add_argument(
        '--risk-tolerance',
        type=float,
        default=0.02,
        help='Risk tolerance per trade (default: 0.02 = 2%%)'
    )
    
    parser.add_argument(
        '--emergency-stop-loss',
        type=float,
        default=0.10,
        help='Emergency stop loss (default: 0.10 = 10%%)'
    )
    
    # Feature flags
    parser.add_argument(
        '--enable-learning',
        action='store_true',
        default=True,
        help='Enable self-learning (default: enabled)'
    )
    
    parser.add_argument(
        '--disable-learning',
        action='store_true',
        help='Disable self-learning'
    )
    
    parser.add_argument(
        '--enable-adaptation',
        action='store_true',
        default=True,
        help='Enable strategy adaptation (default: enabled)'
    )
    
    parser.add_argument(
        '--disable-adaptation',
        action='store_true',
        help='Disable strategy adaptation'
    )
    
    parser.add_argument(
        '--enable-risk-management',
        action='store_true',
        default=True,
        help='Enable autonomous risk management (default: enabled)'
    )
    
    parser.add_argument(
        '--disable-risk-management',
        action='store_true',
        help='Disable autonomous risk management'
    )
    
    parser.add_argument(
        '--enable-regime-detection',
        action='store_true',
        default=True,
        help='Enable market regime detection (default: enabled)'
    )
    
    parser.add_argument(
        '--disable-regime-detection',
        action='store_true',
        help='Disable market regime detection'
    )
    
    # Monitoring options
    parser.add_argument(
        '--status-interval',
        type=int,
        default=300,
        help='Status display interval in seconds (default: 300 = 5 min)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--auto-stop-on-critical',
        action='store_true',
        help='Automatically stop on critical health issues'
    )
    
    # Safety
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirm live trading (required for live mode)'
    )
    
    args = parser.parse_args()
    
    # Handle disable flags
    if args.disable_learning:
        args.enable_learning = False
    if args.disable_adaptation:
        args.enable_adaptation = False
    if args.disable_risk_management:
        args.enable_risk_management = False
    if args.disable_regime_detection:
        args.enable_regime_detection = False
    
    # Validate arguments
    if not 0 < args.confidence_threshold <= 1:
        print("❌ Error: confidence-threshold must be between 0 and 1")
        sys.exit(1)
    
    if not 0 < args.risk_tolerance <= 1:
        print("❌ Error: risk-tolerance must be between 0 and 1")
        sys.exit(1)
    
    if not 0 < args.emergency_stop_loss <= 1:
        print("❌ Error: emergency-stop-loss must be between 0 and 1")
        sys.exit(1)
    
    # Create and run
    runner = AutonomousAIRunner(args)
    
    try:
        await runner.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())