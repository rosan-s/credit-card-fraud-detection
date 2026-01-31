"""
Credit Card Fraud Detection Demo
Demonstrates the fraud detection system with sample transactions
"""

import json
from datetime import datetime, timedelta
from src.transaction import (
    Transaction, 
    TransactionHistory, 
    MerchantCategory, 
    TransactionType
)
from src.analysis_engine import FraudAnalysisEngine


def create_sample_transactions() -> TransactionHistory:
    """Create sample transaction history for demonstration"""
    history = TransactionHistory()
    
    base_time = datetime(2025, 1, 1, 10, 0, 0)
    cardholder_id = "CH001"
    
    # Normal transactions (baseline behavior)
    normal_transactions = [
        Transaction(
            transaction_id="TX001",
            cardholder_id=cardholder_id,
            amount=45.99,
            timestamp=base_time,
            merchant_name="Whole Foods Market",
            merchant_category=MerchantCategory.GROCERY,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 37.7749, "longitude": -122.4194},  # San Francisco
            mcc_code="5411",
            country="USA"
        ),
        Transaction(
            transaction_id="TX002",
            cardholder_id=cardholder_id,
            amount=35.50,
            timestamp=base_time + timedelta(days=1),
            merchant_name="Starbucks",
            merchant_category=MerchantCategory.RESTAURANT,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 37.7749, "longitude": -122.4194},
            mcc_code="5814",
            country="USA"
        ),
        Transaction(
            transaction_id="TX003",
            cardholder_id=cardholder_id,
            amount=65.00,
            timestamp=base_time + timedelta(days=2),
            merchant_name="Shell Gas Station",
            merchant_category=MerchantCategory.GAS,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 37.7749, "longitude": -122.4194},
            mcc_code="5542",
            country="USA"
        ),
        Transaction(
            transaction_id="TX004",
            cardholder_id=cardholder_id,
            amount=120.00,
            timestamp=base_time + timedelta(days=3),
            merchant_name="Target",
            merchant_category=MerchantCategory.RETAIL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 37.7749, "longitude": -122.4194},
            mcc_code="5310",
            country="USA"
        ),
        Transaction(
            transaction_id="TX005",
            cardholder_id=cardholder_id,
            amount=55.00,
            timestamp=base_time + timedelta(days=4),
            merchant_name="Italian Restaurant",
            merchant_category=MerchantCategory.RESTAURANT,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 37.7749, "longitude": -122.4194},
            mcc_code="5814",
            country="USA"
        ),
        Transaction(
            transaction_id="TX006",
            cardholder_id=cardholder_id,
            amount=200.00,
            timestamp=base_time + timedelta(days=5),
            merchant_name="Amazon.com",
            merchant_category=MerchantCategory.ONLINE_RETAIL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 37.7749, "longitude": -122.4194},
            mcc_code="5961",
            country="USA"
        ),
    ]
    
    for tx in normal_transactions:
        history.add_transaction(tx)
    
    return history


