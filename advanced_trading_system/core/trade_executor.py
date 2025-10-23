"""Trade execution logic"""

import time
from typing import Optional
from ..models.trade import Trade, TradeResult


class TradeExecutor:
    """Executes trades on IQOption platform"""

    def __init__(self, api):
        """
        Initialize trade executor

        Args:
            api: IQOption API instance
        """
        self.api = api

    def check_market_open(self, pair: str) -> bool:
        """
        Check if market is open for trading

        Args:
            pair: Trading pair

        Returns:
            True if market is open
        """
        try:
            open_times = self.api.get_all_open_time()
            if 'binary' in open_times and pair in open_times['binary']:
                return open_times['binary'][pair].get('open', False)
        except Exception as e:
            print(f"[ERROR] Failed to check market status: {e}")

        return False

    def get_payout(self, pair: str) -> Optional[float]:
        """
        Get payout percentage for a pair

        Args:
            pair: Trading pair

        Returns:
            Payout percentage or None
        """
        try:
            return self.api.get_binary_payout(pair)
        except Exception:
            return None

    def execute(self, trade: Trade) -> TradeResult:
        """
        Execute a trade on IQOption

        Args:
            trade: Trade to execute

        Returns:
            TradeResult with success status
        """
        try:
            # Check market is open
            if not self.check_market_open(trade.pair):
                return TradeResult(
                    success=False,
                    error=f'Market {trade.pair} is not open',
                    error_code='MARKET_CLOSED'
                )

            # Get current balance
            old_balance = self.api.get_balance()

            # Get payout
            payout = self.get_payout(trade.pair)

            print(f"[EXECUTE] {trade.action.upper()} {trade.pair} | "
                  f"Amount: ${trade.amount} | Duration: {trade.duration}m | "
                  f"Confidence: {trade.confidence}%")

            if payout:
                potential_profit = trade.amount * payout
                print(f"[PAYOUT] {payout:.2%} | Potential: ${potential_profit:.2f}")

            # Execute trade
            status, order_id = self.api.buy(
                trade.amount,
                trade.pair,
                trade.action,
                trade.duration
            )

            if not status or order_id is None:
                return TradeResult(
                    success=False,
                    trade=trade,
                    error='Trade execution failed',
                    error_code='EXECUTION_FAILED'
                )

            print(f"[PLACED] Order ID: {order_id}")

            # Update trade with execution details
            trade.execute(order_id, old_balance, payout or 0.0)

            return TradeResult(success=True, trade=trade)

        except Exception as e:
            print(f"[ERROR] Trade execution failed: {e}")
            return TradeResult(
                success=False,
                trade=trade,
                error=str(e),
                error_code='EXCEPTION'
            )

    def wait_for_result(self, trade: Trade, max_attempts: int = 20) -> TradeResult:
        """
        Wait for trade result

        Args:
            trade: Trade to check
            max_attempts: Maximum check attempts

        Returns:
            TradeResult with final status
        """
        if not trade.order_id:
            return TradeResult(
                success=False,
                trade=trade,
                error='No order ID to check',
                error_code='NO_ORDER_ID'
            )

        # Wait for trade duration
        wait_time = trade.duration * 60 + 5
        print(f"[WAITING] {wait_time}s for trade to complete...")
        time.sleep(wait_time)

        # Check result with retries
        print(f"[CHECKING] Result...")
        profit = None

        for attempt in range(max_attempts):
            try:
                profit = self.api.check_win_v3(trade.order_id)
                if profit is not None:
                    break
            except Exception as e:
                print(f"[RETRY] Check error: {e}")

            time.sleep(0.5)

        if profit is None:
            return TradeResult(
                success=False,
                trade=trade,
                error='Result not available after multiple attempts',
                error_code='RESULT_UNAVAILABLE'
            )

        # Get new balance
        new_balance = self.api.get_balance()

        # Update trade with result
        trade.complete(profit, new_balance)

        result_str = 'WIN' if trade.is_win else 'LOSS'
        print(f"[RESULT] {result_str} - Profit: ${profit:.2f} | "
              f"Balance: ${trade.old_balance:.2f} -> ${new_balance:.2f}")

        return TradeResult(success=True, trade=trade)
