"""
Ensemble Model with Stacking and Blending
Advanced ensemble methods for combining multiple ML models
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from sklearn.ensemble import VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import lightgbm as lgb
import joblib
from datetime import datetime

from .async_base_model import AsyncBaseAIModel


class EnsembleModel(AsyncBaseAIModel):
    """
    Advanced ensemble model combining multiple ML algorithms
    
    Features:
    - Stacking with meta-learner
    - Voting ensemble
    - Dynamic weight adjustment
    - Model diversity optimization
    - Cross-validation based selection
    """
    
    def __init__(self, model_name: str = "ensemble-ml"):
        super().__init__(model_name)
        
        # Base models
        self.base_models = {}
        self.meta_learner = None
        self.stacking_model = None
        self.voting_model = None
        
        # Scalers
        self.feature_scaler = StandardScaler()
        self.is_trained = False
        
        # Ensemble configuration
        self.use_stacking = True
        self.use_voting = True
        self.cv_folds = 5
        
        # Feature engineering
        self.feature_names = [
            'rsi_14', 'rsi_7', 'macd_value', 'macd_signal', 'macd_histogram',
            'bb_position', 'stochastic_k', 'stochastic_d', 'adx', 'cci',
            'williams_r', 'atr', 'price_change_pct', 'volatility_value',
            'trend_encoded', 'volume_ratio', 'support_distance', 'resistance_distance',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos'
        ]
        
        self._initialize_base_models()

    def _initialize_base_models(self):
        """Initialize base models for ensemble"""
        self.base_models = {
            'xgboost': xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                eval_metric='logloss'
            ),
            'lightgbm': lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                verbose=-1
            ),
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'svm': SVC(
                kernel='rbf',
                probability=True,
                random_state=42
            )
        }
        
        # Meta-learner for stacking
        self.meta_learner = LogisticRegression(
            random_state=42,
            max_iter=1000
        )

    def engineer_features(self, market_data: Dict) -> np.ndarray:
        """Engineer features from market data"""
        features = []
        
        # Technical indicators (normalized)
        features.extend([
            market_data.get('rsi_14', 50) / 100,
            market_data.get('rsi_7', 50) / 100,
            market_data.get('macd', {}).get('macd', 0),
            market_data.get('macd', {}).get('signal', 0),
            market_data.get('macd', {}).get('histogram', 0),
            market_data.get('bb_position', 0.5),
            market_data.get('stochastic', {}).get('k', 50) / 100,
            market_data.get('stochastic', {}).get('d', 50) / 100,
            market_data.get('adx', 0) / 100,
            market_data.get('cci', 0) / 200,
            market_data.get('williams_r', -50) / -100,
            market_data.get('atr', 0)
        ])
        
        # Price and volatility features
        features.extend([
            market_data.get('price_change_pct', 0),
            market_data.get('volatility_value', 0)
        ])
        
        # Trend encoding
        trend_map = {'uptrend': 1, 'downtrend': -1, 'sideways': 0}
        trend_encoded = trend_map.get(market_data.get('trend', 'sideways'), 0)
        features.append(trend_encoded)
        
        # Volume analysis
        volume_ma = market_data.get('volume_ma', 1)
        current_volume = market_data.get('volume', volume_ma)
        volume_ratio = current_volume / volume_ma if volume_ma > 0 else 1
        features.append(volume_ratio)
        
        # Support/Resistance distances
        current_price = market_data.get('current_price', 0)
        support = market_data.get('support', current_price)
        resistance = market_data.get('resistance', current_price)
        
        support_distance = (current_price - support) / current_price if current_price > 0 else 0
        resistance_distance = (resistance - current_price) / current_price if current_price > 0 else 0
        
        features.extend([support_distance, resistance_distance])
        
        # Time features (cyclical encoding)
        hour = market_data.get('hour', 12)
        day_of_week = market_data.get('day_of_week', 0)
        
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        day_sin = np.sin(2 * np.pi * day_of_week / 7)
        day_cos = np.cos(2 * np.pi * day_of_week / 7)
        
        features.extend([hour_sin, hour_cos, day_sin, day_cos])
        
        return np.array(features)

    def prepare_training_data(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from market data"""
        X, y = [], []
        
        for i in range(len(data) - 1):  # Exclude last item (no future price)
            # Features from current data
            features = self.engineer_features(data[i])
            X.append(features)
            
            # Target from next data point
            current_price = data[i].get('current_price', data[i].get('close', 0))
            next_price = data[i + 1].get('current_price', data[i + 1].get('close', 0))
            
            if next_price > current_price * 1.0001:  # 0.01% threshold
                target = 1  # UP/CALL
            elif next_price < current_price * 0.9999:
                target = 0  # DOWN/PUT
            else:
                target = 2  # NEUTRAL
            
            y.append(target)
        
        return np.array(X), np.array(y)

    def train(self, training_data: List[Dict], validation_data: List[Dict] = None):
        """Train the ensemble model"""
        print(f"🚀 Training ensemble model with {len(training_data)} samples...")
        
        # Prepare training data
        X_train, y_train = self.prepare_training_data(training_data)
        
        if len(X_train) == 0:
            raise ValueError("No training data generated")
        
        # Scale features
        X_train_scaled = self.feature_scaler.fit_transform(X_train)
        
        # Prepare validation data
        X_val_scaled, y_val = None, None
        if validation_data:
            X_val, y_val = self.prepare_training_data(validation_data)
            X_val_scaled = self.feature_scaler.transform(X_val)
        
        # Train individual base models
        print("📊 Training base models...")
        base_model_scores = {}
        
        for name, model in self.base_models.items():
            print(f"   Training {name}...")
            
            try:
                # Cross-validation score
                cv_scores = cross_val_score(
                    model, X_train_scaled, y_train,
                    cv=StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=42),
                    scoring='accuracy'
                )
                base_model_scores[name] = cv_scores.mean()
                
                # Train on full dataset
                model.fit(X_train_scaled, y_train)
                
                print(f"   ✅ {name}: CV Score = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
                
            except Exception as e:
                print(f"   ❌ {name} failed: {e}")
                # Remove failed model
                del self.base_models[name]
        
        # Select best models for ensemble
        sorted_models = sorted(base_model_scores.items(), key=lambda x: x[1], reverse=True)
        best_models = dict(sorted_models[:4])  # Top 4 models
        
        print(f"📈 Selected models: {list(best_models.keys())}")
        
        # Create stacking ensemble
        if self.use_stacking and len(best_models) >= 2:
            estimators = [(name, self.base_models[name]) for name in best_models.keys()]
            
            self.stacking_model = StackingClassifier(
                estimators=estimators,
                final_estimator=self.meta_learner,
                cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
                n_jobs=-1
            )
            
            print("🔗 Training stacking ensemble...")
            self.stacking_model.fit(X_train_scaled, y_train)
            
            # Evaluate stacking model
            if X_val_scaled is not None:
                stacking_score = self.stacking_model.score(X_val_scaled, y_val)
                print(f"   ✅ Stacking validation score: {stacking_score:.3f}")
        
        # Create voting ensemble
        if self.use_voting and len(best_models) >= 2:
            estimators = [(name, self.base_models[name]) for name in best_models.keys()]
            
            self.voting_model = VotingClassifier(
                estimators=estimators,
                voting='soft',  # Use probabilities
                n_jobs=-1
            )
            
            print("🗳️ Training voting ensemble...")
            self.voting_model.fit(X_train_scaled, y_train)
            
            # Evaluate voting model
            if X_val_scaled is not None:
                voting_score = self.voting_model.score(X_val_scaled, y_val)
                print(f"   ✅ Voting validation score: {voting_score:.3f}")
        
        self.is_trained = True
        print("✅ Ensemble training completed")
        
        return {
            'base_model_scores': base_model_scores,
            'selected_models': list(best_models.keys()),
            'stacking_trained': self.stacking_model is not None,
            'voting_trained': self.voting_model is not None
        }

    async def predict_async(self, market_data: Dict) -> Dict:
        """Generate trading signal using ensemble model"""
        if not self.is_trained:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reasoning': 'Ensemble model not trained yet',
                'feature_importance': {}
            }
        
        try:
            # Engineer features
            features = self.engineer_features(market_data)
            X = features.reshape(1, -1)
            X_scaled = self.feature_scaler.transform(X)
            
            predictions = {}
            probabilities = {}
            
            # Get predictions from individual models
            for name, model in self.base_models.items():
                try:
                    pred_proba = model.predict_proba(X_scaled)[0]
                    pred_class = model.predict(X_scaled)[0]
                    
                    predictions[name] = pred_class
                    probabilities[name] = pred_proba
                except Exception as e:
                    print(f"⚠️ {name} prediction failed: {e}")
            
            # Get ensemble predictions
            ensemble_predictions = {}
            
            if self.stacking_model:
                stacking_proba = self.stacking_model.predict_proba(X_scaled)[0]
                stacking_pred = self.stacking_model.predict(X_scaled)[0]
                ensemble_predictions['stacking'] = {
                    'prediction': stacking_pred,
                    'probabilities': stacking_proba
                }
            
            if self.voting_model:
                voting_proba = self.voting_model.predict_proba(X_scaled)[0]
                voting_pred = self.voting_model.predict(X_scaled)[0]
                ensemble_predictions['voting'] = {
                    'prediction': voting_pred,
                    'probabilities': voting_proba
                }
            
            # Determine final prediction (prefer stacking if available)
            if 'stacking' in ensemble_predictions:
                final_pred = ensemble_predictions['stacking']['prediction']
                final_proba = ensemble_predictions['stacking']['probabilities']
                method = 'stacking'
            elif 'voting' in ensemble_predictions:
                final_pred = ensemble_predictions['voting']['prediction']
                final_proba = ensemble_predictions['voting']['probabilities']
                method = 'voting'
            else:
                # Fallback to majority vote of base models
                pred_counts = {0: 0, 1: 0, 2: 0}
                for pred in predictions.values():
                    pred_counts[pred] += 1
                
                final_pred = max(pred_counts, key=pred_counts.get)
                final_proba = [0.33, 0.33, 0.34]  # Default probabilities
                method = 'majority_vote'
            
            # Convert to trading signal
            if final_pred == 1:  # UP
                signal = 'CALL'
                confidence = final_proba[1] * 100
            elif final_pred == 0:  # DOWN
                signal = 'PUT'
                confidence = final_proba[0] * 100
            else:  # NEUTRAL
                signal = 'NEUTRAL'
                confidence = final_proba[2] * 100
            
            # Feature importance (from best performing model)
            feature_importance = {}
            if self.base_models:
                best_model_name = max(predictions.keys(), 
                                    key=lambda x: max(probabilities[x]) if x in probabilities else 0)
                best_model = self.base_models[best_model_name]
                
                if hasattr(best_model, 'feature_importances_'):
                    importances = best_model.feature_importances_
                    for i, importance in enumerate(importances):
                        if i < len(self.feature_names):
                            feature_importance[self.feature_names[i]] = float(importance)
            
            reasoning_parts = [f"{method} ensemble prediction"]
            if predictions:
                model_votes = [f"{name}:{pred}" for name, pred in predictions.items()]
                reasoning_parts.append(f"Base models: {', '.join(model_votes)}")
            
            return {
                'signal': signal,
                'confidence': int(confidence),
                'reasoning': ' | '.join(reasoning_parts),
                'feature_importance': feature_importance,
                'ensemble_details': {
                    'method': method,
                    'base_predictions': predictions,
                    'ensemble_predictions': ensemble_predictions,
                    'final_probabilities': final_proba.tolist() if hasattr(final_proba, 'tolist') else final_proba
                }
            }
            
        except Exception as e:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reasoning': f'Ensemble prediction error: {str(e)}',
                'feature_importance': {}
            }

    def get_model_diversity(self) -> Dict:
        """Calculate diversity metrics for ensemble models"""
        if not self.is_trained or not self.base_models:
            return {}
        
        # This would require validation data to calculate properly
        # For now, return basic diversity info
        return {
            'num_base_models': len(self.base_models),
            'model_types': list(self.base_models.keys()),
            'has_stacking': self.stacking_model is not None,
            'has_voting': self.voting_model is not None
        }

    def save_model(self, filepath: str):
        """Save the ensemble model"""
        if self.is_trained:
            # Save base models
            for name, model in self.base_models.items():
                joblib.dump(model, f"{filepath}_{name}.pkl")
            
            # Save ensemble models
            if self.stacking_model:
                joblib.dump(self.stacking_model, f"{filepath}_stacking.pkl")
            
            if self.voting_model:
                joblib.dump(self.voting_model, f"{filepath}_voting.pkl")
            
            # Save scaler and metadata
            joblib.dump(self.feature_scaler, f"{filepath}_scaler.pkl")
            
            metadata = {
                'feature_names': self.feature_names,
                'is_trained': self.is_trained,
                'base_model_names': list(self.base_models.keys()),
                'has_stacking': self.stacking_model is not None,
                'has_voting': self.voting_model is not None
            }
            joblib.dump(metadata, f"{filepath}_metadata.pkl")
            
            print(f"💾 Ensemble model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load the ensemble model"""
        try:
            # Load metadata
            metadata = joblib.load(f"{filepath}_metadata.pkl")
            self.feature_names = metadata['feature_names']
            self.is_trained = metadata['is_trained']
            
            # Load base models
            self.base_models = {}
            for name in metadata['base_model_names']:
                self.base_models[name] = joblib.load(f"{filepath}_{name}.pkl")
            
            # Load ensemble models
            if metadata['has_stacking']:
                self.stacking_model = joblib.load(f"{filepath}_stacking.pkl")
            
            if metadata['has_voting']:
                self.voting_model = joblib.load(f"{filepath}_voting.pkl")
            
            # Load scaler
            self.feature_scaler = joblib.load(f"{filepath}_scaler.pkl")
            
            print(f"📂 Ensemble model loaded from {filepath}")
            
        except Exception as e:
            print(f"❌ Failed to load ensemble model: {e}")
            self.is_trained = False

    def get_model_info(self) -> Dict:
        """Return enhanced model metadata"""
        base_info = super().get_model_info()
        base_info.update({
            'provider': 'Scikit-learn',
            'model_type': 'Ensemble',
            'base_models': list(self.base_models.keys()) if self.base_models else [],
            'num_features': len(self.feature_names),
            'is_trained': self.is_trained,
            'has_stacking': self.stacking_model is not None,
            'has_voting': self.voting_model is not None
        })
        return base_info