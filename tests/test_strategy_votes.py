import os
import tempfile
from database.db_manager import DatabaseManager


def test_strategy_votes_aggregation():
    # Create a temporary DB
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    try:
        db = DatabaseManager(path)

        # Insert a trade (minimal required fields)
        trade = {
            'trade_id': 't1',
            'instrument': 'TEST-USD',
            'direction': 'CALL',
            'amount': 1.0,
            'duration': 60,
            'payout_ratio': 0.8,
            'entry_time': '2025-01-01T00:00:00',
            'expiration_time': '2025-01-01T00:01:00',
            'execution_time_ms': 100,
            'result': 'WIN',
            'profit': 0.8,
            'entry_price': 1.0,
            'exit_price': 1.8,
            'price_change': 0.8,
            'mode': 'demo',
            'balance_before': 100.0,
            'balance_after': 100.8,
            'notes': None,
            'selected_strategy': 'test_strategy',
            'strategy_breakdown': '[]'
        }

        db.insert_trade(trade)

        # Insert strategy votes; two votes for strategy_a (one executed and won), one for strategy_b (voted but not executed)
        db.insert_strategy_vote({
            'trade_id': 't1',
            'strategy_name': 'strategy_a',
            'voted_direction': 'CALL',
            'voted_for_executed': True,
            'trade_result': 'WIN',
            'profit': 0.8
        })

        db.insert_strategy_vote({
            'trade_id': 't1',
            'strategy_name': 'strategy_a_v2',
            'voted_direction': 'CALL',
            'voted_for_executed': True,
            'trade_result': 'WIN',
            'profit': 0.8
        })

        db.insert_strategy_vote({
            'trade_id': 't1',
            'strategy_name': 'strategy_b',
            'voted_direction': 'PUT',
            'voted_for_executed': False,
            'trade_result': 'WIN',
            'profit': 0.8
        })

        stats = db.get_strategy_stats(limit=10)
        # stats should include strategy_a and strategy_a_v2
        names = [s['strategy_name'] for s in stats]
        assert 'strategy_a' in names
        assert 'strategy_a_v2' in names

        # Find stats for strategy_a
        sa = next(s for s in stats if s['strategy_name'] == 'strategy_a')
        assert sa['total_trades'] == 1
        assert sa['wins'] == 1
        assert sa['total_profit'] == 0.8

    finally:
        try:
            os.remove(path)
        except Exception:
            pass
