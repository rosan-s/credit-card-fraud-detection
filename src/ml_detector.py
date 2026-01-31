"""
Machine Learning Module for Fraud Detection
Implements ML models for improved fraud detection accuracy
"""

import json
import pickle
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import random
from src.transaction import Transaction, TransactionHistory, MerchantCategory, TransactionType
from src.fraud_detection import (
    AnomalyDetector,
    VelocityChecker,
    GeographicAnalyzer,
    BehavioralAnalyzer
)


@dataclass
class TransactionFeatures:
    """Features extracted from a transaction for ML"""
    amount: float
    hour_of_day: int
    day_of_week: int
    is_weekend: bool
    amount_zscore: float
    days_since_last_transaction: float
    transactions_today: int
    transactions_this_week: int
    is_new_merchant: bool
    is_new_category: bool
    impossible_travel_score: float
    new_country: bool
    category_frequency: float
    merchant_frequency: float
    rapid_transaction_count: int
    
    def to_list(self) -> List[float]:
        """Convert to list for ML model"""
        return [
            self.amount,
            self.hour_of_day,
            self.day_of_week,
            float(self.is_weekend),
            self.amount_zscore,
            self.days_since_last_transaction,
            float(self.transactions_today),
            float(self.transactions_this_week),
            float(self.is_new_merchant),
            float(self.is_new_category),
            self.impossible_travel_score,
            float(self.new_country),
            self.category_frequency,
            self.merchant_frequency,
            float(self.rapid_transaction_count),
        ]


class FeatureEngineer:
    """Extracts features from transactions for ML models"""
    
    def __init__(self, history: TransactionHistory):
        self.history = history
        self.anomaly_detector = AnomalyDetector(history)
        self.velocity_checker = VelocityChecker(history)
        self.geographic_analyzer = GeographicAnalyzer(history)
        self.behavioral_analyzer = BehavioralAnalyzer(history)
    
    def extract_features(
        self,
        transaction: Transaction
    ) -> TransactionFeatures:
        """Extract ML features from a transaction"""
        
        cardholder_id = transaction.cardholder_id
        cardholder_txs = self.history.get_transactions_by_cardholder(cardholder_id)
        
        # Amount features
        amounts = [t.amount for t in cardholder_txs]
        if amounts:
            avg_amount = sum(amounts) / len(amounts)
            amount_zscore = (transaction.amount - avg_amount) / (max(1, avg_amount * 0.5))
        else:
            amount_zscore = 0.0
        
        # Time features
        hour_of_day = transaction.timestamp.hour
        day_of_week = transaction.timestamp.weekday()
        is_weekend = day_of_week >= 5
        
        # Days since last transaction
        if cardholder_txs:
            last_tx = max(cardholder_txs, key=lambda t: t.timestamp)
            days_since = (transaction.timestamp - last_tx.timestamp).days
        else:
            days_since = 0.0
        
        # Transactions today
        today_txs = [
            t for t in cardholder_txs
            if t.timestamp.date() == transaction.timestamp.date()
        ]
        transactions_today = len(today_txs)
        
        # Transactions this week
        week_ago = transaction.timestamp - timedelta(days=7)
        week_txs = [
            t for t in cardholder_txs
            if t.timestamp >= week_ago
        ]
        transactions_this_week = len(week_txs)
        
        # Merchant features
        known_merchants = {t.merchant_name for t in cardholder_txs}
        is_new_merchant = transaction.merchant_name not in known_merchants
        
        merchant_count = sum(
            1 for t in cardholder_txs
            if t.merchant_name == transaction.merchant_name
        )
        merchant_frequency = merchant_count / max(1, len(cardholder_txs))
        
        # Category features
        known_categories = {t.merchant_category for t in cardholder_txs}
        is_new_category = transaction.merchant_category not in known_categories
        
        category_count = sum(
            1 for t in cardholder_txs
            if t.merchant_category == transaction.merchant_category
        )
        category_frequency = category_count / max(1, len(cardholder_txs))
        
        # Geographic features
        is_impossible, impossible_score, _ = self.geographic_analyzer.check_impossible_travel(
            cardholder_id, transaction
        )
        
        known_countries = {t.country for t in cardholder_txs}
        new_country = transaction.country not in known_countries
        
        # Velocity features
        is_rapid, rapid_score, rapid_count = self.velocity_checker.check_rapid_transactions(
            cardholder_id
        )
        
        return TransactionFeatures(
            amount=transaction.amount,
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            amount_zscore=amount_zscore,
            days_since_last_transaction=float(days_since),
            transactions_today=transactions_today,
            transactions_this_week=transactions_this_week,
            is_new_merchant=is_new_merchant,
            is_new_category=is_new_category,
            impossible_travel_score=impossible_score,
            new_country=new_country,
            category_frequency=category_frequency,
            merchant_frequency=merchant_frequency,
            rapid_transaction_count=rapid_count
        )


