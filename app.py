"""
Flask Web Application for Credit Card Fraud Detection
Provides REST API and web interface
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os

from src.transaction import (
    Transaction, 
    TransactionHistory, 
    MerchantCategory, 
    TransactionType
)
from src.analysis_engine import FraudAnalysisEngine, FraudAnalysisResult
from src.ml_detector import MLFraudDetector, FeatureEngineer
from src.report_generator import FraudAnalysisReportGenerator


# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_SORT_KEYS'] = False

# Global instances
history = TransactionHistory()
engine = None
ml_detector = None
report_generator = None


def initialize_system():
    """Initialize fraud detection system"""
    global engine, ml_detector, report_generator
    
    # Load sample baseline transactions
    load_sample_transactions()
    
    # Initialize engines
    engine = FraudAnalysisEngine(history)
    ml_detector = MLFraudDetector(history)
    
    print("✓ System initialized")


def load_sample_transactions():
    """Load sample transactions for baseline"""
    base_date = datetime(2025, 1, 1, 9, 0, 0)
    
    transactions = [
        Transaction(
            transaction_id=f"BASELINE_{i}",
            cardholder_id="CH001",
            amount=50 + i * 10,
            timestamp=base_date + timedelta(days=i),
            merchant_name=f"Merchant {i % 3}",
            merchant_category=MerchantCategory.RETAIL,
            transaction_type=TransactionType.PURCHASE,
            location={"latitude": 40.7128, "longitude": -74.0060},
            mcc_code="5310",
            country="USA"
        )
        for i in range(10)
    ]
    
    for tx in transactions:
        history.add_transaction(tx)


# ==================== WEB INTERFACE ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


@app.route('/analyze')
def analyze_page():
    """Transaction analysis page"""
    return render_template('analyze.html')


@app.route('/ml-detector')
def ml_page():
    """ML detector page"""
    return render_template('ml_detector.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


# ==================== API ROUTES ====================

@app.route('/api/analyze', methods=['POST'])
def api_analyze_transaction():
    """Analyze a single transaction"""
    try:
        data = request.json
        
        # Parse transaction
        transaction = Transaction(
            transaction_id=data.get('transaction_id', f"TX_{datetime.now().timestamp()}"),
            cardholder_id=data.get('cardholder_id', 'CH001'),
            amount=float(data.get('amount', 100)),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            merchant_name=data.get('merchant_name', 'Unknown'),
            merchant_category=MerchantCategory(data.get('merchant_category', 'retail')),
            transaction_type=TransactionType(data.get('transaction_type', 'purchase')),
            location=data.get('location', {'latitude': 40.7128, 'longitude': -74.0060}),
            mcc_code=data.get('mcc_code', '5310'),
            country=data.get('country', 'USA')
        )
        
        # Analyze with rule-based engine
        result = engine.analyze_transaction(transaction)
        
        # Add to history
        history.add_transaction(transaction)
        
        return jsonify({
            "status": "success",
            "analysis": result.to_dict()
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/analyze-batch', methods=['POST'])
def api_analyze_batch():
    """Analyze multiple transactions"""
    try:
        data = request.json
        transactions_data = data.get('transactions', [])
        
        transactions = []
        for tx_data in transactions_data:
            transaction = Transaction(
                transaction_id=tx_data.get('transaction_id', f"TX_{len(transactions)}"),
                cardholder_id=tx_data.get('cardholder_id', 'CH001'),
                amount=float(tx_data.get('amount', 100)),
                timestamp=datetime.fromisoformat(tx_data.get('timestamp', datetime.now().isoformat())),
                merchant_name=tx_data.get('merchant_name', 'Unknown'),
                merchant_category=MerchantCategory(tx_data.get('merchant_category', 'retail')),
                transaction_type=TransactionType(tx_data.get('transaction_type', 'purchase')),
                location=tx_data.get('location', {'latitude': 40.7128, 'longitude': -74.0060}),
                mcc_code=tx_data.get('mcc_code', '5310'),
                country=tx_data.get('country', 'USA')
            )
            transactions.append(transaction)
            history.add_transaction(transaction)
        
        # Batch analyze
        results = engine.batch_analyze(transactions)
        
        return jsonify({
            "status": "success",
            "total": len(results),
            "results": [r.to_dict() for r in results],
            "summary": engine.generate_summary_report(results)
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/ml-predict', methods=['POST'])
def api_ml_predict():
    """ML-based fraud prediction"""
    try:
        if not ml_detector.is_trained:
            return jsonify({
                "status": "error",
                "message": "ML models not yet trained. Please train first."
            }), 400
        
        data = request.json
        
        transaction = Transaction(
            transaction_id=data.get('transaction_id', f"TX_{datetime.now().timestamp()}"),
            cardholder_id=data.get('cardholder_id', 'CH001'),
            amount=float(data.get('amount', 100)),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            merchant_name=data.get('merchant_name', 'Unknown'),
            merchant_category=MerchantCategory(data.get('merchant_category', 'retail')),
            transaction_type=TransactionType(data.get('transaction_type', 'purchase')),
            location=data.get('location', {'latitude': 40.7128, 'longitude': -74.0060}),
            mcc_code=data.get('mcc_code', '5310'),
            country=data.get('country', 'USA')
        )
        
        prediction = ml_detector.predict_fraud_probability(transaction)
        
        return jsonify({
            "status": "success",
            "prediction": prediction
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/ml-train', methods=['POST'])
def api_ml_train():
    """Train ML models"""
    try:
        data = request.json
        num_samples = data.get('num_samples', 20)
        
        # Generate synthetic training data
        training_data = []
        for i in range(num_samples):
            transaction = Transaction(
                transaction_id=f"TRAIN_{i}",
                cardholder_id="CH001",
                amount=50 + i * 5,
                timestamp=datetime.now() - timedelta(days=i),
                merchant_name=f"Merchant_{i % 5}",
                merchant_category=MerchantCategory.RETAIL,
                transaction_type=TransactionType.PURCHASE,
                location={"latitude": 40.7128, "longitude": -74.0060},
                mcc_code="5310",
                country="USA"
            )
            
            # Label: first half normal, second half fraud
            label = 1 if i >= num_samples // 2 else 0
            training_data.append((transaction, label))
        
        result = ml_detector.train_models(training_data, verbose=False)
        
        return jsonify({
            "status": "success",
            "message": "Models trained successfully",
            "training_result": result
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get system statistics"""
    try:
        total_txs = len(history.transactions)
        
        return jsonify({
            "status": "success",
            "statistics": {
                "total_transactions": total_txs,
                "unique_cardholders": len(set(t.cardholder_id for t in history.transactions)),
                "total_amount": sum(t.amount for t in history.transactions),
                "avg_transaction": (sum(t.amount for t in history.transactions) / total_txs) if total_txs > 0 else 0,
                "ml_models_trained": ml_detector.is_trained
            }
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/cardholder/<cardholder_id>', methods=['GET'])
def api_cardholder_info(cardholder_id):
    """Get cardholder information"""
    try:
        cardholder_txs = history.get_transactions_by_cardholder(cardholder_id)
        
        if not cardholder_txs:
            return jsonify({"status": "error", "message": "Cardholder not found"}), 404
        
        return jsonify({
            "status": "success",
            "cardholder_id": cardholder_id,
            "transaction_count": len(cardholder_txs),
            "total_amount": sum(t.amount for t in cardholder_txs),
            "avg_transaction": sum(t.amount for t in cardholder_txs) / len(cardholder_txs),
            "merchants": list(set(t.merchant_name for t in cardholder_txs)),
            "countries": list(set(t.country for t in cardholder_txs))
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engine_ready": engine is not None,
        "ml_ready": ml_detector is not None
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({"status": "error", "message": "Internal server error"}), 500


# ==================== STARTUP ====================

if __name__ == '__main__':
    print("Initializing Fraud Detection System...")
    initialize_system()
    
    print("\n" + "="*80)
    print("CREDIT CARD FRAUD DETECTION - WEB APPLICATION".center(80))
    print("="*80)
    print("\n✓ Flask server starting...")
    print("✓ Visit: http://localhost:5000")
    print("✓ API Documentation: http://localhost:5000/api/health")
    print("\n" + "="*80 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
