#!/usr/bin/env python3
"""
Logging Configuration for Paper Trading System

Features:
- Rotating log files (daily rotation)
- Different log levels for trading and analysis
- Structured logging with timestamps
- Trade history logging
- Error logging with full stack traces
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


class LoggingConfig:
    """Centralized logging configuration"""

    def __init__(self, log_dir: str = "logs"):
        """Initialize logging configuration"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Log files
        self.trading_log = self.log_dir / "trading.log"
        self.analysis_log = self.log_dir / "analysis.log"
        self.error_log = self.log_dir / "errors.log"
        self.alert_log = self.log_dir / "alerts.log"
        self.metrics_log = self.log_dir / "metrics.log"

    def setup_logger(self, name: str, log_file: Path,
                    level: int = logging.INFO) -> logging.Logger:
        """Setup a logger with file handler"""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        # Create rotating file handler (10MB, keep 10 files)
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )

        # Set appropriate level for handler
        handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        return logger

    def get_trading_logger(self) -> logging.Logger:
        """Get logger for trading activities"""
        return self.setup_logger(
            'TradingEngine',
            self.trading_log,
            level=logging.INFO
        )

    def get_analysis_logger(self) -> logging.Logger:
        """Get logger for analysis/indicators"""
        return self.setup_logger(
            'Analysis',
            self.analysis_log,
            level=logging.DEBUG
        )

    def get_error_logger(self) -> logging.Logger:
        """Get logger for errors"""
        return self.setup_logger(
            'ErrorLogger',
            self.error_log,
            level=logging.ERROR
        )

    def get_alert_logger(self) -> logging.Logger:
        """Get logger for alerts"""
        return self.setup_logger(
            'AlertLogger',
            self.alert_log,
            level=logging.WARNING
        )

    def get_metrics_logger(self) -> logging.Logger:
        """Get logger for metrics"""
        return self.setup_logger(
            'MetricsLogger',
            self.metrics_log,
            level=logging.INFO
        )

    @staticmethod
    def log_trade(logger: logging.Logger, trade_data: dict):
        """Log a trade execution"""
        msg = (f"TRADE | Pair: {trade_data.get('pair')} | "
              f"Signal: {trade_data.get('signal')} | "
              f"Confidence: {trade_data.get('confidence'):.1f}% | "
              f"Amount: ${trade_data.get('amount'):.2f}")
        logger.info(msg)

    @staticmethod
    def log_trade_result(logger: logging.Logger, trade_data: dict):
        """Log trade result"""
        msg = (f"RESULT | Pair: {trade_data.get('pair')} | "
              f"Result: {trade_data.get('result')} | "
              f"Profit: ${trade_data.get('profit', 0):.2f}")
        logger.info(msg)

    @staticmethod
    def log_indicator(logger: logging.Logger, pair: str, indicator_data: dict):
        """Log indicator values"""
        msg = f"INDICATOR | {pair} | RSI: {indicator_data.get('rsi', 0):.2f} | " \
              f"MACD: {indicator_data.get('macd', 0):.4f} | " \
              f"Stoch: {indicator_data.get('stoch', 0):.2f}"
        logger.debug(msg)

    @staticmethod
    def log_error(logger: logging.Logger, error_msg: str, exception: Optional[Exception] = None):
        """Log an error"""
        if exception:
            logger.exception(f"ERROR: {error_msg}")
        else:
            logger.error(f"ERROR: {error_msg}")

    @staticmethod
    def log_alert(logger: logging.Logger, alert_type: str, message: str):
        """Log an alert"""
        logger.warning(f"ALERT [{alert_type}]: {message}")

    @staticmethod
    def log_metrics(logger: logging.Logger, metrics: dict):
        """Log current metrics"""
        msg = (f"METRICS | Trades: {metrics.get('total_trades', 0)} | "
              f"Win Rate: {metrics.get('win_rate', 0):.2f}% | "
              f"Profit: ${metrics.get('total_profit', 0):.2f}")
        logger.info(msg)

    def verify_logs(self) -> bool:
        """Verify logging is working correctly"""
        try:
            # Try to write to each log file
            for name, log_file in [
                ('Trading', self.trading_log),
                ('Analysis', self.analysis_log),
                ('Errors', self.error_log),
                ('Alerts', self.alert_log),
                ('Metrics', self.metrics_log),
            ]:
                logger = logging.getLogger(f'Verify_{name}')
                handler = logging.FileHandler(log_file)
                logger.addHandler(handler)
                logger.info(f"Logging verification successful for {name}")
                handler.close()

            return True
        except Exception as e:
            print(f"Error verifying logs: {e}")
            return False

    def get_log_files(self) -> dict:
        """Get information about all log files"""
        log_files = {}

        for log_file in self.log_dir.glob("*.log"):
            try:
                size = log_file.stat().st_size
                size_mb = size / (1024 * 1024)
                log_files[log_file.name] = {
                    'path': str(log_file),
                    'size_bytes': size,
                    'size_mb': round(size_mb, 2),
                    'created': datetime.fromtimestamp(
                        log_file.stat().st_ctime
                    ).isoformat(),
                    'modified': datetime.fromtimestamp(
                        log_file.stat().st_mtime
                    ).isoformat(),
                }
            except Exception as e:
                print(f"Error reading {log_file}: {e}")

        return log_files

    def cleanup_old_logs(self, days: int = 7):
        """Clean up log files older than specified days"""
        import time

        cutoff_time = time.time() - (days * 24 * 60 * 60)

        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    print(f"Deleted old log: {log_file.name}")
                except Exception as e:
                    print(f"Error deleting {log_file}: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Logging configuration for paper trading')
    parser.add_argument('--log-dir', default='logs', help='Log directory path')
    parser.add_argument('--verify', action='store_true', help='Verify logging setup')
    parser.add_argument('--show-files', action='store_true', help='Show log files info')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Clean logs older than N days')

    args = parser.parse_args()

    config = LoggingConfig(log_dir=args.log_dir)

    if args.verify:
        print("Verifying logging configuration...")
        if config.verify_logs():
            print("✓ Logging verification successful!")
        else:
            print("✗ Logging verification failed!")

    if args.show_files:
        print("\nLog Files:")
        print("-" * 80)
        files = config.get_log_files()
        if files:
            for name, info in sorted(files.items()):
                print(f"  {name}")
                print(f"    Path: {info['path']}")
                print(f"    Size: {info['size_mb']} MB")
                print(f"    Modified: {info['modified']}")
        else:
            print("  No log files found")

    if args.cleanup:
        print(f"\nCleaning logs older than {args.cleanup} days...")
        config.cleanup_old_logs(args.cleanup)
        print("Cleanup complete")


if __name__ == '__main__':
    main()
