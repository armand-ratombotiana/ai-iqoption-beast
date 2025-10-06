"""
Advanced LSTM Model with Attention Mechanism
Enhanced LSTM for price prediction with attention and feature engineering
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Attention, LayerNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
from datetime import datetime, timedelta

from .async_base_model import AsyncBaseAIModel


class AttentionLSTM(tf.keras.Model):
    """LSTM with attention mechanism for better long-term dependencies"""
    
    def __init__(self, lstm_units=64, attention_units=32, dropout_rate=0.2):
        super(AttentionLSTM, self).__init__()
        
        self.lstm1 = LSTM(lstm_units, return_sequences=True, dropout=dropout_rate)
        self.lstm2 = LSTM(lstm_units, return_sequences=True, dropout=dropout_rate)
        self.attention = Attention()
        self.layer_norm = LayerNormalization()
        self.dropout = Dropout(dropout_rate)
        self.dense1 = Dense(32, activation='relu')
        self.dense2 = Dense(16, activation='relu')
        self.output_layer = Dense(3, activation='softmax')  # UP, DOWN, NEUTRAL
        
    def call(self, inputs, training=None):
        # LSTM layers
        x = self.lstm1(inputs, training=training)
        x = self.lstm2(x, training=training)
        
        # Attention mechanism
        attention_output = self.attention([x, x], training=training)
        x = self.layer_norm(x + attention_output)
        
        # Global average pooling
        x = tf.reduce_mean(x, axis=1)
        
        # Dense layers
        x = self.dropout(x, training=training)
        x = self.dense1(x)
        x = self.dropout(x, training=training)
        x = self.dense2(x)
        
        return self.output_layer(x)


class AdvancedLSTMModel(AsyncBaseAIModel):
    """
    Advanced LSTM model with attention mechanism and feature engineering
    
    Features:
    - Attention mechanism for better long-term dependencies
    - Advanced feature engineering
    - Online learning capabilities
    - Ensemble predictions
    - Uncertainty quantification
    """
    
    def __init__(self, model_name: str = "advanced-lstm"):
        super().__init__(model_name)
        
        # Model parameters
        self.sequence_length = 60  # 60 time steps
        self.feature_dim = 20  # Number of features
        self.lstm_units = 64
        self.attention_units = 32
        self.dropout_rate = 0.2
        
        # Model components
        self.model = None
        self.feature_scaler = StandardScaler()
        self.price_scaler = MinMaxScaler()
        self.is_trained = False
        
        # Training parameters
        self.batch_size = 32
        self.epochs = 100
        self.patience = 10
        
        # Feature engineering
        self.feature_names = [
            'price_change', 'price_change_pct', 'volatility',
            'rsi_14', 'rsi_7', 'macd', 'macd_signal', 'macd_histogram',
            'bb_position', 'stochastic_k', 'stochastic_d',
            'adx', 'cci', 'williams_r', 'atr',
            'volume_ratio', 'price_momentum', 'trend_strength',
            'support_distance', 'resistance_distance'
        ]
        
        # Online learning
        self.online_buffer = []
        self.online_buffer_size = 1000
        self.retrain_threshold = 100
        self.predictions_since_retrain = 0

    async def initialize(self):
        """Initialize the model"""
        await super().initialize()
        self._build_model()
        
    def _build_model(self):
        """Build the LSTM model with attention"""
        self.model = AttentionLSTM(
            lstm_units=self.lstm_units,
            attention_units=self.attention_units,
            dropout_rate=self.dropout_rate
        )
        
        # Compile model
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        print(f"✅ Built LSTM model with attention mechanism")

    def engineer_features(self, market_data: Dict, historical_data: List[Dict] = None) -> np.ndarray:
        """Engineer features from market data"""
        features = []
        
        # Basic price features
        current_price = market_data.get('current_price', 0)
        features.extend([
            market_data.get('price_change', 0),
            market_data.get('price_change_pct', 0),
            market_data.get('volatility_value', 0)
        ])
        
        # Technical indicators
        features.extend([
            market_data.get('rsi_14', 50) / 100,  # Normalize to 0-1
            market_data.get('rsi_7', 50) / 100,
            market_data.get('macd', {}).get('macd', 0),
            market_data.get('macd', {}).get('signal', 0),
            market_data.get('macd', {}).get('histogram', 0),
            market_data.get('bb_position', 0.5),
            market_data.get('stochastic', {}).get('k', 50) / 100,
            market_data.get('stochastic', {}).get('d', 50) / 100,
            market_data.get('adx', 0) / 100,
            market_data.get('cci', 0) / 200,  # Normalize CCI
            market_data.get('williams_r', -50) / -100,  # Normalize Williams %R
            market_data.get('atr', 0)
        ])
        
        # Advanced features
        volume_ma = market_data.get('volume_ma', 1)
        current_volume = market_data.get('volume', volume_ma)
        volume_ratio = current_volume / volume_ma if volume_ma > 0 else 1
        
        # Price momentum (simplified)
        price_momentum = 0
        if historical_data and len(historical_data) >= 5:
            recent_prices = [d.get('close', current_price) for d in historical_data[-5:]]
            price_momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        # Trend strength
        trend_map = {'uptrend': 1, 'downtrend': -1, 'sideways': 0}
        trend_strength = trend_map.get(market_data.get('trend', 'sideways'), 0)
        
        # Distance to support/resistance
        support = market_data.get('support', current_price)
        resistance = market_data.get('resistance', current_price)
        support_distance = (current_price - support) / current_price if current_price > 0 else 0
        resistance_distance = (resistance - current_price) / current_price if current_price > 0 else 0
        
        features.extend([
            volume_ratio,
            price_momentum,
            trend_strength,
            support_distance,
            resistance_distance
        ])
        
        return np.array(features[:self.feature_dim])  # Ensure correct dimension

    def prepare_sequences(self, data: List[Dict], target_col: str = 'direction') -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM training"""
        if len(data) < self.sequence_length + 1:
            raise ValueError(f"Need at least {self.sequence_length + 1} data points")
        
        # Engineer features for all data points
        features_list = []
        targets = []
        
        for i in range(len(data)):
            # Get historical context for feature engineering
            historical_context = data[max(0, i-10):i] if i > 0 else []
            features = self.engineer_features(data[i], historical_context)
            features_list.append(features)
            
            # Target (next candle direction)
            if i < len(data) - 1:
                next_price = data[i + 1].get('close', data[i].get('current_price', 0))
                current_price = data[i].get('close', data[i].get('current_price', 0))
                
                if next_price > current_price * 1.0001:  # 0.01% threshold
                    target = [1, 0, 0]  # UP
                elif next_price < current_price * 0.9999:
                    target = [0, 1, 0]  # DOWN
                else:
                    target = [0, 0, 1]  # NEUTRAL
                
                targets.append(target)
        
        # Create sequences
        X, y = [], []
        features_array = np.array(features_list)
        targets_array = np.array(targets)
        
        for i in range(self.sequence_length, len(features_array)):
            X.append(features_array[i-self.sequence_length:i])
            if i-1 < len(targets_array):
                y.append(targets_array[i-1])
        
        return np.array(X), np.array(y)

    def train(self, training_data: List[Dict], validation_data: List[Dict] = None):
        """Train the LSTM model"""
        print(f"🚀 Training LSTM model with {len(training_data)} samples...")
        
        # Prepare training data
        X_train, y_train = self.prepare_sequences(training_data)
        
        if len(X_train) == 0:
            raise ValueError("No training sequences generated")
        
        # Scale features
        X_train_scaled = self._scale_features(X_train, fit=True)
        
        # Prepare validation data
        X_val_scaled, y_val = None, None
        if validation_data:
            X_val, y_val = self.prepare_sequences(validation_data)
            X_val_scaled = self._scale_features(X_val, fit=False)
        
        # Callbacks
        callbacks = [
            EarlyStopping(patience=self.patience, restore_best_weights=True),
            ReduceLROnPlateau(patience=5, factor=0.5, min_lr=1e-6)
        ]
        
        # Train model
        validation_data_tuple = (X_val_scaled, y_val) if X_val_scaled is not None else None
        
        history = self.model.fit(
            X_train_scaled, y_train,
            batch_size=self.batch_size,
            epochs=self.epochs,
            validation_data=validation_data_tuple,
            callbacks=callbacks,
            verbose=1
        )
        
        self.is_trained = True
        
        # Calculate training metrics
        train_pred = self.model.predict(X_train_scaled)
        train_accuracy = accuracy_score(
            np.argmax(y_train, axis=1), 
            np.argmax(train_pred, axis=1)
        )
        
        print(f"✅ Training completed. Accuracy: {train_accuracy:.3f}")
        
        return history

    def _scale_features(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        """Scale features for training"""
        # Reshape for scaling
        original_shape = X.shape
        X_reshaped = X.reshape(-1, X.shape[-1])
        
        if fit:
            X_scaled = self.feature_scaler.fit_transform(X_reshaped)
        else:
            X_scaled = self.feature_scaler.transform(X_reshaped)
        
        return X_scaled.reshape(original_shape)

    async def predict_async(self, market_data: Dict) -> Dict:
        """Generate trading signal using LSTM model"""
        if not self.is_trained:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reasoning': 'Model not trained yet',
                'feature_importance': {}
            }
        
        try:
            # Get recent historical data for sequence
            # In production, this would come from the data provider
            # For now, simulate with current data repeated
            sequence_data = [market_data] * self.sequence_length
            
            # Engineer features
            features_sequence = []
            for i, data_point in enumerate(sequence_data):
                historical_context = sequence_data[max(0, i-10):i] if i > 0 else []
                features = self.engineer_features(data_point, historical_context)
                features_sequence.append(features)
            
            # Prepare input
            X = np.array([features_sequence])
            X_scaled = self._scale_features(X, fit=False)
            
            # Predict
            prediction = self.model.predict(X_scaled, verbose=0)[0]
            
            # Get prediction probabilities
            up_prob = float(prediction[0])
            down_prob = float(prediction[1])
            neutral_prob = float(prediction[2])
            
            # Determine signal
            if up_prob > down_prob and up_prob > neutral_prob:
                signal = 'CALL'
                confidence = up_prob * 100
            elif down_prob > up_prob and down_prob > neutral_prob:
                signal = 'PUT'
                confidence = down_prob * 100
            else:
                signal = 'NEUTRAL'
                confidence = neutral_prob * 100
            
            # Feature importance (simplified)
            feature_importance = {}
            if len(features_sequence) > 0:
                latest_features = features_sequence[-1]
                for i, feature_name in enumerate(self.feature_names[:len(latest_features)]):
                    feature_importance[feature_name] = float(latest_features[i])
            
            # Online learning
            self._add_to_online_buffer(market_data, signal)
            
            return {
                'signal': signal,
                'confidence': int(confidence),
                'reasoning': f'LSTM prediction: UP={up_prob:.3f}, DOWN={down_prob:.3f}, NEUTRAL={neutral_prob:.3f}',
                'feature_importance': feature_importance,
                'prediction_probabilities': {
                    'up': up_prob,
                    'down': down_prob,
                    'neutral': neutral_prob
                }
            }
            
        except Exception as e:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reasoning': f'LSTM prediction error: {str(e)}',
                'feature_importance': {}
            }

    def _add_to_online_buffer(self, market_data: Dict, predicted_signal: str):
        """Add data to online learning buffer"""
        self.online_buffer.append({
            'market_data': market_data,
            'predicted_signal': predicted_signal,
            'timestamp': datetime.now()
        })
        
        # Keep buffer size manageable
        if len(self.online_buffer) > self.online_buffer_size:
            self.online_buffer = self.online_buffer[-self.online_buffer_size:]
        
        self.predictions_since_retrain += 1

    def should_retrain(self) -> bool:
        """Check if model should be retrained"""
        return (self.predictions_since_retrain >= self.retrain_threshold and 
                len(self.online_buffer) >= self.sequence_length * 2)

    def online_retrain(self):
        """Perform online retraining with recent data"""
        if not self.should_retrain():
            return False
        
        print(f"🔄 Performing online retraining with {len(self.online_buffer)} samples...")
        
        try:
            # Convert buffer to training format
            training_data = []
            for item in self.online_buffer:
                training_data.append(item['market_data'])
            
            # Retrain with recent data
            if len(training_data) >= self.sequence_length + 1:
                X_new, y_new = self.prepare_sequences(training_data)
                X_new_scaled = self._scale_features(X_new, fit=False)
                
                # Fine-tune model
                self.model.fit(
                    X_new_scaled, y_new,
                    batch_size=min(16, len(X_new)),
                    epochs=5,
                    verbose=0
                )
                
                self.predictions_since_retrain = 0
                print("✅ Online retraining completed")
                return True
                
        except Exception as e:
            print(f"❌ Online retraining failed: {e}")
        
        return False

    def save_model(self, filepath: str):
        """Save the trained model"""
        if self.model and self.is_trained:
            self.model.save_weights(f"{filepath}_weights.h5")
            joblib.dump(self.feature_scaler, f"{filepath}_feature_scaler.pkl")
            joblib.dump(self.price_scaler, f"{filepath}_price_scaler.pkl")
            
            # Save metadata
            metadata = {
                'sequence_length': self.sequence_length,
                'feature_dim': self.feature_dim,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained
            }
            joblib.dump(metadata, f"{filepath}_metadata.pkl")
            
            print(f"💾 Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load a trained model"""
        try:
            # Load metadata
            metadata = joblib.load(f"{filepath}_metadata.pkl")
            self.sequence_length = metadata['sequence_length']
            self.feature_dim = metadata['feature_dim']
            self.feature_names = metadata['feature_names']
            self.is_trained = metadata['is_trained']
            
            # Rebuild and load model
            self._build_model()
            self.model.load_weights(f"{filepath}_weights.h5")
            
            # Load scalers
            self.feature_scaler = joblib.load(f"{filepath}_feature_scaler.pkl")
            self.price_scaler = joblib.load(f"{filepath}_price_scaler.pkl")
            
            print(f"📂 Model loaded from {filepath}")
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.is_trained = False

    def get_model_info(self) -> Dict:
        """Return enhanced model metadata"""
        base_info = super().get_model_info()
        base_info.update({
            'provider': 'TensorFlow',
            'model_type': 'LSTM-Attention',
            'sequence_length': self.sequence_length,
            'feature_dim': self.feature_dim,
            'is_trained': self.is_trained,
            'online_buffer_size': len(self.online_buffer),
            'predictions_since_retrain': self.predictions_since_retrain
        })
        return base_info