def demonstrate_fraud_detection():
    """Demonstrate the fraud detection system"""
    print("=" * 80)
    print("CREDIT CARD FRAUD DETECTION SYSTEM - DEMO")
    print("=" * 80)
    print()
    
    # Create sample transaction history
    history = create_sample_transactions()
    print(f"✓ Created baseline transaction history with {len(history.transactions)} transactions")
    print()
    
    # Initialize fraud detection engine
    engine = FraudAnalysisEngine(history)
    print("✓ Fraud Detection Engine initialized")
    print()
    
    # Test Case 1: Unusual Amount
    print("-" * 80)
    print("TEST CASE 1: UNUSUAL TRANSACTION AMOUNT")
    print("-" * 80)
    unusual_amount_tx = Transaction(
        transaction_id="TX_FRAUD_001",
        cardholder_id="CH001",
        amount=5000.00,  # Significantly higher than normal
        timestamp=datetime(2025, 1, 7, 11, 30, 0),
        merchant_name="Best Buy",
        merchant_category=MerchantCategory.RETAIL,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 37.7749, "longitude": -122.4194},
        mcc_code="5310",
        country="USA"
    )
    
    result1 = engine.analyze_transaction(unusual_amount_tx)
    print_analysis_result(result1)
    print()
    
    # Test Case 2: Impossible Travel
    print("-" * 80)
    print("TEST CASE 2: IMPOSSIBLE TRAVEL (Too far, too fast)")
    print("-" * 80)
    impossible_travel_tx = Transaction(
        transaction_id="TX_FRAUD_002",
        cardholder_id="CH001",
        amount=150.00,
        timestamp=datetime(2025, 1, 7, 11, 35, 0),  # 5 minutes after previous
        merchant_name="Harrods",
        merchant_category=MerchantCategory.RETAIL,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 51.5074, "longitude": -0.1278},  # London, UK
        mcc_code="5310",
        country="UK"
    )
    
    result2 = engine.analyze_transaction(impossible_travel_tx)
    print_analysis_result(result2)
    print()
    
    # Test Case 3: Rapid Multiple Transactions
    print("-" * 80)
    print("TEST CASE 3: RAPID TRANSACTION VELOCITY")
    print("-" * 80)
    
    # Add rapid transactions to history
    base_time = datetime(2025, 1, 7, 14, 0, 0)
    for i in range(4):
        rapid_tx = Transaction(
            transaction_id=f"TX_RAPID_{i}",
            cardholder_id="CH001",
            amount=100.00 + i * 10,
            timestamp=base_time + timedelta(minutes=i),
            merchant_name=f"Store {i}",
            merchant_category=MerchantCategory.RETAIL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 37.7749, "longitude": -122.4194},
            mcc_code="5310",
            country="USA"
        )
        history.add_transaction(rapid_tx)
    
    # Analyze the last rapid transaction
    rapid_test_tx = Transaction(
        transaction_id="TX_FRAUD_003",
        cardholder_id="CH001",
        amount=110.00,
        timestamp=base_time + timedelta(minutes=5),
        merchant_name="Store 5",
        merchant_category=MerchantCategory.RETAIL,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 37.7749, "longitude": -122.4194},
        mcc_code="5310",
        country="USA"
    )
    
    result3 = engine.analyze_transaction(rapid_test_tx)
    print_analysis_result(result3)
    print()
    
    # Test Case 4: New Merchant and Category
    print("-" * 80)
    print("TEST CASE 4: NEW MERCHANT & UNUSUAL CATEGORY")
    print("-" * 80)
    new_merchant_tx = Transaction(
        transaction_id="TX_FRAUD_004",
        cardholder_id="CH001",
        amount=800.00,
        timestamp=datetime(2025, 1, 8, 2, 15, 0),  # Unusual time
        merchant_name="Luxury Casino Resort",
        merchant_category=MerchantCategory.ENTERTAINMENT,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 36.1699, "longitude": -115.1398},  # Las Vegas
        mcc_code="7011",
        country="USA"
    )
    
    result4 = engine.analyze_transaction(new_merchant_tx)
    print_analysis_result(result4)
    print()
    
    # Test Case 5: Legitimate Transaction
    print("-" * 80)
    print("TEST CASE 5: LEGITIMATE TRANSACTION")
    print("-" * 80)
    legitimate_tx = Transaction(
        transaction_id="TX_LEGIT_001",
        cardholder_id="CH001",
        amount=42.00,
        timestamp=datetime(2025, 1, 8, 10, 30, 0),
        merchant_name="Starbucks",
        merchant_category=MerchantCategory.RESTAURANT,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 37.7749, "longitude": -122.4194},
        mcc_code="5814",
        country="USA"
    )
    
    result5 = engine.analyze_transaction(legitimate_tx)
    print_analysis_result(result5)
    print()
    
    # Generate Summary Report
    print("=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    all_results = [result1, result2, result3, result4, result5]
    summary = engine.generate_summary_report(all_results)
    
    print(f"Total Transactions Analyzed: {summary['total_transactions']}")
    print(f"High-Risk Transactions: {summary['high_risk_transactions']}")
    print(f"Medium-Risk Transactions: {summary['medium_risk_transactions']}")
    print(f"Average Fraud Score: {summary['average_fraud_score']:.3f}")
    print(f"Estimated Fraud Cases: {summary['estimated_fraud_transactions']}")
    print()
    print("Top Fraud Indicators:")
    for indicator, count in summary['top_fraud_indicators']:
        print(f"  - {indicator}: {count} occurrences")
    print()
    
    # Save results to JSON
    save_results_to_json(all_results)


def print_analysis_result(result):
    """Pretty print analysis result"""
    print(f"Transaction ID: {result.transaction_id}")
    print(f"Cardholder ID: {result.cardholder_id}")
    print(f"Fraud Score: {result.fraud_score:.3f} / 1.000")
    print(f"Risk Level: {result.risk_level}")
    print(f"Recommendation: {result.recommendation}")
    print()
    print("Fraud Indicators:")
    
    triggered_count = 0
    for indicator, (triggered, confidence) in result.fraud_indicators.items():
        status = "✓ TRIGGERED" if triggered else "✗ Not triggered"
        print(f"  • {indicator}: {status} (confidence: {confidence:.2f})")
        if triggered:
            triggered_count += 1
    
    print()
    print(f"Triggered Indicators: {triggered_count}/{len(result.fraud_indicators)}")
    print()
    print("Transaction Details:")
    print(f"  • Amount: ${result.details['transaction_amount']:.2f}")
    print(f"  • Merchant: {result.details['merchant_name']}")
    print(f"  • Category: {result.details['merchant_category']}")
    print(f"  • Country: {result.details['country']}")
    print(f"  • Timestamp: {result.details['timestamp']}")


def save_results_to_json(results):
    """Save analysis results to JSON file"""
    output_file = "c:/Users/dhara/Desktop/credit card/analysis/fraud_analysis_results.json"
    
    results_data = {
        "analysis_timestamp": datetime.now().isoformat(),
        "total_transactions": len(results),
        "transactions": [r.to_dict() for r in results]
    }
    
    with open(output_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"✓ Results saved to: {output_file}")


if __name__ == "__main__":
    demonstrate_fraud_detection()
