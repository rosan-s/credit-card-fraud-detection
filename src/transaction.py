"""
Transaction Data Module
Handles transaction data structure, validation, and management
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class TransactionType(Enum):
    """Types of transactions"""
    PURCHASE = "purchase"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    ONLINE = "online"
    INTERNATIONAL = "international"


class MerchantCategory(Enum):
    """Merchant categories for classification"""
    GROCERY = "grocery"
    RESTAURANT = "restaurant"
    RETAIL = "retail"
    GAS = "gas"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    TRAVEL = "travel"
    ONLINE_RETAIL = "online_retail"
    CASH_ADVANCE = "cash_advance"
    OTHER = "other"


@dataclass
class Transaction:
    """Represents a single transaction"""
    transaction_id: str
    cardholder_id: str
    amount: float
    timestamp: datetime
    merchant_name: str
    merchant_category: MerchantCategory
    transaction_type: TransactionType
    location: Dict[str, float]  # {'latitude': float, 'longitude': float}
    mcc_code: str  # Merchant Category Code
    country: str
    is_fraud: bool = False
    
    def to_dict(self) -> Dict:
        """Convert transaction to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['merchant_category'] = self.merchant_category.value
        data['transaction_type'] = self.transaction_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        """Create transaction from dictionary"""
        data_copy = data.copy()
        data_copy['timestamp'] = datetime.fromisoformat(data_copy['timestamp'])
        data_copy['merchant_category'] = MerchantCategory(data_copy['merchant_category'])
        data_copy['transaction_type'] = TransactionType(data_copy['transaction_type'])
        return cls(**data_copy)


class TransactionHistory:
    """Manages transaction history for analysis"""
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self._index_by_cardholder: Dict[str, List[Transaction]] = {}
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to history"""
        self.transactions.append(transaction)
        
        # Update cardholder index
        if transaction.cardholder_id not in self._index_by_cardholder:
            self._index_by_cardholder[transaction.cardholder_id] = []
        self._index_by_cardholder[transaction.cardholder_id].append(transaction)
    
    def get_transactions_by_cardholder(self, cardholder_id: str) -> List[Transaction]:
        """Get all transactions for a specific cardholder"""
        return self._index_by_cardholder.get(cardholder_id, [])
    
    def get_transactions_in_timeframe(
        self, 
        cardholder_id: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Transaction]:
        """Get transactions within a specific timeframe"""
        cardholder_transactions = self.get_transactions_by_cardholder(cardholder_id)
        return [
            t for t in cardholder_transactions 
            if start_time <= t.timestamp <= end_time
        ]
    
    def get_total_amount_by_cardholder(self, cardholder_id: str) -> float:
        """Get total transaction amount for a cardholder"""
        return sum(
            t.amount for t in self.get_transactions_by_cardholder(cardholder_id)
        )
    
    def get_fraud_transactions(self) -> List[Transaction]:
        """Get all marked fraud transactions"""
        return [t for t in self.transactions if t.is_fraud]
    
    def mark_fraud(self, transaction_id: str) -> bool:
        """Mark a transaction as fraudulent"""
        for transaction in self.transactions:
            if transaction.transaction_id == transaction_id:
                transaction.is_fraud = True
                return True
        return False
