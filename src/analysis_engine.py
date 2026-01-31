"""
Fraud Analysis Engine
Combines all detection algorithms and generates comprehensive fraud scores
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from src.transaction import Transaction, TransactionHistory, MerchantCategory, TransactionType
from src.fraud_detection import (
    AnomalyDetector, 
    VelocityChecker, 
    GeographicAnalyzer,
    BehavioralAnalyzer
)


@dataclass
class FraudAnalysisResult:
    """Result of fraud analysis for a transaction"""
    transaction_id: str
    cardholder_id: str
    fraud_score: float  # 0.0 to 1.0
    risk_level: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    fraud_indicators: Dict[str, Tuple[bool, float]]  # {indicator_name: (triggered, confidence)}
    recommendation: str
    details: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        indicators = {
            name: {"triggered": triggered, "confidence": confidence}
            for name, (triggered, confidence) in self.fraud_indicators.items()
        }
        return {
            "transaction_id": self.transaction_id,
            "cardholder_id": self.cardholder_id,
            "fraud_score": self.fraud_score,
            "risk_level": self.risk_level,
            "fraud_indicators": indicators,
            "recommendation": self.recommendation,
            "details": self.details
        }


class FraudAnalysisEngine:
    """Main engine for comprehensive fraud detection"""
    
    # Weights for different detection methods
    WEIGHTS = {
        "amount_anomaly": 0.20,
        "time_anomaly": 0.10,
        "rapid_transactions": 0.25,
        "high_frequency_day": 0.15,
        "impossible_travel": 0.30,
        "country_shift": 0.20,
        "category_deviation": 0.10,
        "new_merchant": 0.15
    }
    
    # Risk thresholds
    RISK_THRESHOLDS = {
        "LOW": 0.3,
        "MEDIUM": 0.5,
        "HIGH": 0.7,
        "CRITICAL": 0.85
    }
    
    def __init__(self, history: TransactionHistory):
        self.history = history
        self.anomaly_detector = AnomalyDetector(history)
        self.velocity_checker = VelocityChecker(history)
        self.geographic_analyzer = GeographicAnalyzer(history)
        self.behavioral_analyzer = BehavioralAnalyzer(history)
    
    def analyze_transaction(
        self,
        transaction: Transaction
    ) -> FraudAnalysisResult:
        """
        Perform comprehensive fraud analysis on a transaction
        """
        indicators = {}
        weighted_scores = []
        
        # 1. Amount Anomaly Detection
        is_anomalous, confidence = self.anomaly_detector.detect_amount_anomaly(
            transaction.cardholder_id, 
            transaction.amount
        )
        indicators["amount_anomaly"] = (is_anomalous, confidence)
        weighted_scores.append((confidence, self.WEIGHTS["amount_anomaly"]))
        
        # 2. Time Anomaly Detection
        is_unusual_time, confidence = self.anomaly_detector.detect_time_anomaly(
            transaction.cardholder_id,
            transaction.timestamp
        )
        indicators["time_anomaly"] = (is_unusual_time, confidence)
        weighted_scores.append((confidence, self.WEIGHTS["time_anomaly"]))
        
        # 3. Rapid Transaction Detection
        is_rapid, confidence, count = self.velocity_checker.check_rapid_transactions(
            transaction.cardholder_id
        )
        indicators["rapid_transactions"] = (is_rapid, confidence)
        weighted_scores.append((confidence, self.WEIGHTS["rapid_transactions"]))
        
        # 4. High Frequency Day Detection
        is_high_freq, confidence, daily_count = self.velocity_checker.check_high_frequency_day(
            transaction.cardholder_id,
            transaction.timestamp
        )
        indicators["high_frequency_day"] = (is_high_freq, confidence)
        weighted_scores.append((confidence, self.WEIGHTS["high_frequency_day"]))
        
        # 5. Impossible Travel Detection
        is_impossible, confidence, speed = self.geographic_analyzer.check_impossible_travel(
            transaction.cardholder_id,
            transaction
        )
        indicators["impossible_travel"] = (is_impossible, confidence)
        weighted_scores.append((confidence, self.WEIGHTS["impossible_travel"]))
        
        # 6. Country Shift Detection
        is_new_country, confidence = self.geographic_analyzer.check_country_shift(
            transaction.cardholder_id,
            transaction
        )
        indicators["country_shift"] = (is_new_country, confidence)
        weighted_scores.append((confidence, self.WEIGHTS["country_shift"]))
        
        # 7. Category Deviation Detection
        is_unusual_category, confidence = self.behavioral_analyzer.analyze_category_deviation(
            transaction.cardholder_id,
            transaction
        )
        indicators["category_deviation"] = (is_unusual_category, confidence)
        weighted_scores.append((confidence, self.WEIGHTS["category_deviation"]))
        
        # 8. New Merchant Detection
        is_new_merchant, confidence = self.behavioral_analyzer.check_merchant_pattern(
            transaction.cardholder_id,
            transaction
        )
        indicators["new_merchant"] = (is_new_merchant, confidence)
        weighted_scores.append((confidence, self.WEIGHTS["new_merchant"]))
        
        # Calculate weighted fraud score
        fraud_score = self._calculate_weighted_score(weighted_scores)
        
        # Determine risk level
        risk_level = self._determine_risk_level(fraud_score)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(risk_level, indicators)
        
        # Compile details
        details = {
            "transaction_amount": transaction.amount,
            "merchant_name": transaction.merchant_name,
            "merchant_category": transaction.merchant_category.value,
            "transaction_type": transaction.transaction_type.value,
            "country": transaction.country,
            "timestamp": transaction.timestamp.isoformat(),
            "rapid_tx_count": count,
            "daily_tx_count": daily_count,
            "impossible_travel_speed": speed
        }
        
        return FraudAnalysisResult(
            transaction_id=transaction.transaction_id,
            cardholder_id=transaction.cardholder_id,
            fraud_score=fraud_score,
            risk_level=risk_level,
            fraud_indicators=indicators,
            recommendation=recommendation,
            details=details
        )
    
    @staticmethod
    def _calculate_weighted_score(weighted_scores: List[Tuple[float, float]]) -> float:
        """Calculate weighted average fraud score"""
        if not weighted_scores:
            return 0.0
        
        total_weight = sum(weight for _, weight in weighted_scores)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(score * weight for score, weight in weighted_scores)
        return weighted_sum / total_weight
    
    def _determine_risk_level(self, fraud_score: float) -> str:
        """Determine risk level based on fraud score"""
        if fraud_score >= self.RISK_THRESHOLDS["CRITICAL"]:
            return "CRITICAL"
        elif fraud_score >= self.RISK_THRESHOLDS["HIGH"]:
            return "HIGH"
        elif fraud_score >= self.RISK_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"
    
    @staticmethod
    def _generate_recommendation(risk_level: str, indicators: Dict) -> str:
        """Generate recommendation based on risk level and indicators"""
        triggered_indicators = [
            name for name, (triggered, _) in indicators.items() if triggered
        ]
        
        if risk_level == "CRITICAL":
            return "BLOCK_TRANSACTION - Multiple high-risk indicators detected"
        elif risk_level == "HIGH":
            if indicators.get("impossible_travel", (False, 0))[0]:
                return "REQUIRE_VERIFICATION - Impossible travel detected"
            elif indicators.get("rapid_transactions", (False, 0))[0]:
                return "REQUIRE_VERIFICATION - Unusual transaction velocity"
            else:
                return "REVIEW_TRANSACTION - High fraud risk"
        elif risk_level == "MEDIUM":
            return "MONITOR_TRANSACTION - Multiple moderate risk factors"
        else:
            return "APPROVE_TRANSACTION - Low fraud risk"
    
    def batch_analyze(
        self,
        transactions: List[Transaction]
    ) -> List[FraudAnalysisResult]:
        """Analyze multiple transactions"""
        return [self.analyze_transaction(tx) for tx in transactions]
    
    def generate_summary_report(
        self,
        results: List[FraudAnalysisResult]
    ) -> Dict:
        """Generate summary report from analysis results"""
        high_risk_count = sum(1 for r in results if r.risk_level in ["HIGH", "CRITICAL"])
        medium_risk_count = sum(1 for r in results if r.risk_level == "MEDIUM")
        
        # Count indicator triggers
        indicator_counts = {}
        for result in results:
            for indicator, (triggered, _) in result.fraud_indicators.items():
                if triggered:
                    indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1
        
        return {
            "total_transactions": len(results),
            "high_risk_transactions": high_risk_count,
            "medium_risk_transactions": medium_risk_count,
            "average_fraud_score": sum(r.fraud_score for r in results) / len(results) if results else 0,
            "top_fraud_indicators": sorted(
                indicator_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "estimated_fraud_transactions": high_risk_count + int(medium_risk_count * 0.5)
        }