class SimpleFraudClassifier:
    """Simple ML classifier for fraud detection (no external libraries)"""
    
    def __init__(self):
        self.weights = None
        self.bias = 0.0
        self.is_trained = False
    
    def sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        if x > 500:
            return 1.0
        if x < -500:
            return 0.0
        return 1.0 / (1.0 + (2.718281828 ** -x))
    
    def train(
        self,
        features_list: List[List[float]],
        labels: List[int],
        learning_rate: float = 0.01,
        epochs: int = 100
    ) -> Dict:
        """Train logistic regression model"""
        
        if not features_list or not labels:
            return {"error": "No training data"}
        
        num_features = len(features_list[0])
        self.weights = [0.0] * num_features
        self.bias = 0.0
        
        training_history = []
        
        for epoch in range(epochs):
            total_loss = 0.0
            
            for features, label in zip(features_list, labels):
                # Forward pass
                z = self.bias + sum(w * f for w, f in zip(self.weights, features))
                prediction = self.sigmoid(z)
                
                # Calculate loss
                loss = -((label * (prediction + 1e-10)) + 
                        (1 - label) * (1 - prediction + 1e-10))
                total_loss += loss
                
                # Backward pass
                error = prediction - label
                self.bias -= learning_rate * error
                for i in range(num_features):
                    self.weights[i] -= learning_rate * error * features[i]
            
            avg_loss = total_loss / len(features_list)
            training_history.append(avg_loss)
            
            # Early stopping if converged
            if epoch > 10 and abs(training_history[-1] - training_history[-10]) < 0.001:
                break
        
        self.is_trained = True
        return {
            "epochs_trained": epoch + 1,
            "final_loss": avg_loss,
            "converged": True
        }
    
    def predict(self, features: List[float]) -> float:
        """Predict fraud probability (0-1)"""
        if not self.is_trained or self.weights is None:
            return 0.5
        
        z = self.bias + sum(w * f for w, f in zip(self.weights, features))
        return self.sigmoid(z)
    
    def predict_batch(self, features_list: List[List[float]]) -> List[float]:
        """Predict on multiple samples"""
        return [self.predict(features) for features in features_list]


class RandomForestClassifier:
    """Simple random forest implementation (no external libraries)"""
    
    def __init__(self, num_trees: int = 10, max_depth: int = 5):
        self.num_trees = num_trees
        self.max_depth = max_depth
        self.trees = []
    
    def train(
        self,
        features_list: List[List[float]],
        labels: List[int]
    ) -> Dict:
        """Train random forest"""
        
        for _ in range(self.num_trees):
            # Bootstrap sampling
            sample_indices = [
                random.randint(0, len(features_list) - 1)
                for _ in range(len(features_list))
            ]
            
            sampled_features = [features_list[i] for i in sample_indices]
            sampled_labels = [labels[i] for i in sample_indices]
            
            # Build decision tree
            tree = self._build_tree(sampled_features, sampled_labels, depth=0)
            self.trees.append(tree)
        
        return {"num_trees": len(self.trees), "status": "trained"}
    
    def _build_tree(
        self,
        features_list: List[List[float]],
        labels: List[int],
        depth: int
    ) -> Dict:
        """Recursively build decision tree"""
        
        if depth >= self.max_depth or len(set(labels)) == 1 or not features_list:
            majority_class = 1 if sum(labels) > len(labels) / 2 else 0
            return {"type": "leaf", "prediction": majority_class}
        
        best_feature = None
        best_threshold = None
        best_gain = 0.0
        
        # Try random features
        num_features = len(features_list[0])
        for feature_idx in range(min(3, num_features)):  # Try 3 random features
            
            feature_values = [f[feature_idx] for f in features_list]
            threshold = sum(feature_values) / len(feature_values)
            
            # Split
            left_labels = [
                labels[i] for i in range(len(features_list))
                if features_list[i][feature_idx] <= threshold
            ]
            right_labels = [
                labels[i] for i in range(len(features_list))
                if features_list[i][feature_idx] > threshold
            ]
            
            if not left_labels or not right_labels:
                continue
            
            # Information gain
            gain = self._information_gain(labels, left_labels, right_labels)
            
            if gain > best_gain:
                best_gain = gain
                best_feature = feature_idx
                best_threshold = threshold
        
        if best_feature is None:
            majority_class = 1 if sum(labels) > len(labels) / 2 else 0
            return {"type": "leaf", "prediction": majority_class}
        
        # Split data
        left_features, left_labels, right_features, right_labels = [], [], [], []
        for features, label in zip(features_list, labels):
            if features[best_feature] <= best_threshold:
                left_features.append(features)
                left_labels.append(label)
            else:
                right_features.append(features)
                right_labels.append(label)
        
        return {
            "type": "node",
            "feature": best_feature,
            "threshold": best_threshold,
            "left": self._build_tree(left_features, left_labels, depth + 1),
            "right": self._build_tree(right_features, right_labels, depth + 1)
        }
    
    @staticmethod
    def _information_gain(parent_labels, left_labels, right_labels) -> float:
        """Calculate information gain"""
        parent_entropy = SimpleFraudClassifier._entropy(parent_labels)
        left_entropy = SimpleFraudClassifier._entropy(left_labels)
        right_entropy = SimpleFraudClassifier._entropy(right_labels)
        
        left_weight = len(left_labels) / len(parent_labels)
        right_weight = len(right_labels) / len(parent_labels)
        
        return parent_entropy - (left_weight * left_entropy + right_weight * right_entropy)
    
    @staticmethod
    def _entropy(labels: List[int]) -> float:
        """Calculate entropy"""
        if not labels:
            return 0.0
        pos = sum(labels)
        neg = len(labels) - pos
        total = len(labels)
        
        if pos == 0 or neg == 0:
            return 0.0
        
        p_pos = pos / total
        p_neg = neg / total
        
        return -(p_pos * (p_pos + 1e-10) + p_neg * (p_neg + 1e-10))
    
    def predict(self, features: List[float]) -> float:
        """Predict fraud probability"""
        predictions = []
        
        for tree in self.trees:
            pred = self._traverse_tree(tree, features)
            predictions.append(pred)
        
        return sum(predictions) / len(predictions) if predictions else 0.5
    
    def _traverse_tree(self, tree: Dict, features: List[float]) -> float:
        """Traverse tree for prediction"""
        if tree["type"] == "leaf":
            return float(tree["prediction"])
        
        if features[tree["feature"]] <= tree["threshold"]:
            return self._traverse_tree(tree["left"], features)
        else:
            return self._traverse_tree(tree["right"], features)


