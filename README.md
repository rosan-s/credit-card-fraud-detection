# Credit Card Fraud Detection System - Documentation

## Overview

This is a comprehensive **Credit Card Transaction Pattern Analysis System** for fraud detection. It uses multiple machine learning and statistical techniques to identify fraudulent transactions in real-time or batch processing.

## System Architecture

### Core Components

#### 1. **Transaction Module** (`src/transaction.py`)
Handles all transaction data structures and management.

**Key Classes:**
- `Transaction`: Represents a single transaction with all attributes
- `TransactionHistory`: Manages transaction history and provides query methods
- `TransactionType` & `MerchantCategory`: Enums for classification

**Features:**
- Transaction serialization (to/from dict and JSON)
- Indexed cardholder transaction lookup
- Time-based transaction filtering
- Fraud marking system

#### 2. **Fraud Detection Algorithms** (`src/fraud_detection.py`)
Implements pattern recognition and anomaly detection.

**Key Classes:**

##### **AnomalyDetector**
Detects statistical anomalies in transaction patterns:
- **Amount Anomaly**: Uses Z-score analysis to identify unusual transaction amounts
  - Calculates standard deviation from historical transactions
  - Flags transactions exceeding 2.5 standard deviations
  - Returns confidence score based on Z-score

- **Time Anomaly**: Identifies unusual transaction times
  - Analyzes historical transaction hours
  - Flags transactions outside 5% frequency threshold
  - Useful for detecting after-hours fraud attempts

##### **VelocityChecker**
Detects unusual transaction velocity patterns:
- **Rapid Transactions**: Checks for multiple transactions in short timeframe
  - Configurable time window (default: 10 minutes)
  - Flags when 3+ transactions occur in window
  - Returns count of transactions in window

- **High Frequency Day**: Detects unusual daily transaction volume
  - Compares daily frequency to historical average
  - Flags when daily count exceeds 2x average
  - Helps identify account takeover scenarios

##### **GeographicAnalyzer**
Analyzes geographic patterns and locations:
- **Impossible Travel**: Checks if transaction distance/time is physically impossible
  - Uses Haversine formula to calculate distance
  - Compares against commercial flight speed (900 km/h)
  - Extremely reliable fraud indicator

- **Country Shift**: Detects transactions from new countries
  - Maintains set of countries with historical transactions
  - Flags first transaction from any new country
  - Configurable severity

##### **BehavioralAnalyzer**
Analyzes typical spending behavior:
- **Category Deviation**: Identifies unusual merchant categories
  - Analyzes category frequency distribution
  - Flags categories appearing in <5% of transactions
  - Helps detect account compromise

- **Merchant Pattern**: Checks against known merchant list
  - Maintains set of historical merchants
  - Flags new merchants (additional risk factor)
  - Helps identify compromised card usage

#### 3. **Analysis Engine** (`src/analysis_engine.py`)
Combines all detection methods into comprehensive scoring system.

**Key Classes:**

##### **FraudAnalysisResult**
Encapsulates analysis output:
- `fraud_score`: 0-1 confidence score
- `risk_level`: LOW, MEDIUM, HIGH, CRITICAL
- `fraud_indicators`: Dict of all detection results
- `recommendation`: Action recommendation
- `details`: Transaction context

##### **FraudAnalysisEngine**
Main orchestrator for fraud detection:

**Scoring Algorithm:**
- Weighted combination of 8 fraud indicators
- Weights reflect detection importance:
  - Impossible Travel: 30% (highest)
  - Rapid Transactions: 25%
  - Amount Anomaly: 20%
  - Country Shift: 20%
  - High Frequency Day: 15%
  - New Merchant: 15%
  - Time Anomaly: 10%
  - Category Deviation: 10%

**Risk Level Classification:**
- LOW: Score < 0.3 → APPROVE
- MEDIUM: Score 0.3-0.5 → MONITOR
- HIGH: Score 0.5-0.7 → REVIEW/VERIFY
- CRITICAL: Score ≥ 0.85 → BLOCK

