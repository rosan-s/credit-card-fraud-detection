# Credit Card Fraud Detection System - Setup & Deployment Guide

## Overview

This document provides complete instructions for setting up and running the Credit Card Fraud Detection System with Machine Learning and Web Interface.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Browser                             │
│              (HTML5 + CSS3 + JavaScript)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/REST API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Flask Web Server                           │
│          (Port 5000 by default)                             │
├──────────────────────────────────────────────────────────────┤
│  Routes:                                                      │
│  - GET  /                          (Home Page)              │
│  - GET  /dashboard                 (Statistics)             │
│  - GET  /analyze                   (Analysis Interface)     │
│  - GET  /ml-detector               (ML Training/Prediction) │
│  - GET  /about                     (Documentation)          │
│                                                              │
│  API Endpoints:                                             │
│  - POST /api/analyze               (Single Transaction)     │
│  - POST /api/analyze-batch         (Batch Analysis)         │
│  - POST /api/ml-train              (Train ML Models)        │
│  - POST /api/ml-predict            (ML Prediction)          │
│  - GET  /api/stats                 (System Statistics)      │
│  - GET  /api/cardholder/<id>       (Cardholder Info)       │
│  - GET  /api/health                (Health Check)           │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼─────┐  ┌───▼──────┐  ┌──▼────────┐
    │Transaction│  │ Fraud    │  │ ML        │
    │Module     │  │Detection │  │Detector   │
    │           │  │Engine    │  │           │
    │ - Parse   │  │          │  │ - Feature │
    │ - Store   │  │ - 8      │  │  Engineer │
    │ - History │  │   Indicators│ - Logistic│
    │           │  │ - Weighted   │   Regression
    │           │  │   Scoring    │ - Random  │
    │           │  │ - Risk       │   Forest  │
    │           │  │   Levels     │           │
    └───────────┘  └──────────┘  └───────────┘
```

## Prerequisites

- **Python**: 3.7 or higher
- **pip**: Python package manager
- **Virtual Environment** (recommended): `venv` or `conda`
- **Browser**: Any modern web browser (Chrome, Firefox, Safari, Edge)

## Installation Steps

### 1. Clone/Download the Project

```bash
# Navigate to project directory
cd "c:\Users\dhara\Desktop\credit card"
```

### 2. Create Virtual Environment (Recommended)

**Option A: Using venv (built-in)**
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

**Option B: Using conda**
```powershell
conda create -n fraud-detection python=3.10
conda activate fraud-detection
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- **Flask** (Web framework)
- **Werkzeug** (WSGI utilities)
- **Jinja2** (Templating engine)
- **click** (CLI utilities)
- **itsdangerous** (Data serialization)

### 4. Verify Installation

```powershell
python -c "import flask; print(f'Flask version: {flask.__version__}')"
```

## Running the Application

### 1. Start the Flask Web Server

```powershell
python app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
 * Restarting with stat reloader
 * Debugger is active!
```

### 2. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

**or**

```
http://127.0.0.1:5000
```

### 3. Stop the Server

Press `Ctrl+C` in the terminal where Flask is running.

## Using the Web Application

### Home Page (/)
- **Purpose**: Overview of the fraud detection system
- **Features**:
  - Hero section with quick start buttons
  - Feature cards explaining key capabilities
  - Fraud indicators with weights
  - Risk level classification

### Dashboard (/dashboard)
- **Purpose**: Monitor system statistics and alerts
- **Features**:
  - Total transactions count
  - Unique cardholders count
  - Total transaction volume
  - Average transaction amount
  - High-risk transaction alerts
  - Daily summary statistics
  - System status indicators
  - Auto-refreshes every 30 seconds