class MLFraudDetector:
    """ML-based fraud detector using trained models"""
    
    def __init__(self, history: TransactionHistory):
        self.history = history
        self.feature_engineer = FeatureEngineer(history)
        self.logistic_model = SimpleFraudClassifier()
        self.forest_model = RandomForestClassifier(num_trees=10)
        self.is_trained = False
    
    def train_models(
        self,
        training_transactions: List[Tuple[Transaction, int]],
        verbose: bool = True
    ) -> Dict:
        """Train ML models on labeled transactions"""
        
        if verbose:
            print(f"Training on {len(training_transactions)} transactions...")
        
        features_list = []
        labels = []
        
        for transaction, label in training_transactions:
            features = self.feature_engineer.extract_features(transaction)
            features_list.append(features.to_list())
            labels.append(label)
        
        # Train logistic regression
        log_results = self.logistic_model.train(features_list, labels)
        if verbose:
            print(f"Logistic Regression: {log_results}")
        
        # Train random forest
        forest_results = self.forest_model.train(features_list, labels)
        if verbose:
            print(f"Random Forest: {forest_results}")
        
        self.is_trained = True
        
        return {
            "logistic_regression": log_results,
            "random_forest": forest_results,
            "total_samples": len(training_transactions)
        }
    
    def predict_fraud_probability(self, transaction: Transaction) -> Dict:
        """Predict fraud probability using ML models"""
        
        if not self.is_trained:
            return {"error": "Models not trained"}
        
        features = self.feature_engineer.extract_features(transaction)
        features_list = features.to_list()
        
        # Get predictions from both models
        logistic_prob = self.logistic_model.predict(features_list)
        forest_prob = self.forest_model.predict(features_list)
        
        # Ensemble prediction (average)
        ensemble_prob = (logistic_prob + forest_prob) / 2.0
        
        # Classify
        if ensemble_prob > 0.7:
            risk_level = "CRITICAL"
        elif ensemble_prob > 0.5:
            risk_level = "HIGH"
        elif ensemble_prob > 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "transaction_id": transaction.transaction_id,
            "logistic_regression_score": logistic_prob,
            "random_forest_score": forest_prob,
            "ensemble_score": ensemble_prob,
            "risk_level": risk_level,
            "features": {
                "amount": features.amount,
                "hour_of_day": features.hour_of_day,
                "is_new_merchant": features.is_new_merchant,
                "impossible_travel_score": features.impossible_travel_score
            }
        }
    
    def save_models(self, filepath: str) -> bool:
        """Save trained models to file"""
        try:
            model_data = {
                "logistic": {
                    "weights": self.logistic_model.weights,
                    "bias": self.logistic_model.bias
                },
                "forest": {
                    "trees": self.forest_model.trees
                },
                "timestamp": datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving models: {e}")
            return False
    
    def load_models(self, filepath: str) -> bool:
        """Load trained models from file"""
        try:
            with open(filepath, 'r') as f:
                model_data = json.load(f)
            
            self.logistic_model.weights = model_data["logistic"]["weights"]
            self.logistic_model.bias = model_data["logistic"]["bias"]
            self.logistic_model.is_trained = True
            
            self.forest_model.trees = model_data["forest"]["trees"]
            self.is_trained = True
            
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