**Recommendations:**
- BLOCK_TRANSACTION: Multiple high-risk indicators
- REQUIRE_VERIFICATION: High fraud risk with specific triggers
- REVIEW_TRANSACTION: Moderate risk factors
- MONITOR_TRANSACTION: Multiple moderate factors
- APPROVE_TRANSACTION: Low fraud risk

## Fraud Indicators

### 1. Amount Anomaly
**Detection Method:** Z-score statistical analysis
- **Trigger:** Transaction amount deviates >2.5 std from average
- **Confidence:** Normalized Z-score value
- **Reason:** Fraudsters often test with small amounts before large ones

### 2. Time Anomaly
**Detection Method:** Temporal pattern analysis
- **Trigger:** Transaction occurs at unusual hour (<5% frequency)
- **Confidence:** 1 - historical frequency
- **Reason:** Compromised accounts show different usage times

### 3. Rapid Transactions
**Detection Method:** Velocity checking within time window
- **Trigger:** 3+ transactions within 10-minute window
- **Confidence:** (count - threshold) / threshold
- **Reason:** Indicates rapid-fire testing or account takeover

### 4. High Frequency Day
**Detection Method:** Daily volume comparison
- **Trigger:** Daily count > 2x historical average
- **Confidence:** Normalized ratio
- **Reason:** Sudden spike in activity suggests compromise

### 5. Impossible Travel
**Detection Method:** Geographic distance/speed analysis
- **Trigger:** Speed > 900 km/h between consecutive transactions
- **Confidence:** (speed - 900) / 900
- **Reason:** Physically impossible movement (highest indicator)