### Analyze (/analyze)
- **Purpose**: Analyze individual transactions for fraud risk
- **Steps**:
  1. Enter transaction details:
     - Cardholder ID
     - Transaction amount
     - Merchant name
     - Merchant category (e.g., Retail, Gas Station)
     - Country
     - Timestamp (auto-filled with current time)
  2. Click "Analyze Transaction"
  3. View results:
     - Risk level (LOW/MEDIUM/HIGH/CRITICAL) with color coding
     - Fraud score (0-100%)
     - Individual fraud indicators (triggered/not triggered)
     - Recommendation (APPROVE/REVIEW/REJECT)
     - Transaction details summary

### ML Detector (/ml-detector)
- **Purpose**: Train and use machine learning models
- **Features**:

  **Training Section**:
  - Input sample count (default: 100)
  - Click "Train Models" to train ML models
  - View performance metrics:
    - Accuracy
    - Precision
    - Recall
    - F1-Score

  **Prediction Section**:
  - Enter transaction details
  - Click "Predict with ML"
  - View results:
    - Risk level from ML models
    - Fraud probability (ensemble: average of Logistic Regression and Random Forest)
    - Individual model probabilities
    - Recommendation based on ML prediction

### About (/about)
- **Purpose**: System documentation
- **Contains**:
  - System overview
  - Technology stack
  - Fraud detection methods (rule-based + ML)
  - Performance metrics
  - API endpoint documentation
  - Future enhancements

## REST API Endpoints

### 1. Single Transaction Analysis

**Endpoint**: `POST /api/analyze`

**Request Body**:
```json
{
  "cardholder_id": "CH123456",
  "amount": 150.50,
  "merchant_name": "Amazon",
  "merchant_category": "Online Retail",
  "country": "US",
  "timestamp": "2024-01-15T10:30:00",
  "transaction_id": "TX_1234567890",
  "transaction_type": "purchase",
  "mcc_code": "5310",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

**Response**:
```json
{
  "status": "success",
  "analysis": {
    "transaction_id": "TX_1234567890",
    "fraud_score": 0.35,
    "risk_level": "MEDIUM",
    "recommendation": "REVIEW",
    "fraud_indicators": {
      "Impossible Travel": {"triggered": false, "confidence": 0.1},
      "Rapid Transactions": {"triggered": true, "confidence": 0.8},
      ...
    },
    "details": {...}
  }
}
```

### 2. Batch Transaction Analysis

**Endpoint**: `POST /api/analyze-batch`

**Request Body**:
```json
{
  "transactions": [
    {transaction_object_1},
    {transaction_object_2},
    ...
  ]
}
```

**Response**: Array of analysis results

### 3. Train ML Models

**Endpoint**: `POST /api/ml-train`

**Request Body**:
```json
{
  "num_samples": 100
}
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
  "message": "Models trained successfully"
}
```

### 4. ML Prediction

**Endpoint**: `POST /api/ml-predict`

**Request Body**: (Same as analyze, but runs ML models)

**Response**:
```json
{
  "status": "success",
  "prediction": {
    "fraud_probability": 0.42,
    "logistic_probability": 0.40,
    "forest_probability": 0.44,
    "risk_level": "MEDIUM",
    "recommendation": "REVIEW"
  }
}
```

### 5. System Statistics

**Endpoint**: `GET /api/stats`

**Response**:
```json
{
  "status": "success",
  "stats": {
    "total_transactions": 150,
    "unique_cardholders": 45,
    "total_amount": 25000.50,
    "avg_transaction_amount": 166.67,
    "high_risk_transactions": [...],
    "daily_stats": {...},
    "fraud_engine_status": "ACTIVE",
    "ml_engine_status": "READY"
  }
}
```

### 6. Cardholder Information

**Endpoint**: `GET /api/cardholder/<cardholder_id>`

**Response**:
```json
{
  "status": "success",
  "cardholder": {
    "id": "CH123456",
    "total_transactions": 25,
    "total_volume": 5000.00,
    "avg_transaction": 200.00,
    "high_risk_count": 2,
    "last_transaction": {...}
  }
}
```

### 7. Health Check

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "fraud_engine": "active",
  "ml_engine": "ready",
  "uptime": "2 hours 15 minutes"
}
```

