// Analyze page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('transactionForm');
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
            showLoading();
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.status === 'success') {
                displayResults(data.analysis);
            } else {
                showError(data.message);
            }
        } catch (error) {
            showError('Error: ' + error.message);
        }
    });
});

function showLoading() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div class="spinner"></div><p>Analyzing transaction...</p>';
}

function displayResults(analysis) {
    const resultsDiv = document.getElementById('results');
    
    const riskColors = {
        'LOW': '#10b981',
        'MEDIUM': '#f59e0b',
        'HIGH': '#f97316',
        'CRITICAL': '#ef4444'
    };

    const riskEmojis = {
        'LOW': '🟢',
        'MEDIUM': '🟡',
        'HIGH': '🟠',
        'CRITICAL': '🔴'
    };

    const indicatorRows = Object.entries(analysis.fraud_indicators).map(([key, value]) => {
        const triggered = value.triggered ? 'TRIGGERED' : 'OK';
        const status = value.triggered ? '✓' : '✗';
        return `
            <tr>
                <td>${key}</td>
                <td>${status} ${triggered}</td>
                <td>${(value.confidence * 100).toFixed(1)}%</td>
            </tr>
        `;
    }).join('');

    const html = `
        <div style="background: white; border-radius: 0.5rem; padding: 2rem;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem;">
                    <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">TRANSACTION ID</div>
                    <div style="font-weight: bold;">${analysis.transaction_id}</div>
                </div>
                <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem;">
                    <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">RISK LEVEL</div>
                    <div style="font-weight: bold; color: ${riskColors[analysis.risk_level]}; font-size: 1.2rem;">
                        ${riskEmojis[analysis.risk_level]} ${analysis.risk_level}
                    </div>
                </div>
                <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem;">
                    <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">FRAUD SCORE</div>
                    <div style="font-weight: bold; font-size: 1.5rem; color: #2563eb;">
                        ${(analysis.fraud_score * 100).toFixed(2)}%
                    </div>
                </div>
            </div>

            <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 2rem;">
                <div style="font-weight: bold; margin-bottom: 0.5rem;">RECOMMENDATION</div>
                <div style="color: #374151;">${analysis.recommendation}</div>
            </div>

            <div style="margin-bottom: 2rem;">
                <div style="font-weight: bold; margin-bottom: 1rem;">FRAUD INDICATORS</div>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f3f4f6;">
                            <th style="padding: 1rem; text-align: left; border-bottom: 1px solid #e5e7eb;">Indicator</th>
                            <th style="padding: 1rem; text-align: left; border-bottom: 1px solid #e5e7eb;">Status</th>
                            <th style="padding: 1rem; text-align: left; border-bottom: 1px solid #e5e7eb;">Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${indicatorRows}
                    </tbody>
                </table>
            </div>

            <div style="background: white; border: 1px solid #e5e7eb; padding: 1.5rem; border-radius: 0.5rem;">
                <div style="font-weight: bold; margin-bottom: 1rem;">TRANSACTION DETAILS</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; font-size: 0.95rem;">
                    <div><span style="color: #6b7280;">Amount:</span> $${analysis.details.transaction_amount.toFixed(2)}</div>
                    <div><span style="color: #6b7280;">Merchant:</span> ${analysis.details.merchant_name}</div>
                    <div><span style="color: #6b7280;">Category:</span> ${analysis.details.merchant_category}</div>
                    <div><span style="color: #6b7280;">Country:</span> ${analysis.details.country}</div>
                    <div><span style="color: #6b7280;">Timestamp:</span> ${new Date(analysis.details.timestamp).toLocaleString()}</div>
                </div>
            </div>
        </div>
    `;

    resultsDiv.innerHTML = html;
}

function showError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<div style="color: #7f1d1d; background: #fee2e2; border: 1px solid #fecaca; padding: 1rem; border-radius: 0.5rem;">⚠️ ${message}</div>`;
}
