# Credit Card Fraud Detection System - API Reference

## Quick Start

**Start Server**:
```bash
python app.py
```

**Access Web UI**:
```
http://localhost:5000
```

---

## Web Routes

### Home Page
- **URL**: `GET http://localhost:5000/`
- **Purpose**: System overview, features, indicators, and risk levels
- **Returns**: HTML page

### Dashboard
- **URL**: `GET http://localhost:5000/dashboard`
- **Purpose**: View system statistics, transactions, alerts
- **Returns**: HTML dashboard with live stats

### Analyze Transaction
- **URL**: `GET http://localhost:5000/analyze`
- **Purpose**: Interactive form to analyze individual transactions
- **Returns**: HTML form and results

### ML Detector
- **URL**: `GET http://localhost:5000/ml-detector`
- **Purpose**: Train ML models and make predictions
- **Returns**: HTML interface for ML operations

### About
- **URL**: `GET http://localhost:5000/about`
- **Purpose**: Documentation and API reference
- **Returns**: HTML documentation page

---

## REST API Endpoints

### 1. Analyze Single Transaction

**Endpoint**: `POST /api/analyze`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cardholder_id": "CH001",
    "amount": 500.00,
    "merchant_name": "Best Buy",
    "merchant_category": "Electronics",
    "country": "US",
    "timestamp": "2024-01-15T14:30:00",
    "transaction_id": "TX_001",
    "transaction_type": "purchase",
    "mcc_code": "5310",
    "location": {"latitude": 40.7128, "longitude": -74.0060}
  }'
```

**Response** (Success):
```json
{
  "status": "success",
  "analysis": {
    "transaction_id": "TX_001",
    "cardholder_id": "CH001",
    "fraud_score": 0.45,
    "risk_level": "MEDIUM",
    "recommendation": "REVIEW",
    "fraud_indicators": {
      "Impossible Travel": {
        "triggered": false,
        "confidence": 0.05,
        "weight": 0.30
      },
      "Rapid Transactions": {
        "triggered": true,
        "confidence": 0.80,
        "weight": 0.25
      },
      "Amount Anomaly": {
        "triggered": false,
        "confidence": 0.15,
        "weight": 0.20
      },
      "Country Shift": {
        "triggered": false,
        "confidence": 0.10,
        "weight": 0.20
      },
      "High Frequency Day": {
        "triggered": true,
        "confidence": 0.70,
        "weight": 0.15
      },
      "New Merchant": {
        "triggered": false,
        "confidence": 0.05,
        "weight": 0.15
      },
      "Time Anomaly": {
        "triggered": false,
        "confidence": 0.10,
        "weight": 0.10
      },
      "Category Deviation": {
        "triggered": false,
        "confidence": 0.05,
        "weight": 0.10
      }
    },
    "details": {
      "transaction_amount": 500.00,
      "merchant_name": "Best Buy",
      "merchant_category": "Electronics",
      "country": "US",
      "timestamp": "2024-01-15T14:30:00"
    }
  }
}
```

**Response** (Error):
```json
{
  "status": "error",
  "message": "Invalid transaction data"
}
```

---

### 2. Batch Analyze Transactions

**Endpoint**: `POST /api/analyze-batch`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/analyze-batch \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {
        "cardholder_id": "CH001",
        "amount": 100.00,
        "merchant_name": "Starbucks",
        "merchant_category": "Coffee",
        "country": "US",
        "timestamp": "2024-01-15T09:00:00",
        "transaction_id": "TX_001",
        "transaction_type": "purchase",
        "mcc_code": "5310",
        "location": {"latitude": 40.7128, "longitude": -74.0060}
      },
      {
        "cardholder_id": "CH001",
        "amount": 5000.00,
        "merchant_name": "Electronics Store",
        "merchant_category": "Electronics",
        "country": "JP",
        "timestamp": "2024-01-15T10:30:00",
        "transaction_id": "TX_002",
        "transaction_type": "purchase",
        "mcc_code": "5310",
        "location": {"latitude": 35.6762, "longitude": 139.6503}
      }
    ]
  }'
```

**Response**:
```json
{
  "status": "success",
  "results": [
    { "transaction_id": "TX_001", "fraud_score": 0.15, "risk_level": "LOW" },
    { "transaction_id": "TX_002", "fraud_score": 0.85, "risk_level": "CRITICAL" }
  ],
  "summary": {
    "total": 2,
    "low_risk": 1,
    "medium_risk": 0,
    "high_risk": 0,
    "critical_risk": 1
  }
}
```

---

### 3. Get System Statistics

**Endpoint**: `GET /api/stats`

**Example Request**:
```bash
curl http://localhost:5000/api/stats
```

**Response**:
```json
{
  "status": "success",
  "stats": {
    "total_transactions": 150,
    "unique_cardholders": 42,
    "total_amount": 45320.50,
    "avg_transaction_amount": 302.14,
    "high_risk_transactions": [
      {
        "transaction_id": "TX_045",
        "merchant_name": "Suspicious Store",
        "amount": 2500.00,
        "fraud_score": 0.92
      }
    ],
    "daily_stats": {
      "transactions_today": 25,
      "volume_today": 8500.00,
      "fraud_alerts_today": 3,
      "avg_transaction_today": 340.00
    },
    "fraud_engine_status": "ACTIVE",
    "ml_engine_status": "READY"
  }
}
```

