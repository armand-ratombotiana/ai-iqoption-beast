#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize AI Data Collection Database Schema

This script initializes all the tables required for AI model training:
- trades_ai: Enhanced trade tracking with ML features
- market_snapshots: Time-series market data
- strategy_performance: Strategy metrics tracking
- session_analytics: Session-level aggregations
- weekly_analysis: Automated weekly reports

Usage:
    python scripts/initialize_ai_database.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from database.ai_data_collector import AIDataCollector


def main():
    """Initialize AI database schema"""
    print("="*80)
    print("🤖 AI DATA COLLECTION - DATABASE INITIALIZATION")
    print("="*80)

    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("   Please set it in your .env file or environment")
        return False

    db_host = database_url.split('@')[1] if '@' in database_url else 'local'
    print(f"📊 Database: {db_host}")

    try:
        # Initialize AI Data Collector (this creates all tables)
        print("\n🔧 Initializing schema...")
        collector = AIDataCollector(database_url)

        print("\n✅ Schema initialization complete!")
        print("\nCreated tables:")
        print("  1. trades_ai           - Enhanced trade tracking (40+ fields)")
        print("  2. market_snapshots    - Time-series market data (25+ fields)")
        print("  3. strategy_performance - Strategy metrics tracking (20+ fields)")
        print("  4. session_analytics   - Session-level data (10+ fields)")
        print("  5. weekly_analysis     - Automated weekly reports (15+ fields)")

        print("\n📈 Indexes created:")
        print("  - trades_ai: 5 indexes (time, strategy, instrument, result, condition)")
        print("  - market_snapshots: 2 indexes (time, instrument)")
        print("  - strategy_performance: 2 indexes (time, strategy)")

        print("\n✅ Database ready for AI data collection!")

        # Validate data integrity
        print("\n🔍 Running initial data integrity check...")
        validation = collector.validate_data_integrity()

        if validation.get('error'):
            print(f"⚠️  Validation error: {validation['error']}")
        else:
            print(f"   Health Score: {validation['health_score'] * 100:.1f}%")
            print(f"   Duplicates: {validation['duplicates']}")
            print(f"   Missing Exit Data: {validation['missing_exit_data']}")
            print(f"   Missing Result Data: {validation['missing_result_data']}")
            print(f"   Invalid Values: {validation['invalid_values']}")

        # Close connection
        collector.close()

        print("\n" + "="*80)
        print("🎉 AI Data Collection System Ready!")
        print("="*80)

        return True

    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
