"""
Fraud Detection Algorithms
Implements various pattern analysis techniques for fraud detection
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from statistics import mean, stdev
from src.transaction import Transaction, TransactionHistory


class AnomalyDetector:
    """Detects statistical anomalies in transaction patterns"""
    
    def __init__(self, history: TransactionHistory):
        self.history = history
    
    def detect_amount_anomaly(
        self, 
        cardholder_id: str, 
        transaction_amount: float,
        threshold_std: float = 2.5
    ) -> Tuple[bool, float]:
        """
        Detect if transaction amount is anomalous based on historical average
        Returns (is_anomalous, confidence_score)
        """
        cardholder_transactions = self.history.get_transactions_by_cardholder(cardholder_id)
        
        if len(cardholder_transactions) < 3:
            return False, 0.0  # Not enough data
        
        amounts = [t.amount for t in cardholder_transactions]
        avg_amount = mean(amounts)
        std_dev = stdev(amounts) if len(amounts) > 1 else 0
        
        if std_dev == 0:
            # All amounts are the same
            if abs(transaction_amount - avg_amount) > avg_amount * 0.1:
                return True, 0.7
            return False, 0.0
        
        # Z-score calculation
        z_score = abs((transaction_amount - avg_amount) / std_dev)
        is_anomalous = z_score > threshold_std
        confidence = min(z_score / 3.0, 1.0)  # Normalize to 0-1
        
        return is_anomalous, confidence
    
    def detect_time_anomaly(
        self,
        cardholder_id: str,
        transaction_time: datetime,
        hours_window: int = 24
    ) -> Tuple[bool, float]:
        """
        Detect unusual transaction times based on historical patterns
        Returns (is_anomalous, confidence_score)
        """
        cardholder_transactions = self.history.get_transactions_by_cardholder(cardholder_id)
        
        if len(cardholder_transactions) < 5:
            return False, 0.0
        
        # Get hours of transaction
        transaction_hour = transaction_time.hour
        historical_hours = [t.timestamp.hour for t in cardholder_transactions]
        
        # Calculate frequency distribution
        hour_counts = {}
        for hour in historical_hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Check if transaction hour is typical
        total_transactions = len(cardholder_transactions)
        expected_frequency = hour_counts.get(transaction_hour, 0) / total_transactions
        
        # If transaction hour appears in less than 5% of historical transactions
        is_anomalous = expected_frequency < 0.05
        confidence = 1.0 - expected_frequency if is_anomalous else 0.0
        
        return is_anomalous, confidence


class VelocityChecker:
    """Checks for unusual transaction velocity patterns"""
    
    def __init__(self, history: TransactionHistory):
        self.history = history
    
    def check_rapid_transactions(
        self,
        cardholder_id: str,
        time_window_minutes: int = 10,
        transaction_count_threshold: int = 3
    ) -> Tuple[bool, float, int]:
        """
        Check if too many transactions in short time window
        Returns (is_suspicious, confidence, transaction_count)
        """
        cardholder_transactions = self.history.get_transactions_by_cardholder(cardholder_id)
        
        if len(cardholder_transactions) < 2:
            return False, 0.0, 0
        
        # Get most recent transaction time
        recent_transactions = sorted(
            cardholder_transactions, 
            key=lambda t: t.timestamp, 
            reverse=True
        )[:5]
        
        # Check transactions in window
        window_start = recent_transactions[0].timestamp - timedelta(minutes=time_window_minutes)
        transactions_in_window = [
            t for t in cardholder_transactions
            if window_start <= t.timestamp <= recent_transactions[0].timestamp
        ]
        
        count = len(transactions_in_window)
        is_suspicious = count >= transaction_count_threshold
        confidence = min((count - 2) / transaction_count_threshold, 1.0) if is_suspicious else 0.0
        
        return is_suspicious, confidence, count
    
    def check_high_frequency_day(
        self,
        cardholder_id: str,
        target_date: datetime,
        avg_daily_threshold: float = 2.0
    ) -> Tuple[bool, float, int]:
        """
        Check if transaction frequency unusually high on a specific day
        Returns (is_suspicious, confidence, daily_count)
        """
        cardholder_transactions = self.history.get_transactions_by_cardholder(cardholder_id)
        
        if len(cardholder_transactions) < 5:
            return False, 0.0, 0
        
        # Count transactions per day historically
        daily_counts = {}
        for t in cardholder_transactions:
            day_key = t.timestamp.date()
            daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
        
        avg_daily = mean(daily_counts.values())
        target_day_count = daily_counts.get(target_date.date(), 0)
        
        is_suspicious = target_day_count > avg_daily * avg_daily_threshold
        confidence = min((target_day_count - avg_daily) / avg_daily, 1.0) if is_suspicious else 0.0
        
        return is_suspicious, confidence, target_day_count


class GeographicAnalyzer:
    """Analyzes geographic patterns for fraud detection"""
    
    def __init__(self, history: TransactionHistory):
        self.history = history
    
    @staticmethod
    def calculate_distance(loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two coordinates in kilometers"""
        lat1, lon1 = loc1['latitude'], loc1['longitude']
        lat2, lon2 = loc2['latitude'], loc2['longitude']
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def check_impossible_travel(
        self,
        cardholder_id: str,
        new_transaction: Transaction,
        min_speed_kmh: float = 900  # Commercial flight speed
    ) -> Tuple[bool, float, Optional[float]]:
        """
        Check if transaction is geographically impossible given previous transaction
        Returns (is_impossible, confidence, calculated_speed)
        """
        cardholder_transactions = self.history.get_transactions_by_cardholder(cardholder_id)
        
        if not cardholder_transactions:
            return False, 0.0, None
        
        # Get most recent transaction
        last_transaction = max(cardholder_transactions, key=lambda t: t.timestamp)
        
        # Calculate distance and time difference
        distance = self.calculate_distance(
            last_transaction.location,
            new_transaction.location
        )
        time_diff_hours = (
            new_transaction.timestamp - last_transaction.timestamp
        ).total_seconds() / 3600
        
        if time_diff_hours <= 0:
            return False, 0.0, None
        
        calculated_speed = distance / time_diff_hours
        is_impossible = calculated_speed > min_speed_kmh
        
        # Confidence based on how much it exceeds minimum speed
        confidence = min((calculated_speed - min_speed_kmh) / min_speed_kmh, 1.0) if is_impossible else 0.0
        
        return is_impossible, confidence, calculated_speed
    
    def check_country_shift(
        self,
        cardholder_id: str,
        new_transaction: Transaction
    ) -> Tuple[bool, float]:
        """
        Check if transaction is from unusual country
        Returns (is_unusual, confidence)
        """
        cardholder_transactions = self.history.get_transactions_by_cardholder(cardholder_id)
        
        if len(cardholder_transactions) < 5:
            return False, 0.0
        
        # Count countries in transaction history
        countries = {}
        for t in cardholder_transactions:
            countries[t.country] = countries.get(t.country, 0) + 1
        
        total = sum(countries.values())
        new_country_frequency = countries.get(new_transaction.country, 0) / total
        
        is_unusual = new_country_frequency == 0  # Never transacted from this country
        confidence = 0.6 if is_unusual else 0.0
        
        return is_unusual, confidence


