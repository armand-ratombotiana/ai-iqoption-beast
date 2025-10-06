"""
ML Data Exporter
Export training data in formats optimized for ML frameworks
Supports: NumPy, Pandas, TensorFlow, PyTorch, CSV
"""
import numpy as np
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os


class MLDataExporter:
    """Export training data for ML frameworks"""

    def __init__(self, postgres_connector):
        """
        Initialize exporter

        Args:
            postgres_connector: PostgresConnector instance
        """
        self.pg = postgres_connector

    def export_to_numpy(
        self,
        pair: str = None,
        limit: int = 10000,
        timeframe: str = '5min',
        output_dir: str = './ml_data'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Export training data as NumPy arrays

        Args:
            pair: Currency pair filter
            limit: Maximum records
            timeframe: Target timeframe (5min, 15min, 1h)
            output_dir: Directory to save files

        Returns:
            Tuple of (X, y) NumPy arrays
        """
        print(f"Exporting data to NumPy arrays (timeframe={timeframe})...")

        # Get training data
        data = self.pg.get_training_data(pair=pair, limit=limit)

        if not data:
            print("No training data found")
            return np.array([]), np.array([])

        # Filter for records with labels
        label_field = f'label_{timeframe}'
        actual_field = f'actual_{timeframe}'

        valid_data = [
            row for row in data
            if row.get(actual_field) is not None and row.get('feature_vector')
        ]

        print(f"Found {len(valid_data)} valid training samples")

        if not valid_data:
            return np.array([]), np.array([])

        # Extract features (X)
        X = []
        for row in valid_data:
            feature_vector = row['feature_vector']
            if isinstance(feature_vector, str):
                feature_vector = json.loads(feature_vector)

            # Convert to ordered array
            feature_array = self._dict_to_array(feature_vector)
            X.append(feature_array)

        X = np.array(X)

        # Extract labels (y)
        y = []
        for row in valid_data:
            actual = row[actual_field]
            # Binary: 1 = CALL, 0 = PUT
            label = 1 if actual == 'CALL' else 0
            y.append(label)

        y = np.array(y)

        # Save to disk
        os.makedirs(output_dir, exist_ok=True)

        pair_suffix = f"_{pair}" if pair else "_all"
        X_file = os.path.join(output_dir, f"X{pair_suffix}_{timeframe}.npy")
        y_file = os.path.join(output_dir, f"y{pair_suffix}_{timeframe}.npy")

        np.save(X_file, X)
        np.save(y_file, y)

        print(f"✓ Saved NumPy arrays:")
        print(f"  X: {X_file} {X.shape}")
        print(f"  y: {y_file} {y.shape}")

        return X, y

    def export_to_csv(
        self,
        pair: str = None,
        limit: int = 10000,
        timeframe: str = '5min',
        output_file: str = './ml_data/training_data.csv'
    ):
        """
        Export training data as CSV

        Args:
            pair: Currency pair filter
            limit: Maximum records
            timeframe: Target timeframe
            output_file: Output CSV file path
        """
        print(f"Exporting data to CSV (timeframe={timeframe})...")

        # Get training data
        data = self.pg.get_training_data(pair=pair, limit=limit)

        if not data:
            print("No training data found")
            return

        label_field = f'label_{timeframe}'
        actual_field = f'actual_{timeframe}'

        # Prepare CSV
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as f:
            # Write header
            if data:
                first_row = data[0]
                feature_vector = first_row['feature_vector']
                if isinstance(feature_vector, str):
                    feature_vector = json.loads(feature_vector)

                feature_names = sorted(feature_vector.keys())
                header = ['timestamp', 'pair'] + feature_names + ['label', 'actual']
                f.write(','.join(header) + '\n')

                # Write data
                for row in data:
                    if row.get(actual_field) is None:
                        continue

                    feature_vector = row['feature_vector']
                    if isinstance(feature_vector, str):
                        feature_vector = json.loads(feature_vector)

                    values = [
                        str(row['timestamp']),
                        row['pair']
                    ]

                    # Feature values in same order as header
                    for fname in feature_names:
                        values.append(str(feature_vector.get(fname, 0)))

                    # Label and actual
                    values.append(row.get(label_field, ''))
                    values.append(row.get(actual_field, ''))

                    f.write(','.join(values) + '\n')

        print(f"✓ Saved CSV: {output_file}")

    def export_to_tensorflow_dataset(
        self,
        pair: str = None,
        limit: int = 10000,
        timeframe: str = '5min',
        batch_size: int = 32,
        validation_split: float = 0.2
    ):
        """
        Export as TensorFlow dataset (requires TensorFlow)

        Args:
            pair: Currency pair filter
            limit: Maximum records
            timeframe: Target timeframe
            batch_size: Batch size for training
            validation_split: Fraction for validation

        Returns:
            Tuple of (train_dataset, val_dataset) or None if TF not available
        """
        try:
            import tensorflow as tf
        except ImportError:
            print("TensorFlow not installed. Install with: pip install tensorflow")
            return None

        print(f"Creating TensorFlow datasets (timeframe={timeframe})...")

        # Get NumPy arrays
        X, y = self.export_to_numpy(pair=pair, limit=limit, timeframe=timeframe, output_dir='/tmp')

        if len(X) == 0:
            print("No data to export")
            return None

        # Split into train/val
        split_idx = int(len(X) * (1 - validation_split))

        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        # Create TF datasets
        train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
        train_dataset = train_dataset.shuffle(1000).batch(batch_size).prefetch(tf.data.AUTOTUNE)

        val_dataset = tf.data.Dataset.from_tensor_slices((X_val, y_val))
        val_dataset = val_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

        print(f"✓ Created TensorFlow datasets:")
        print(f"  Train: {len(X_train)} samples")
        print(f"  Val: {len(X_val)} samples")

        return train_dataset, val_dataset

    def export_to_pytorch_dataset(
        self,
        pair: str = None,
        limit: int = 10000,
        timeframe: str = '5min',
        output_dir: str = './ml_data'
    ):
        """
        Export as PyTorch dataset (requires PyTorch)

        Args:
            pair: Currency pair filter
            limit: Maximum records
            timeframe: Target timeframe
            output_dir: Output directory

        Returns:
            PyTorchDataset instance or None if PyTorch not available
        """
        try:
            import torch
            from torch.utils.data import Dataset, DataLoader
        except ImportError:
            print("PyTorch not installed. Install with: pip install torch")
            return None

        print(f"Creating PyTorch dataset (timeframe={timeframe})...")

        # Get NumPy arrays
        X, y = self.export_to_numpy(pair=pair, limit=limit, timeframe=timeframe, output_dir=output_dir)

        if len(X) == 0:
            print("No data to export")
            return None

        # Create PyTorch dataset
        class TradingDataset(Dataset):
            def __init__(self, X, y):
                self.X = torch.FloatTensor(X)
                self.y = torch.LongTensor(y)

            def __len__(self):
                return len(self.X)

            def __getitem__(self, idx):
                return self.X[idx], self.y[idx]

        dataset = TradingDataset(X, y)

        print(f"✓ Created PyTorch dataset: {len(dataset)} samples")

        return dataset

    def export_statistics(self, pair: str = None, timeframe: str = '5min') -> Dict:
        """
        Export dataset statistics

        Args:
            pair: Currency pair filter
            timeframe: Target timeframe

        Returns:
            Dictionary with statistics
        """
        data = self.pg.get_training_data(pair=pair, limit=100000)

        if not data:
            return {}

        actual_field = f'actual_{timeframe}'

        # Count labels
        call_count = sum(1 for row in data if row.get(actual_field) == 'CALL')
        put_count = sum(1 for row in data if row.get(actual_field) == 'PUT')
        total = call_count + put_count

        stats = {
            'total_samples': len(data),
            'labeled_samples': total,
            'call_samples': call_count,
            'put_samples': put_count,
            'call_percentage': round(call_count / total * 100, 2) if total > 0 else 0,
            'put_percentage': round(put_count / total * 100, 2) if total > 0 else 0,
            'class_balance': round(min(call_count, put_count) / max(call_count, put_count), 2) if max(call_count, put_count) > 0 else 0
        }

        # Feature statistics
        if data and data[0].get('feature_vector'):
            feature_vector = data[0]['feature_vector']
            if isinstance(feature_vector, str):
                feature_vector = json.loads(feature_vector)

            stats['num_features'] = len(feature_vector)
            stats['feature_names'] = sorted(feature_vector.keys())

        print("\n" + "=" * 60)
        print("DATASET STATISTICS")
        print("=" * 60)
        print(f"Total samples: {stats['total_samples']}")
        print(f"Labeled samples: {stats['labeled_samples']}")
        print(f"  CALL: {stats['call_samples']} ({stats['call_percentage']}%)")
        print(f"  PUT: {stats['put_samples']} ({stats['put_percentage']}%)")
        print(f"Class balance: {stats['class_balance']}")
        print(f"Number of features: {stats.get('num_features', 'N/A')}")
        print("=" * 60)

        return stats

    def _dict_to_array(self, feature_dict: Dict) -> np.ndarray:
        """
        Convert feature dictionary to ordered array

        Args:
            feature_dict: Feature dictionary

        Returns:
            NumPy array with features in consistent order
        """
        # Sort keys for consistent ordering
        sorted_keys = sorted(feature_dict.keys())

        # Extract values
        values = []
        for key in sorted_keys:
            value = feature_dict[key]

            # Handle different types
            if isinstance(value, (int, float)):
                values.append(float(value))
            elif isinstance(value, bool):
                values.append(1.0 if value else 0.0)
            else:
                # Skip non-numeric features
                values.append(0.0)

        return np.array(values)

    def create_training_splits(
        self,
        pair: str = None,
        timeframe: str = '5min',
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        output_dir: str = './ml_data'
    ):
        """
        Create train/val/test splits

        Args:
            pair: Currency pair filter
            timeframe: Target timeframe
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            output_dir: Output directory
        """
        print(f"Creating train/val/test splits...")

        # Get data
        X, y = self.export_to_numpy(pair=pair, limit=100000, timeframe=timeframe, output_dir='/tmp')

        if len(X) == 0:
            print("No data to split")
            return

        # Calculate split indices
        n = len(X)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)

        # Split
        X_train, y_train = X[:train_end], y[:train_end]
        X_val, y_val = X[train_end:val_end], y[train_end:val_end]
        X_test, y_test = X[val_end:], y[val_end:]

        # Save
        os.makedirs(output_dir, exist_ok=True)

        pair_suffix = f"_{pair}" if pair else "_all"

        np.save(os.path.join(output_dir, f"X_train{pair_suffix}_{timeframe}.npy"), X_train)
        np.save(os.path.join(output_dir, f"y_train{pair_suffix}_{timeframe}.npy"), y_train)
        np.save(os.path.join(output_dir, f"X_val{pair_suffix}_{timeframe}.npy"), X_val)
        np.save(os.path.join(output_dir, f"y_val{pair_suffix}_{timeframe}.npy"), y_val)
        np.save(os.path.join(output_dir, f"X_test{pair_suffix}_{timeframe}.npy"), X_test)
        np.save(os.path.join(output_dir, f"y_test{pair_suffix}_{timeframe}.npy"), y_test)

        print(f"\n✓ Created splits in {output_dir}:")
        print(f"  Train: {len(X_train)} samples ({train_ratio*100}%)")
        print(f"  Val: {len(X_val)} samples ({val_ratio*100}%)")
        print(f"  Test: {len(X_test)} samples ({test_ratio*100}%)")


# CLI interface
if __name__ == '__main__':
    import argparse
    from postgres_connector import create_connector

    parser = argparse.ArgumentParser(description='Export ML training data')
    parser.add_argument('--format', default='numpy', choices=['numpy', 'csv', 'tensorflow', 'pytorch', 'all'],
                        help='Export format')
    parser.add_argument('--pair', help='Currency pair filter (e.g., EURUSD)')
    parser.add_argument('--limit', type=int, default=10000, help='Maximum records')
    parser.add_argument('--timeframe', default='5min', choices=['5min', '15min', '1h'],
                        help='Target timeframe')
    parser.add_argument('--output-dir', default='./ml_data', help='Output directory')

    args = parser.parse_args()

    # Create connector
    pg = create_connector()

    # Create exporter
    exporter = MLDataExporter(pg)

    # Export statistics
    exporter.export_statistics(pair=args.pair, timeframe=args.timeframe)

    # Export data
    if args.format == 'numpy' or args.format == 'all':
        exporter.export_to_numpy(pair=args.pair, limit=args.limit, timeframe=args.timeframe, output_dir=args.output_dir)
        exporter.create_training_splits(pair=args.pair, timeframe=args.timeframe, output_dir=args.output_dir)

    if args.format == 'csv' or args.format == 'all':
        output_file = os.path.join(args.output_dir, f'training_data_{args.timeframe}.csv')
        exporter.export_to_csv(pair=args.pair, limit=args.limit, timeframe=args.timeframe, output_file=output_file)

    if args.format == 'tensorflow' or args.format == 'all':
        exporter.export_to_tensorflow_dataset(pair=args.pair, limit=args.limit, timeframe=args.timeframe)

    if args.format == 'pytorch' or args.format == 'all':
        exporter.export_to_pytorch_dataset(pair=args.pair, limit=args.limit, timeframe=args.timeframe, output_dir=args.output_dir)

    # Close connection
    pg.close()
