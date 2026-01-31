"""
Advanced Fraud Analysis Example with Report Generation
Demonstrates comprehensive analysis and reporting capabilities
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
from src.report_generator import FraudAnalysisReportGenerator, print_beautiful_report


def create_advanced_test_scenarios() -> TransactionHistory:
    """Create a more complex transaction history with multiple patterns"""
    history = TransactionHistory()
    
    base_date = datetime(2025, 1, 1, 9, 0, 0)
    
    # Cardholder 1: Normal user with stable behavior
    ch1_transactions = [
        # Weekly grocery shopping
        Transaction(
            transaction_id="CH1_TX001",
            cardholder_id="CH001",
            amount=87.50,
            timestamp=base_date + timedelta(days=0),
            merchant_name="Whole Foods Market",
            merchant_category=MerchantCategory.GROCERY,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 40.7128, "longitude": -74.0060},  # NYC
            mcc_code="5411",
            country="USA"
        ),
        Transaction(
            transaction_id="CH1_TX002",
            cardholder_id="CH001",
            amount=45.30,
            timestamp=base_date + timedelta(days=3),
            merchant_name="Starbucks Coffee",
            merchant_category=MerchantCategory.RESTAURANT,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 40.7128, "longitude": -74.0060},
            mcc_code="5814",
            country="USA"
        ),
        Transaction(
            transaction_id="CH1_TX003",
            cardholder_id="CH001",
            amount=52.00,
            timestamp=base_date + timedelta(days=7),
            merchant_name="Shell Gas Station",
            merchant_category=MerchantCategory.GAS,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 40.7128, "longitude": -74.0060},
            mcc_code="5542",
            country="USA"
        ),
        Transaction(
            transaction_id="CH1_TX004",
            cardholder_id="CH001",
            amount=125.99,
            timestamp=base_date + timedelta(days=10),
            merchant_name="Target Store",
            merchant_category=MerchantCategory.RETAIL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 40.7128, "longitude": -74.0060},
            mcc_code="5310",
            country="USA"
        ),
        Transaction(
            transaction_id="CH1_TX005",
            cardholder_id="CH001",
            amount=200.00,
            timestamp=base_date + timedelta(days=14),
            merchant_name="Amazon.com",
            merchant_category=MerchantCategory.ONLINE_RETAIL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 40.7128, "longitude": -74.0060},
            mcc_code="5961",
            country="USA"
        ),
    ]
    
    for tx in ch1_transactions:
        history.add_transaction(tx)
    
    # Cardholder 2: Frequent traveler
    ch2_base_date = base_date + timedelta(days=20)
    ch2_transactions = [
        Transaction(
            transaction_id="CH2_TX001",
            cardholder_id="CH002",
            amount=234.50,
            timestamp=ch2_base_date,
            merchant_name="United Airlines",
            merchant_category=MerchantCategory.TRAVEL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 40.7128, "longitude": -74.0060},  # NYC
            mcc_code="4511",
            country="USA"
        ),
        Transaction(
            transaction_id="CH2_TX002",
            cardholder_id="CH002",
            amount=150.00,
            timestamp=ch2_base_date + timedelta(days=2),
            merchant_name="Hilton Hotel",
            merchant_category=MerchantCategory.TRAVEL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 51.5074, "longitude": -0.1278},  # London
            mcc_code="7011",
            country="UK"
        ),
        Transaction(
            transaction_id="CH2_TX003",
            cardholder_id="CH002",
            amount=89.00,
            timestamp=ch2_base_date + timedelta(days=5),
            merchant_name="Harrods London",
            merchant_category=MerchantCategory.RETAIL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 51.5074, "longitude": -0.1278},
            mcc_code="5310",
            country="UK"
        ),
    ]
    
    for tx in ch2_transactions:
        history.add_transaction(tx)
    
    return history


def demonstrate_advanced_analysis():
    """Run advanced fraud analysis with reporting"""
    
    print("\n" + "=" * 100)
    print("ADVANCED FRAUD ANALYSIS SYSTEM - COMPREHENSIVE EXAMPLE".center(100))
    print("=" * 100 + "\n")
    
    # Create transaction history
    history = create_advanced_test_scenarios()
    print(f"✓ Created transaction history with {len(history.transactions)} transactions\n")
    
    # Initialize engine
    engine = FraudAnalysisEngine(history)
    print("✓ Fraud Detection Engine initialized\n")
    
    # Create test transactions for analysis
    test_transactions = []
    
    # Scenario 1: Normal transaction
    tx1 = Transaction(
        transaction_id="TEST_TX001",
        cardholder_id="CH001",
        amount=67.89,
        timestamp=base_date + timedelta(days=17, hours=10),
        merchant_name="Whole Foods Market",
        merchant_category=MerchantCategory.GROCERY,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 40.7128, "longitude": -74.0060},
        mcc_code="5411",
        country="USA"
    )
    test_transactions.append(tx1)
    
    # Scenario 2: Suspicious amount
    tx2 = Transaction(
        transaction_id="TEST_TX002",
        cardholder_id="CH001",
        amount=3500.00,  # Way above average
        timestamp=base_date + timedelta(days=18, hours=14),
        merchant_name="Gucci Store",
        merchant_category=MerchantCategory.RETAIL,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 40.7128, "longitude": -74.0060},
        mcc_code="5310",
        country="USA"
    )
    test_transactions.append(tx2)
    
    # Scenario 3: Rapid transactions
    for i in range(3):
        rapid_tx = Transaction(
            transaction_id=f"TEST_TX_RAPID_{i}",
            cardholder_id="CH001",
            amount=99.99 + i * 10,
            timestamp=base_date + timedelta(days=19, hours=15, minutes=i),
            merchant_name=f"Store {i}",
            merchant_category=MerchantCategory.RETAIL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 40.7128, "longitude": -74.0060},
            mcc_code="5310",
            country="USA"
        )
        history.add_transaction(rapid_tx)
        test_transactions.append(rapid_tx)
    
    # Scenario 4: Impossible travel
    tx4 = Transaction(
        transaction_id="TEST_TX004",
        cardholder_id="CH001",
        amount=125.00,
        timestamp=base_date + timedelta(days=19, hours=15, minutes=5),  # 5 minutes after last
        merchant_name="Piccadilly Circus",
        merchant_category=MerchantCategory.RETAIL,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 51.5100, "longitude": -0.1340},  # London - impossible travel
        mcc_code="5310",
        country="UK"
    )
    test_transactions.append(tx4)
    
    # Scenario 5: Unusual time
    tx5 = Transaction(
        transaction_id="TEST_TX005",
        cardholder_id="CH001",
        amount=200.00,
        timestamp=base_date + timedelta(days=20, hours=3, minutes=30),  # 3:30 AM
        merchant_name="Casino Resort",
        merchant_category=MerchantCategory.ENTERTAINMENT,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 36.1699, "longitude": -115.1398},  # Las Vegas
        mcc_code="7011",
        country="USA"
    )
    test_transactions.append(tx5)
    
    # Scenario 6: Legitimate traveler transaction
    tx6 = Transaction(
        transaction_id="TEST_TX006",
        cardholder_id="CH002",
        amount=180.00,
        timestamp=ch2_base_date + timedelta(days=8),
        merchant_name="Café in Paris",
        merchant_category=MerchantCategory.RESTAURANT,
        transaction_type=TransactionType.PURCHASE,
        location={"latitude": 48.8566, "longitude": 2.3522},  # Paris
        mcc_code="5814",
        country="France"
    )
    test_transactions.append(tx6)
    
    # Analyze all test transactions
    print("Analyzing test transactions...\n")
    results = engine.batch_analyze(test_transactions)
    
    # Print individual results
    print("=" * 100)
    print("INDIVIDUAL TRANSACTION ANALYSIS RESULTS".center(100))
    print("=" * 100 + "\n")
    
    for i, result in enumerate(results, 1):
        print(f"Transaction {i}: {result.transaction_id}")
        print(f"  Risk Level: {result.risk_level} | Fraud Score: {result.fraud_score:.3f}")
        print(f"  Recommendation: {result.recommendation}")
        print()
    
    # Generate comprehensive report
    print("\n" + "=" * 100)
    print("GENERATING COMPREHENSIVE FRAUD ANALYSIS REPORT".center(100))
    print("=" * 100 + "\n")
    
    report_generator = FraudAnalysisReportGenerator(engine, results)
    comprehensive_report = report_generator.generate_comprehensive_report()
    
    # Print beautiful report
    print_beautiful_report(comprehensive_report)
    
    # Save detailed report to JSON
    report_file = "c:/Users/dhara/Desktop/credit card/analysis/comprehensive_fraud_report.json"
    with open(report_file, 'w') as f:
        json.dump(comprehensive_report, f, indent=2, default=str)
    
    print(f"✓ Detailed report saved to: {report_file}\n")
    
    # Generate individual cardholder reports
    print("=" * 100)
    print("CARDHOLDER-SPECIFIC ANALYSIS".center(100))
    print("=" * 100 + "\n")
    
    for cardholder_id in ["CH001", "CH002"]:
        ch_report = report_generator.generate_cardholder_report(cardholder_id)
        print(f"\n📋 Cardholder Report: {cardholder_id}")
        print("-" * 100)
        print(f"  Total Transactions: {ch_report.get('total_transactions', 0)}")
        print(f"  High-Risk: {ch_report.get('high_risk_count', 0)} | Medium-Risk: {ch_report.get('medium_risk_count', 0)}")
        print(f"  Avg Fraud Score: {ch_report.get('average_fraud_score', 0):.3f}")
        
        if ch_report.get('high_risk_transactions'):
            print(f"\n  ⚠️  High-Risk Transactions:")
            for tx in ch_report.get('high_risk_transactions', []):
                print(f"    • {tx['transaction_id']}: Score={tx['fraud_score']:.3f}")
        print()


# Placeholder for base_date (defined in create_advanced_test_scenarios context)
base_date = datetime(2025, 1, 1, 9, 0, 0)
ch2_base_date = base_date + timedelta(days=20)


if __name__ == "__main__":
    demonstrate_advanced_analysis()
