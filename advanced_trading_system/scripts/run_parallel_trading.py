"""
Parallel Trading System Runner
Executes trades on multiple pairs simultaneously with filtering
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import TradingConfig
from trading.parallel_trading_engine import ParallelTradingEngine


async def main():
    """Main parallel trading execution"""
    print("🚀 PARALLEL BINARY OPTIONS TRADING SYSTEM")
    print("=" * 80)
    
    # Validate configuration
    try:
        TradingConfig.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Initialize parallel trading engine
    engine = ParallelTradingEngine(TradingConfig)
    
    try:
        # Initialize all components
        await engine.initialize()
        
        # Display available pairs
        pairs_summary = engine.provider.get_pairs_summary()
        print(f"\n📊 Available Pairs Summary:")
        print(f"   Total Pairs: {pairs_summary['total_pairs']}")
        print(f"   High Payout (>85%): {pairs_summary['payout_ranges']['high']}")
        print(f"   Medium Payout (75-85%): {pairs_summary['payout_ranges']['medium']}")
        print(f"   Low Payout (<75%): {pairs_summary['payout_ranges']['low']}")
        
        print(f"\n🏆 Top 5 Payout Pairs:")
        for pair_info in pairs_summary['top_payouts'][:5]:
            print(f"   • {pair_info['pair']}: {pair_info['payout']:.1%} ({pair_info['category']})")
        
        # Run parallel trading session
        session_results = await engine.run_parallel_trading_session(duration_minutes=60)
        
        print(f"\n✅ Parallel trading session completed!")
        print(f"📁 Database: {TradingConfig.DB_PATH}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Session interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Cleanup
        await engine.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