## Project Structure

```
c:\Users\dhara\Desktop\credit card\
├── app.py                          # Flask web application
├── requirements.txt                # Python dependencies
├── SETUP_GUIDE.md                  # This file
│
├── src/
│   ├── transaction.py              # Transaction data structures
│   ├── fraud_detection.py          # 8 fraud detection indicators
│   ├── analysis_engine.py          # Weighted scoring engine
│   ├── report_generator.py         # Report generation
│   └── ml_detector.py              # ML models (Logistic Regression, Random Forest)
│
├── templates/                      # HTML templates
│   ├── index.html                  # Home page
│   ├── dashboard.html              # Dashboard
│   ├── analyze.html                # Analysis interface
│   ├── ml_detector.html            # ML training/prediction
│   └── about.html                  # Documentation
│
└── static/                         # Static assets
    ├── css/
    │   └── style.css               # Main stylesheet
    └── js/
        ├── main.js                 # Core JavaScript
        ├── dashboard.js            # Dashboard functionality
        ├── analyze.js              # Analysis page functionality
        └── ml_detector.js          # ML detector functionality
```

## Configuration

### Flask Development Server

Default settings in `app.py`:
```python
app.config['DEBUG'] = True           # Enable debug mode
app.config['FLASK_ENV'] = 'development'
```

**For Production**, disable debug mode:
```python
app.config['DEBUG'] = False
```

### Changing Default Port

To run on a different port, modify the last line of `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Change 5000 to your port
```

### System Initialization

The app automatically:
1. Initializes a FraudAnalysisEngine with all 8 indicators
2. Initializes an MLFraudDetector instance
3. Loads 10 sample baseline transactions for statistics
4. Sets up global instances for request handling

## Troubleshooting

### Issue: "Flask not found" error

**Solution**: Ensure virtual environment is activated and dependencies installed
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### Issue: Port 5000 already in use

**Solution**: Use a different port in `app.py`:
```python
app.run(debug=True, port=8080)
```

Or kill the existing process:
```powershell
# PowerShell
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use a different port
python app.py --port 8080
```

### Issue: Templates not found (404 error)

**Solution**: Ensure `templates/` folder exists in same directory as `app.py`
```powershell
ls templates/
```

### Issue: Static files not loading (CSS/JS not working)

**Solution**: Ensure `static/` folder structure is correct
```powershell
ls static/css/style.css
ls static/js/main.js
```

### Issue: ML models not training

**Solution**: Ensure `src/ml_detector.py` and dependencies are in place
```powershell
python -c "from src.ml_detector import MLFraudDetector; print('ML module loaded successfully')"
```

## Running Demo Scripts

### Basic Demo

```powershell
python demo.py
```

Demonstrates:
- Transaction creation
- Basic fraud analysis
- Individual indicator results
- Reporting

### Advanced Demo

```powershell
python advanced_demo.py
```

Demonstrates:
- Batch transaction processing
- Cardholder analysis
- Comprehensive reporting
- Historical analysis

## Performance Notes

- **Response Time**: Most API endpoints return results in < 100ms
- **Concurrent Users**: Flask development server handles ~50 concurrent users
- **Database**: Uses in-memory storage (no persistent database)
- **ML Models**: Training on 100 samples takes ~1-2 seconds
- **Scalability**: For production, use Gunicorn or Waitress

## Production Deployment

### Using Gunicorn

```powershell
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Waitress

```powershell
pip install waitress
waitress-serve --port=5000 app:app
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```powershell
docker build -t fraud-detection .
docker run -p 5000:5000 fraud-detection
```

## Support & Documentation

- **API Documentation**: Available at http://localhost:5000/about
- **Code Documentation**: See docstrings in each module
- **Issues**: Check troubleshooting section above

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python Documentation](https://docs.python.org/)
- [Fraud Detection Best Practices](https://www.fraud.org/)

---

**Last Updated**: 2024
**Version**: 1.0.0
