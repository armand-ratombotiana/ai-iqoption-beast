"""
Database Migration Tools
Migrate data from SQLite to PostgreSQL/TimescaleDB
"""
import sqlite3
import os
from typing import Dict, List
from datetime import datetime
from postgres_connector import PostgresConnector


class DatabaseMigrator:
    """Migrate trading data from SQLite to PostgreSQL"""

    def __init__(self, sqlite_path: str, postgres_connector: PostgresConnector):
        """
        Initialize migrator

        Args:
            sqlite_path: Path to SQLite database
            postgres_connector: PostgresConnector instance
        """
        self.sqlite_path = sqlite_path
        self.pg = postgres_connector
        self.stats = {
            'trades_migrated': 0,
            'ai_predictions_migrated': 0,
            'errors': []
        }

    def migrate_all(self):
        """Migrate all data from SQLite to PostgreSQL"""
        print("=" * 80)
        print("DATABASE MIGRATION: SQLite → PostgreSQL/TimescaleDB")
        print("=" * 80)

        # Check if SQLite DB exists
        if not os.path.exists(self.sqlite_path):
            print(f"✗ SQLite database not found: {self.sqlite_path}")
            return

        # Connect to SQLite
        sqlite_conn = sqlite3.connect(self.sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row  # Access columns by name

        try:
            # Migrate AI models
            print("\n[1/3] Migrating AI models...")
            self._migrate_ai_models(sqlite_conn)

            # Migrate trades
            print("\n[2/3] Migrating trades...")
            self._migrate_trades(sqlite_conn)

            # Migrate AI predictions (if table exists)
            print("\n[3/3] Migrating AI predictions...")
            self._migrate_ai_predictions(sqlite_conn)

            # Print summary
            print("\n" + "=" * 80)
            print("MIGRATION COMPLETE")
            print("=" * 80)
            print(f"✓ Trades migrated: {self.stats['trades_migrated']}")
            print(f"✓ AI predictions migrated: {self.stats['ai_predictions_migrated']}")
            if self.stats['errors']:
                print(f"\n⚠ Errors encountered: {len(self.stats['errors'])}")
                for error in self.stats['errors'][:5]:  # Show first 5 errors
                    print(f"  - {error}")

        finally:
            sqlite_conn.close()

    def _migrate_ai_models(self, sqlite_conn: sqlite3.Connection):
        """Migrate AI models registry"""
        cursor = sqlite_conn.cursor()

        # Check if ai_models table exists in SQLite
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_models';")
        if not cursor.fetchone():
            print("  ⚠ ai_models table not found in SQLite, creating default models in PostgreSQL...")
            self._create_default_ai_models()
            return

        # Get models from SQLite
        cursor.execute("SELECT * FROM ai_models;")
        models = cursor.fetchall()

        if not models:
            print("  ⚠ No models found in SQLite, creating defaults...")
            self._create_default_ai_models()
            return

        # Insert into PostgreSQL
        for model in models:
            query = """
            INSERT INTO ai_models (model_name, model_type, provider, version, cost_per_request, is_active)
            VALUES (%(model_name)s, %(model_type)s, %(provider)s, %(version)s, %(cost_per_request)s, %(is_active)s)
            ON CONFLICT (model_name) DO NOTHING;
            """

            model_data = dict(model)
            try:
                self.pg.execute_query(query, model_data, fetch=False)
            except Exception as e:
                self.stats['errors'].append(f"AI model migration error: {e}")

        print(f"  ✓ Migrated {len(models)} AI models")

    def _create_default_ai_models(self):
        """Create default AI models in PostgreSQL"""
        default_models = [
            {'model_name': 'openai-gpt-4o-mini', 'model_type': 'LLM', 'provider': 'OpenAI', 'version': '1.0', 'cost_per_request': 0.0001, 'is_active': True},
            {'model_name': 'claude-claude-3-5-haiku-20241022', 'model_type': 'LLM', 'provider': 'Anthropic', 'version': '1.0', 'cost_per_request': 0.0001, 'is_active': True},
            {'model_name': 'deepseek-deepseek-chat', 'model_type': 'LLM', 'provider': 'DeepSeek', 'version': '1.0', 'cost_per_request': 0.00001, 'is_active': True},
            {'model_name': 'lstm-price-predictor', 'model_type': 'DL', 'provider': 'Local', 'version': '1.0', 'cost_per_request': 0.0, 'is_active': True},
            {'model_name': 'xgboost-ensemble', 'model_type': 'ML', 'provider': 'Local', 'version': '1.0', 'cost_per_request': 0.0, 'is_active': True},
            {'model_name': 'gemini-gemini-2.0-flash-exp', 'model_type': 'LLM', 'provider': 'Google', 'version': '1.0', 'cost_per_request': 0.0, 'is_active': True},
            {'model_name': 'mistral-mistral-small-latest', 'model_type': 'LLM', 'provider': 'Mistral', 'version': '1.0', 'cost_per_request': 0.00002, 'is_active': True},
            {'model_name': 'ollama-llama3.2', 'model_type': 'LLM', 'provider': 'Ollama', 'version': '1.0', 'cost_per_request': 0.0, 'is_active': True},
        ]

        for model in default_models:
            query = """
            INSERT INTO ai_models (model_name, model_type, provider, version, cost_per_request, is_active)
            VALUES (%(model_name)s, %(model_type)s, %(provider)s, %(version)s, %(cost_per_request)s, %(is_active)s)
            ON CONFLICT (model_name) DO NOTHING;
            """
            try:
                self.pg.execute_query(query, model, fetch=False)
            except Exception as e:
                self.stats['errors'].append(f"Default model creation error: {e}")

        print(f"  ✓ Created {len(default_models)} default AI models")

    def _migrate_trades(self, sqlite_conn: sqlite3.Connection):
        """Migrate trades from SQLite to PostgreSQL"""
        cursor = sqlite_conn.cursor()

        # Get all trades
        cursor.execute("SELECT * FROM trades ORDER BY timestamp;")
        trades = cursor.fetchall()

        if not trades:
            print("  ⚠ No trades found in SQLite")
            return

        print(f"  Found {len(trades)} trades to migrate...")

        # Migrate in batches
        batch_size = 100
        for i in range(0, len(trades), batch_size):
            batch = trades[i:i + batch_size]

            for trade in batch:
                trade_data = self._convert_trade_to_postgres(dict(trade))

                query = """
                INSERT INTO trades (
                    timestamp, pair, direction, amount, duration, result, profit,
                    entry_price, exit_price, ai_signal_confidence, ai_model_agreement, ai_models_count,
                    rsi_14, macd_value, bb_upper, bb_middle, bb_lower,
                    trend, volatility, market_regime,
                    hour_of_day, day_of_week,
                    strategy_version, model_version, notes
                ) VALUES (
                    %(timestamp)s, %(pair)s, %(direction)s, %(amount)s, %(duration)s, %(result)s, %(profit)s,
                    %(entry_price)s, %(exit_price)s, %(ai_signal_confidence)s, %(ai_model_agreement)s, %(ai_models_count)s,
                    %(rsi_14)s, %(macd_value)s, %(bb_upper)s, %(bb_middle)s, %(bb_lower)s,
                    %(trend)s, %(volatility)s, %(market_regime)s,
                    %(hour_of_day)s, %(day_of_week)s,
                    %(strategy_version)s, %(model_version)s, %(notes)s
                )
                ON CONFLICT (timestamp, trade_id) DO NOTHING;
                """

                try:
                    self.pg.execute_query(query, trade_data, fetch=False)
                    self.stats['trades_migrated'] += 1
                except Exception as e:
                    self.stats['errors'].append(f"Trade migration error: {e}")

            print(f"  Progress: {min(i + batch_size, len(trades))}/{len(trades)} trades")

        print(f"  ✓ Migrated {self.stats['trades_migrated']} trades")

    def _convert_trade_to_postgres(self, trade: Dict) -> Dict:
        """Convert SQLite trade record to PostgreSQL format"""
        # Parse timestamp
        if isinstance(trade.get('timestamp'), str):
            try:
                trade['timestamp'] = datetime.fromisoformat(trade['timestamp'])
            except:
                trade['timestamp'] = datetime.now()

        # Extract hour and day of week from timestamp
        if 'timestamp' in trade and isinstance(trade['timestamp'], datetime):
            trade['hour_of_day'] = trade['timestamp'].hour
            trade['day_of_week'] = trade['timestamp'].weekday()

        # Set defaults for new fields
        defaults = {
            'rsi_14': None,
            'macd_value': None,
            'bb_upper': None,
            'bb_middle': None,
            'bb_lower': None,
            'trend': None,
            'volatility': None,
            'market_regime': None,
            'ai_model_agreement': None,
            'ai_models_count': None,
            'strategy_version': 'v1.0',
            'model_version': 'v1.0',
            'notes': None
        }

        for key, value in defaults.items():
            if key not in trade:
                trade[key] = value

        return trade

    def _migrate_ai_predictions(self, sqlite_conn: sqlite3.Connection):
        """Migrate AI predictions (if table exists)"""
        cursor = sqlite_conn.cursor()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_predictions';")
        if not cursor.fetchone():
            print("  ⚠ ai_predictions table not found in SQLite, skipping...")
            return

        # Get predictions
        cursor.execute("SELECT * FROM ai_predictions ORDER BY timestamp;")
        predictions = cursor.fetchall()

        if not predictions:
            print("  ⚠ No AI predictions found in SQLite")
            return

        print(f"  Found {len(predictions)} predictions to migrate...")

        # Need to map model names to model IDs
        model_name_to_id = self._get_model_name_to_id_mapping()

        for prediction in predictions:
            pred_data = dict(prediction)

            # Convert timestamp
            if isinstance(pred_data.get('timestamp'), str):
                try:
                    pred_data['timestamp'] = datetime.fromisoformat(pred_data['timestamp'])
                except:
                    pred_data['timestamp'] = datetime.now()

            # Map model_name to model_id
            model_name = pred_data.get('model_name') or pred_data.get('model')
            if model_name and model_name in model_name_to_id:
                pred_data['model_id'] = model_name_to_id[model_name]
            else:
                # Skip if model not found
                continue

            query = """
            INSERT INTO ai_predictions (
                timestamp, trade_id, model_id, signal, confidence, reasoning
            ) VALUES (
                %(timestamp)s, %(trade_id)s, %(model_id)s, %(signal)s, %(confidence)s, %(reasoning)s
            );
            """

            try:
                self.pg.execute_query(query, pred_data, fetch=False)
                self.stats['ai_predictions_migrated'] += 1
            except Exception as e:
                self.stats['errors'].append(f"Prediction migration error: {e}")

        print(f"  ✓ Migrated {self.stats['ai_predictions_migrated']} AI predictions")

    def _get_model_name_to_id_mapping(self) -> Dict[str, int]:
        """Get mapping of model names to IDs from PostgreSQL"""
        query = "SELECT model_id, model_name FROM ai_models;"
        results = self.pg.execute_query(query)

        mapping = {}
        if results:
            for row in results:
                mapping[row['model_name']] = row['model_id']

        return mapping


def setup_postgres_database(postgres_connector: PostgresConnector, schema_file: str = None):
    """
    Initialize PostgreSQL database with schema

    Args:
        postgres_connector: PostgresConnector instance
        schema_file: Path to SQL schema file
    """
    if schema_file is None:
        schema_file = os.path.join(os.path.dirname(__file__), 'advanced_db_schema.sql')

    if not os.path.exists(schema_file):
        print(f"✗ Schema file not found: {schema_file}")
        return False

    print("=" * 80)
    print("INITIALIZING POSTGRESQL DATABASE")
    print("=" * 80)

    try:
        # Read schema file
        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        # Split into individual statements (simple split on semicolons)
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

        print(f"Executing {len(statements)} SQL statements...")

        # Execute each statement
        for i, statement in enumerate(statements, 1):
            try:
                postgres_connector.execute_query(statement, fetch=False)
            except Exception as e:
                # Some statements may fail if objects already exist, that's okay
                if 'already exists' not in str(e).lower():
                    print(f"  ⚠ Statement {i} warning: {e}")

        print("\n✓ Database schema initialized successfully")
        return True

    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        return False


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Migrate SQLite database to PostgreSQL')
    parser.add_argument('--sqlite', default='../../data/trading.db', help='Path to SQLite database')
    parser.add_argument('--schema', default='advanced_db_schema.sql', help='Path to PostgreSQL schema file')
    parser.add_argument('--init-only', action='store_true', help='Only initialize schema, skip migration')

    args = parser.parse_args()

    # Create PostgreSQL connector
    print("\nConnecting to PostgreSQL...")
    pg = create_connector()

    # Initialize database
    if not args.init_only:
        setup_postgres_database(pg, args.schema)

    # Migrate data
    if not args.init_only:
        print("\nStarting migration...")
        migrator = DatabaseMigrator(args.sqlite, pg)
        migrator.migrate_all()
    else:
        print("\n✓ Schema initialization complete (migration skipped)")

    # Close connection
    pg.close()
