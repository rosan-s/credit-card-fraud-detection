// Main JavaScript

// Analyze transaction form
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('transactionForm');
    if (form) {
        // Set default timestamp to now
        const now = new Date().toISOString().slice(0, 16);
        document.getElementById('timestamp').value = now;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                cardholder_id: document.getElementById('cardholder_id').value,
                amount: parseFloat(document.getElementById('amount').value),
                merchant_name: document.getElementById('merchant_name').value,
                merchant_category: document.getElementById('merchant_category').value,
                country: document.getElementById('country').value,
                timestamp: document.getElementById('timestamp').value,
                transaction_id: `TX_${Date.now()}`,
                transaction_type: 'purchase',
                mcc_code: '5310',
                location: {
                    latitude: 40.7128,
                    longitude: -74.0060
                }
            };

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data.status === 'success') {
                    displayAnalysisResults(data.analysis);
                } else {
                    showError(data.message);
                }
            } catch (error) {
                showError('Error analyzing transaction: ' + error.message);
            }
        });
    }
});

function displayAnalysisResults(analysis) {
    const resultsDiv = document.getElementById('results');
    
    const riskColor = {
        'LOW': '#10b981',
        'MEDIUM': '#f59e0b',
        'HIGH': '#f97316',
        'CRITICAL': '#ef4444'
    };

    const riskEmoji = {
        'LOW': '🟢',
        'MEDIUM': '🟡',
        'HIGH': '🟠',
        'CRITICAL': '🔴'
    };

    const html = `
        <div class="result-card">
            <div class="result-title">Transaction ID</div>
            <div>${analysis.transaction_id}</div>
        </div>
        <div class="result-card">
            <div class="result-title">Risk Level</div>
            <div style="color: ${riskColor[analysis.risk_level]}; font-size: 1.5rem;">
                ${riskEmoji[analysis.risk_level]} ${analysis.risk_level}
            </div>
        </div>
        <div class="result-card">
            <div class="result-title">Fraud Score</div>
            <div class="result-value">${(analysis.fraud_score * 100).toFixed(2)}%</div>
        </div>
        <div class="result-card">
            <div class="result-title">Recommendation</div>
            <div>${analysis.recommendation}</div>
        </div>
        <div class="result-card">
            <div class="result-title">Triggered Indicators</div>
            <div>
                ${Object.entries(analysis.fraud_indicators).map(([key, value]) => 
                    `<div>${key}: ${value.triggered ? '✓ TRIGGERED' : '✗ OK'} (${(value.confidence * 100).toFixed(0)}%)</div>`
                ).join('')}
            </div>
        </div>
    `;

    resultsDiv.innerHTML = html;
}

function showError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<div style="color: #dc2626; padding: 1rem; background: #fee2e2; border-radius: 0.5rem;">Error: ${message}</div>`;
}

// Dashboard refresh
function refreshDashboard() {
    loadDashboardStats();
}

function loadDashboardStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const stats = data.statistics;
                document.getElementById('total-txs').textContent = stats.total_transactions;
                document.getElementById('unique-holders').textContent = stats.unique_cardholders;
                document.getElementById('total-amount').textContent = '$' + stats.total_amount.toFixed(2);
                document.getElementById('avg-transaction').textContent = '$' + stats.avg_transaction.toFixed(2);
                
                document.getElementById('ml-status').textContent = stats.ml_models_trained ? '✓ Trained' : '✗ Not Trained';
            }
        })
        .catch(error => console.error('Error loading stats:', error));
}

// Load stats on page load
window.addEventListener('load', function() {
    if (document.getElementById('total-txs')) {
        loadDashboardStats();
    }
});