### 6. Country Shift
**Detection Method:** Geographic location expansion
- **Trigger:** First transaction from new country
- **Confidence:** 0.6 (fixed, as it's binary)
- **Reason:** Indicates international compromise or cloning

### 7. Category Deviation
**Detection Method:** Merchant category distribution analysis
- **Trigger:** Category appears in <5% of transactions
- **Confidence:** 1 - frequency
- **Reason:** Spending pattern change suggests compromise

### 8. New Merchant
**Detection Method:** Merchant set membership
- **Trigger:** Merchant not in historical transaction set
- **Confidence:** 0.3 (fixed, moderate risk)
- **Reason:** Single indicator but supported by others

## Usage Examples

### Basic Analysis
```python
from src.transaction import Transaction, TransactionHistory, MerchantCategory, TransactionType
from src.analysis_engine import FraudAnalysisEngine
from datetime import datetime

# Create history with baseline transactions
history = TransactionHistory()
# ... add transactions ...

# Initialize engine
engine = FraudAnalysisEngine(history)

# Analyze transaction
result = engine.analyze_transaction(new_transaction)
print(f"Risk Level: {result.risk_level}")
print(f"Fraud Score: {result.fraud_score:.3f}")
```

### Batch Analysis
```python
# Analyze multiple transactions
transactions = [tx1, tx2, tx3, ...]
results = engine.batch_analyze(transactions)

# Generate summary report
summary = engine.generate_summary_report(results)
print(f"High-risk transactions: {summary['high_risk_transactions']}")
```

### Custom Thresholds
```python
# Detect amount anomaly with custom threshold
is_anomalous, confidence = anomaly_detector.detect_amount_anomaly(
    cardholder_id,
    amount,
    threshold_std=3.0  # More lenient (default: 2.5)
)
```

## Data Flow

```
Transaction Input
        ↓
[AnomalyDetector] → Amount/Time Analysis
        ↓
[VelocityChecker] → Rapid/Frequency Analysis
        ↓
[GeographicAnalyzer] → Location/Travel Analysis
        ↓
[BehavioralAnalyzer] → Category/Merchant Analysis
        ↓
[FraudAnalysisEngine] → Weighted Scoring
        ↓
FraudAnalysisResult (Score, Risk Level, Recommendation)
```

## Performance Characteristics

- **Analysis Time:** O(n) per transaction (where n = cardholder transaction history size)
- **Memory:** O(n) for history storage
- **Accuracy:** Depends on historical data quality and volume
  - Minimum 5 baseline transactions recommended for pattern analysis
  - 10+ transactions provides high confidence

## Configuration

### Adjustable Parameters

1. **Amount Anomaly Threshold**: `threshold_std = 2.5`
   - Increase for more lenient detection
   - Decrease for stricter detection

2. **Time Window**: `time_window_minutes = 10`
   - Adjust based on expected transaction frequency

3. **Minimum Transactions**: Various checks use 3-5 minimum
   - Ensures statistical significance

4. **Risk Thresholds**: Customize in `RISK_THRESHOLDS`
   - Adjust cutoff scores for risk levels

5. **Weights**: Modify in `WEIGHTS` dict
   - Prioritize certain indicators

## Best Practices

1. **Data Quality**: Ensure accurate transaction timestamps and locations
2. **Baseline Period**: Use 7-30 days minimum for baseline behavior
3. **Real-time Processing**: Analyze transactions immediately upon detection
4. **Alert Thresholds**: Adjust based on false positive tolerance
5. **Manual Review**: High-risk transactions should undergo manual review
6. **Feedback Loop**: Update models with confirmed fraud cases

## Extensibility

### Adding New Indicators
1. Implement detection method in appropriate class
2. Add to fraud_indicators dict in engine
3. Add weight to WEIGHTS dict
4. Update recommendations logic

### Adding New Merchant Categories
```python
class MerchantCategory(Enum):
    # Add new category
    HEALTHCARE = "healthcare"
```

### Custom Analysis Rules
```python
class CustomAnalyzer:
    def custom_detection(self, transaction):
        # Implement custom logic
        return (is_fraudulent, confidence)
```

## Test Cases

The demo includes 5 test cases:

1. **Unusual Amount**: $5000 purchase vs $50-200 baseline
2. **Impossible Travel**: San Francisco → London in 5 minutes
3. **Rapid Velocity**: 5 transactions in 5 minutes
4. **New Category**: Casino transaction by regular grocery shopper
5. **Legitimate**: Normal Starbucks transaction

## Output

### JSON Results Format
```json
{
  "transaction_id": "TX001",
  "cardholder_id": "CH001",
  "fraud_score": 0.75,
  "risk_level": "HIGH",
  "fraud_indicators": {
    "amount_anomaly": {"triggered": true, "confidence": 0.8},
    ...
  },
  "recommendation": "REQUIRE_VERIFICATION",
  "details": {...}
}
```

## Limitations & Future Improvements

### Current Limitations
- Single cardholder view (no cross-cardholder patterns)
- No machine learning/model training
- No seasonal adjustment
- Limited merchant data enrichment

### Future Enhancements
1. Machine learning models (Random Forest, Neural Networks)
2. Cross-cardholder fraud rings detection
3. Seasonal adjustment for merchant categories
4. Integration with external fraud databases
5. Real-time streaming analysis
6. Merchant categorization enrichment
7. Device fingerprinting
8. IP geolocation analysis

## File Structure

```
credit card/
├── src/
│   ├── __init__.py
│   ├── transaction.py          # Transaction data structures
│   ├── fraud_detection.py      # Detection algorithms
│   └── analysis_engine.py      # Main analysis engine
├── data/                        # Transaction data storage
├── analysis/                    # Analysis results
│   └── fraud_analysis_results.json
└── demo.py                      # Demonstration script
```

## Dependencies

- Python 3.7+
- Standard library only (math, datetime, dataclasses, enum, statistics)
- No external dependencies required

## Author Notes

This system is designed to be:
- **Modular**: Each detector works independently
- **Extensible**: Easy to add new detectors
- **Interpretable**: Clear fraud indicators for explaining decisions
- **Efficient**: Minimal computational overhead
- **Production-ready**: Can be integrated into real banking systems

For production deployment, consider:
- Database backend for history storage
- API wrapper for real-time analysis
- Advanced ML models
- 24/7 monitoring and alerting
- Regular model retraining
