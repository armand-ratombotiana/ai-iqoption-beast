#!/usr/bin/env python3
"""
Alert System for Paper Trading
Monitors for critical events and alerts the user

Alerts:
- Consecutive losses (3+)
- Approaching daily loss limit
- Connection issues
- Low signal quality (<50% confidence)
- High drawdown
- Trading paused conditions
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Types of alerts"""
    CONSECUTIVE_LOSSES = "consecutive_losses"
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    CONNECTION_ISSUE = "connection_issue"
    LOW_SIGNAL_QUALITY = "low_signal_quality"
    HIGH_DRAWDOWN = "high_drawdown"
    TRADING_PAUSED = "trading_paused"
    RECOVERY_SUCCESS = "recovery_success"
    ENGINE_ERROR = "engine_error"


class Alert:
    """Individual alert"""

    def __init__(self, alert_type: AlertType, level: AlertLevel, message: str,
                 timestamp: Optional[datetime] = None):
        """Initialize alert"""
        self.alert_type = alert_type
        self.level = level
        self.message = message
        self.timestamp = timestamp or datetime.now()
        self.acknowledged = False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'type': self.alert_type.value,
            'level': self.level.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged
        }


class AlertSystem:
    """Central alert management system"""

    def __init__(self, data_dir: str = "data", log_dir: str = "logs"):
        """Initialize alert system"""
        self.data_dir = Path(data_dir)
        self.log_dir = Path(log_dir)
        self.alerts_file = self.data_dir / "alerts.json"
        self.status_file = self.data_dir / "status.json"
        self.trades_file = self.data_dir / "trades.json"

        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()

        # Active alerts
        self.active_alerts: Dict[AlertType, Alert] = {}

        # Alert handlers (callbacks for actions)
        self.handlers: Dict[AlertType, List[Callable]] = {
            alert_type: [] for alert_type in AlertType
        }

        # Configuration thresholds
        self.config = {
            'consecutive_loss_threshold': 3,
            'daily_loss_limit': 20.0,
            'low_confidence_threshold': 50,
            'high_drawdown_threshold': 50.0,
            'check_interval': 30,  # seconds
        }

        # Load previous alerts
        self._load_alerts()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for alerts"""
        logger = logging.getLogger('AlertSystem')
        logger.setLevel(logging.INFO)

        # File handler
        alert_log = self.log_dir / "alerts.log"
        file_handler = logging.FileHandler(alert_log)
        file_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def _load_alerts(self):
        """Load previous alerts from file"""
        try:
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                    # Load recent critical alerts
                    for alert_data in data.get('recent', []):
                        if not alert_data.get('acknowledged'):
                            alert = Alert(
                                AlertType(alert_data['type']),
                                AlertLevel(alert_data['level']),
                                alert_data['message'],
                                datetime.fromisoformat(alert_data['timestamp'])
                            )
                            self.active_alerts[alert.alert_type] = alert
        except Exception as e:
            self.logger.error(f"Could not load previous alerts: {e}")

    def _save_alerts(self):
        """Save alerts to file"""
        try:
            recent = list(self.active_alerts.values())[:10]  # Keep last 10
            with open(self.alerts_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'recent': [a.to_dict() for a in recent]
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save alerts: {e}")

    def trigger_alert(self, alert_type: AlertType, level: AlertLevel,
                     message: str) -> Alert:
        """Trigger an alert"""
        alert = Alert(alert_type, level, message)

        # Log alert
        log_level = logging.WARNING if level == AlertLevel.WARNING else logging.CRITICAL
        self.logger.log(log_level, f"[{alert_type.value}] {message}")

        # Store alert
        self.active_alerts[alert_type] = alert

        # Execute handlers
        if alert_type in self.handlers:
            for handler in self.handlers[alert_type]:
                try:
                    handler(alert)
                except Exception as e:
                    self.logger.error(f"Error executing alert handler: {e}")

        # Save
        self._save_alerts()

        return alert

    def register_handler(self, alert_type: AlertType, handler: Callable):
        """Register a callback for alert type"""
        if alert_type in self.handlers:
            self.handlers[alert_type].append(handler)

    def acknowledge_alert(self, alert_type: AlertType):
        """Acknowledge an alert"""
        if alert_type in self.active_alerts:
            self.active_alerts[alert_type].acknowledged = True
            self._save_alerts()

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())

    def get_critical_alerts(self) -> List[Alert]:
        """Get critical alerts"""
        return [a for a in self.active_alerts.values()
                if a.level == AlertLevel.CRITICAL and not a.acknowledged]

    def check_consecutive_losses(self, consecutive_losses: int) -> bool:
        """Check for consecutive losses alert"""
        threshold = self.config['consecutive_loss_threshold']

        if consecutive_losses >= threshold:
            if AlertType.CONSECUTIVE_LOSSES not in self.active_alerts:
                self.trigger_alert(
                    AlertType.CONSECUTIVE_LOSSES,
                    AlertLevel.CRITICAL,
                    f"ALERT: {consecutive_losses} consecutive losses detected!"
                )
            return True

        # Clear alert if consecutive losses drop below threshold
        elif AlertType.CONSECUTIVE_LOSSES in self.active_alerts:
            self.acknowledge_alert(AlertType.CONSECUTIVE_LOSSES)
            self.logger.info(f"Consecutive loss streak broken at {consecutive_losses}")

        return False

    def check_daily_loss_limit(self, daily_loss: float, daily_loss_limit: float) -> bool:
        """Check for approaching/exceeded daily loss limit"""
        percentage = (abs(daily_loss) / daily_loss_limit) * 100 if daily_loss_limit > 0 else 0

        if percentage >= 100:
            self.trigger_alert(
                AlertType.DAILY_LOSS_LIMIT,
                AlertLevel.CRITICAL,
                f"ALERT: Daily loss limit reached! Loss: ${abs(daily_loss):.2f}"
            )
            return True
        elif percentage >= 80:
            self.trigger_alert(
                AlertType.DAILY_LOSS_LIMIT,
                AlertLevel.WARNING,
                f"WARNING: Daily loss limit {percentage:.0f}% reached. "
                f"Loss: ${abs(daily_loss):.2f} / Limit: ${daily_loss_limit:.2f}"
            )
            return True

        # Clear alert if back to safe territory
        elif AlertType.DAILY_LOSS_LIMIT in self.active_alerts and percentage < 50:
            self.acknowledge_alert(AlertType.DAILY_LOSS_LIMIT)

        return False

    def check_connection_status(self, connected: bool) -> bool:
        """Check connection status"""
        if not connected:
            if AlertType.CONNECTION_ISSUE not in self.active_alerts:
                self.trigger_alert(
                    AlertType.CONNECTION_ISSUE,
                    AlertLevel.CRITICAL,
                    "ALERT: Lost connection to trading server!"
                )
            return False
        else:
            if AlertType.CONNECTION_ISSUE in self.active_alerts:
                self.trigger_alert(
                    AlertType.CONNECTION_ISSUE,
                    AlertLevel.INFO,
                    "Connection restored to trading server"
                )
                self.acknowledge_alert(AlertType.CONNECTION_ISSUE)
            return True

    def check_signal_quality(self, confidence: float) -> bool:
        """Check signal confidence quality"""
        threshold = self.config['low_confidence_threshold']

        if confidence < threshold:
            if AlertType.LOW_SIGNAL_QUALITY not in self.active_alerts:
                self.trigger_alert(
                    AlertType.LOW_SIGNAL_QUALITY,
                    AlertLevel.WARNING,
                    f"WARNING: Low signal quality detected. "
                    f"Confidence: {confidence:.1f}% (threshold: {threshold}%)"
                )
            return False

        # Clear alert if quality improves
        elif AlertType.LOW_SIGNAL_QUALITY in self.active_alerts:
            self.acknowledge_alert(AlertType.LOW_SIGNAL_QUALITY)

        return True

    def check_drawdown(self, max_drawdown: float,
                      drawdown_limit: Optional[float] = None) -> bool:
        """Check drawdown levels"""
        limit = drawdown_limit or self.config['high_drawdown_threshold']

        if max_drawdown > limit:
            if AlertType.HIGH_DRAWDOWN not in self.active_alerts:
                self.trigger_alert(
                    AlertType.HIGH_DRAWDOWN,
                    AlertLevel.WARNING,
                    f"WARNING: High drawdown detected. "
                    f"Drawdown: ${max_drawdown:.2f} (threshold: ${limit:.2f})"
                )
            return True

        # Clear alert if drawdown reduces
        elif AlertType.HIGH_DRAWDOWN in self.active_alerts and max_drawdown < (limit * 0.7):
            self.acknowledge_alert(AlertType.HIGH_DRAWDOWN)

        return False

    def check_engine_health(self) -> bool:
        """Check overall engine health"""
        try:
            if not self.status_file.exists():
                return False

            with open(self.status_file, 'r') as f:
                status = json.load(f)

            is_running = status.get('is_running', False)
            connected = status.get('connected', False)

            if not is_running or not connected:
                self.trigger_alert(
                    AlertType.ENGINE_ERROR,
                    AlertLevel.CRITICAL,
                    f"Engine health check failed. Running: {is_running}, Connected: {connected}"
                )
                return False

            return True

        except Exception as e:
            self.trigger_alert(
                AlertType.ENGINE_ERROR,
                AlertLevel.CRITICAL,
                f"Error checking engine health: {e}"
            )
            return False

    def run_checks(self) -> Dict[str, bool]:
        """Run all monitoring checks"""
        results = {}

        try:
            # Load current metrics
            trades_file = self.data_dir / "trades.json"
            if trades_file.exists():
                with open(trades_file, 'r') as f:
                    trades = json.load(f)
                    completed = [t for t in trades if t.get('result') is not None]

                    if completed:
                        # Consecutive losses
                        consecutive = 0
                        for t in reversed(completed):
                            if t.get('result') == 'LOSS':
                                consecutive += 1
                            else:
                                break
                        results['consecutive_losses'] = not self.check_consecutive_losses(consecutive)

                        # Daily loss
                        today = datetime.now().date()
                        today_trades = [
                            t for t in completed
                            if datetime.fromisoformat(t.get('timestamp', '')).date() == today
                        ]
                        daily_loss = sum(
                            float(t.get('profit', 0)) for t in today_trades
                            if float(t.get('profit', 0)) < 0
                        )
                        results['daily_loss'] = not self.check_daily_loss_limit(daily_loss, 20.0)

            # Connection status
            status_file = self.status_file
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f)
                    results['connection'] = self.check_connection_status(status.get('connected', False))

            # Engine health
            results['engine_health'] = self.check_engine_health()

        except Exception as e:
            self.logger.error(f"Error running checks: {e}")

        return results

    def print_alerts(self):
        """Print current alerts"""
        alerts = self.get_active_alerts()

        if not alerts:
            print("No active alerts")
            return

        print("\nACTIVE ALERTS:")
        print("-" * 80)

        for alert in sorted(alerts, key=lambda a: a.level.value, reverse=True):
            status = "ACKNOWLEDGED" if alert.acknowledged else "ACTIVE"
            timestamp = alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{alert.level.value:8}] [{timestamp}] {alert.message} ({status})")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Alert system for paper trading')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    parser.add_argument('--log-dir', default='logs', help='Log directory path')
    parser.add_argument('--check', action='store_true', help='Run health checks')
    parser.add_argument('--alerts', action='store_true', help='Show current alerts')

    args = parser.parse_args()

    alert_system = AlertSystem(data_dir=args.data_dir, log_dir=args.log_dir)

    if args.check:
        print("Running alert system checks...")
        results = alert_system.run_checks()
        for check, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"  {check}: {status}")

    if args.alerts:
        alert_system.print_alerts()

    # Show any critical alerts
    critical = alert_system.get_critical_alerts()
    if critical:
        print(f"\nCRITICAL ALERTS ({len(critical)}):")
        for alert in critical:
            print(f"  {alert.message}")


if __name__ == '__main__':
    main()