---

### 4. Train ML Models

**Endpoint**: `POST /api/ml-train`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/ml-train \
  -H "Content-Type: application/json" \
  -d '{"num_samples": 100}'
```

**Response**:
```json
{
  "status": "success",
  "accuracy": 0.92,
  "metrics": {
    "accuracy": 0.92,
    "precision": 0.88,
    "recall": 0.95,
    "f1_score": 0.91
  },
  "message": "Models trained successfully with 100 samples"
}
```

---

### 5. ML Fraud Prediction

**Endpoint**: `POST /api/ml-predict`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/ml-predict \
  -H "Content-Type: application/json" \
  -d '{
    "cardholder_id": "CH001",
    "amount": 750.00,
    "merchant_name": "Amazon",
    "merchant_category": "Online Retail",
    "country": "US",
    "timestamp": "2024-01-15T15:00:00",
    "transaction_id": "TX_100",
    "transaction_type": "purchase",
    "mcc_code": "5310",
    "location": {"latitude": 40.7128, "longitude": -74.0060}
  }'
```

**Response**:
```json
{
  "status": "success",
  "prediction": {
    "fraud_probability": 0.38,
    "logistic_probability": 0.35,
    "forest_probability": 0.41,
    "risk_level": "MEDIUM",
    "recommendation": "REVIEW"
  }
}
```

---

### 6. Get Cardholder Information

**Endpoint**: `GET /api/cardholder/<cardholder_id>`

**Example Request**:
```bash
curl http://localhost:5000/api/cardholder/CH001
```

**Response**:
```json
{
  "status": "success",
  "cardholder": {
    "id": "CH001",
    "total_transactions": 25,
    "total_volume": 5000.00,
    "avg_transaction": 200.00,
    "high_risk_count": 2,
    "last_transaction": {
      "transaction_id": "TX_100",
      "amount": 750.00,
      "merchant_name": "Amazon",
      "timestamp": "2024-01-15T15:00:00"
    }
  }
}
```

---

### 7. Health Check

**Endpoint**: `GET /api/health`

**Example Request**:
```bash
curl http://localhost:5000/api/health
```

**Response**:
```json
{
  "status": "healthy",
  "fraud_engine": "active",
  "ml_engine": "ready",
  "uptime": "2 hours 30 minutes"
}
```

---

## Risk Levels & Color Coding

| Risk Level | Score Range | Color | Emoji | Recommendation |
|-----------|------------|-------|-------|-----------------|
| LOW | 0.0 - 0.3 | Green | 🟢 | APPROVE |
| MEDIUM | 0.3 - 0.5 | Yellow | 🟡 | REVIEW |
| HIGH | 0.5 - 0.7 | Orange | 🟠 | REVIEW |
| CRITICAL | 0.7 - 1.0 | Red | 🔴 | REJECT |

---

## Fraud Indicators (with weights)

1. **Impossible Travel** (30%) - Detection of physically impossible travel between locations
2. **Rapid Transactions** (25%) - Multiple transactions in rapid succession
3. **Amount Anomaly** (20%) - Transaction amount significantly deviates from history
4. **Country Shift** (20%) - Sudden location changes in different countries
5. **High Frequency Day** (15%) - Unusual number of transactions in a day
6. **New Merchant** (15%) - First transaction with a new merchant
7. **Time Anomaly** (10%) - Transaction at unusual times for the cardholder
8. **Category Deviation** (10%) - Transaction category unusual for the cardholder

---

## ML Models

### Logistic Regression
- **Activation**: Sigmoid function
- **Training**: Gradient descent
- **Features**: 15 engineered features
- **Output**: Binary classification (Fraud/Not Fraud) with probability

### Random Forest
- **Trees**: Ensemble of decision trees
- **Sampling**: Bootstrap sampling with replacement
- **Splitting**: Information gain (entropy) based
- **Output**: Binary classification with probability

### Ensemble Prediction
- **Method**: Average of both models
- **Formula**: `ensemble_prob = (logistic_prob + forest_prob) / 2`

---

## Example Integration (Python)

```python
import requests
import json

# API endpoint
URL = "http://localhost:5000/api/analyze"

# Transaction data
transaction = {
    "cardholder_id": "CH123",
    "amount": 199.99,
    "merchant_name": "Target",
    "merchant_category": "Retail",
    "country": "US",
    "timestamp": "2024-01-15T14:30:00",
    "transaction_id": "TX_9999",
    "transaction_type": "purchase",
    "mcc_code": "5310",
    "location": {"latitude": 40.7128, "longitude": -74.0060}
}

# Make request
response = requests.post(URL, json=transaction)
result = response.json()

# Process result
if result["status"] == "success":
    analysis = result["analysis"]
    print(f"Risk Level: {analysis['risk_level']}")
    print(f"Fraud Score: {analysis['fraud_score']:.2%}")
    print(f"Recommendation: {analysis['recommendation']}")
```

---

## Error Codes

| Code | Message | Meaning |
|------|---------|---------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request data |
| 404 | Not Found | Endpoint not found |
| 500 | Internal Error | Server error |

---

## Rate Limiting

Currently not implemented. For production deployment, consider:
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## Authentication

Currently not implemented. For production deployment, add:
- API key authentication
- OAuth 2.0
- JWT tokens

---

**API Version**: 1.0.0  
**Last Updated**: 2024