class BehavioralAnalyzer:
    """Analyzes typical behavioral patterns"""
    
    def __init__(self, history: TransactionHistory):
        self.history = history
    
    def analyze_category_deviation(
        self,
        cardholder_id: str,
        new_transaction: Transaction
    ) -> Tuple[bool, float]:
        """
        Check if transaction category is unusual for this cardholder
        Returns (is_unusual, confidence)
        """
        cardholder_transactions = self.history.get_transactions_by_cardholder(cardholder_id)
        
        if len(cardholder_transactions) < 5:
            return False, 0.0
        
        # Count categories
        categories = {}
        for t in cardholder_transactions:
            cat = t.merchant_category.value
            categories[cat] = categories.get(cat, 0) + 1
        
        total = sum(categories.values())
        new_category_frequency = categories.get(new_transaction.merchant_category.value, 0) / total
        
        # If this category appears less than 5% of the time, it's unusual
        is_unusual = new_category_frequency < 0.05
        confidence = 1.0 - new_category_frequency if is_unusual else 0.0
        
        return is_unusual, confidence
    
    def check_merchant_pattern(
        self,
        cardholder_id: str,
        new_transaction: Transaction
    ) -> Tuple[bool, float]:
        """
        Check if merchant is in cardholder's regular merchant list
        Returns (is_new_merchant, confidence)
        """
        cardholder_transactions = self.history.get_transactions_by_cardholder(cardholder_id)
        
        if len(cardholder_transactions) < 3:
            return False, 0.0
        
        # Get set of merchants
        known_merchants = {t.merchant_name for t in cardholder_transactions}
        
        is_new_merchant = new_transaction.merchant_name not in known_merchants
        confidence = 0.3 if is_new_merchant else 0.0
        
        return is_new_merchant, confidence
