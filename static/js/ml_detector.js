// ML Detector page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Training form
    const trainingForm = document.getElementById('trainingForm');
    if (trainingForm) {
        trainingForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const sampleCount = parseInt(document.getElementById('sampleCount').value) || 100;
            
            try {
                showTrainingStatus('Training in progress...');
                
                const response = await fetch('/api/ml-train', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        num_samples: sampleCount
                    })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    showTrainingStatus(`✓ Training completed! Accuracy: ${(data.accuracy * 100).toFixed(2)}%`, 'success');
                    displayModelMetrics(data);
                } else {
                    showTrainingStatus('Error: ' + data.message, 'error');
                }
            } catch (error) {
                showTrainingStatus('Error: ' + error.message, 'error');
            }
        });
    }

    // Prediction form
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        predictionForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = {
                cardholder_id: document.getElementById('pred_cardholder_id').value,
                amount: parseFloat(document.getElementById('pred_amount').value),
                merchant_name: document.getElementById('pred_merchant_name').value,
                merchant_category: document.getElementById('pred_merchant_category').value,
                country: document.getElementById('pred_country').value,
                timestamp: document.getElementById('pred_timestamp').value,
                transaction_id: `TX_${Date.now()}`,
                transaction_type: 'purchase',
                mcc_code: '5310',
                location: {
                    latitude: 40.7128,
                    longitude: -74.0060
                }
            };

            try {
                showPredictionStatus('Analyzing with ML models...');
                
                const response = await fetch('/api/ml-predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data.status === 'success') {
                    displayPredictionResults(data.prediction);
                    showPredictionStatus('', 'clear');
                } else {
                    showPredictionStatus('Error: ' + data.message, 'error');
                }
            } catch (error) {
                showPredictionStatus('Error: ' + error.message, 'error');
            }
        });

        // Set default timestamp to now
        const now = new Date().toISOString().slice(0, 16);
        document.getElementById('pred_timestamp').value = now;
    }
});

function showTrainingStatus(message, type = 'info') {
    const statusDiv = document.getElementById('trainingStatus');
    if (statusDiv) {
        const bgColor = type === 'success' ? '#d1fae5' : type === 'error' ? '#fee2e2' : '#dbeafe';
        const textColor = type === 'success' ? '#065f46' : type === 'error' ? '#7f1d1d' : '#1e40af';
        const borderColor = type === 'success' ? '#a7f3d0' : type === 'error' ? '#fecaca' : '#93c5fd';

        statusDiv.innerHTML = `
            <div style="background: ${bgColor}; border: 1px solid ${borderColor}; color: ${textColor}; padding: 1rem; border-radius: 0.5rem;">
                ${message}
            </div>
        `;
    }
}

function showPredictionStatus(message, type = 'info') {
    const statusDiv = document.getElementById('predictionStatus');
    if (statusDiv) {
        if (type === 'clear') {
            statusDiv.innerHTML = '';
            return;
        }

        const bgColor = type === 'success' ? '#d1fae5' : type === 'error' ? '#fee2e2' : '#dbeafe';
        const textColor = type === 'success' ? '#065f46' : type === 'error' ? '#7f1d1d' : '#1e40af';
        const borderColor = type === 'success' ? '#a7f3d0' : type === 'error' ? '#fecaca' : '#93c5fd';

        statusDiv.innerHTML = `
            <div style="background: ${bgColor}; border: 1px solid ${borderColor}; color: ${textColor}; padding: 1rem; border-radius: 0.5rem;">
                ${message}
            </div>
        `;
    }
}

function displayModelMetrics(data) {
    const metricsDiv = document.getElementById('modelMetrics');
    if (metricsDiv && data.metrics) {
        const metrics = data.metrics;
        const html = `
            <div style="background: white; border-radius: 0.5rem; padding: 1.5rem; margin-top: 1rem;">
                <div style="font-weight: bold; margin-bottom: 1rem;">MODEL PERFORMANCE</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    <div style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem;">
                        <div style="color: #6b7280; font-size: 0.85rem; margin-bottom: 0.25rem;">Accuracy</div>
                        <div style="font-weight: bold; font-size: 1.5rem; color: #2563eb;">
                            ${(metrics.accuracy * 100).toFixed(2)}%
                        </div>
                    </div>
                    <div style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem;">
                        <div style="color: #6b7280; font-size: 0.85rem; margin-bottom: 0.25rem;">Precision</div>
                        <div style="font-weight: bold; font-size: 1.5rem; color: #2563eb;">
                            ${(metrics.precision * 100).toFixed(2)}%
                        </div>
                    </div>
                    <div style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem;">
                        <div style="color: #6b7280; font-size: 0.85rem; margin-bottom: 0.25rem;">Recall</div>
                        <div style="font-weight: bold; font-size: 1.5rem; color: #2563eb;">
                            ${(metrics.recall * 100).toFixed(2)}%
                        </div>
                    </div>
                    <div style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem;">
                        <div style="color: #6b7280; font-size: 0.85rem; margin-bottom: 0.25rem;">F1-Score</div>
                        <div style="font-weight: bold; font-size: 1.5rem; color: #2563eb;">
                            ${(metrics.f1_score * 100).toFixed(2)}%
                        </div>
                    </div>
                </div>
            </div>
        `;
        metricsDiv.innerHTML = html;
    }
}

function displayPredictionResults(prediction) {
    const resultsDiv = document.getElementById('predictionResults');
    if (resultsDiv && prediction) {
        const fraudProb = prediction.fraud_probability || 0;
        const riskLevel = prediction.risk_level || 'UNKNOWN';
        
        const riskColors = {
            'LOW': { bg: '#d1fae5', text: '#065f46', emoji: '🟢' },
            'MEDIUM': { bg: '#fef3c7', text: '#92400e', emoji: '🟡' },
            'HIGH': { bg: '#fed7aa', text: '#9a3412', emoji: '🟠' },
            'CRITICAL': { bg: '#fee2e2', text: '#7f1d1d', emoji: '🔴' }
        };

        const riskStyle = riskColors[riskLevel] || { bg: '#f3f4f6', text: '#374151', emoji: '❓' };

        const html = `
            <div style="background: white; border-radius: 0.5rem; padding: 1.5rem; margin-top: 1rem;">
                <div style="font-weight: bold; margin-bottom: 1rem;">ML PREDICTION RESULT</div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: ${riskStyle.bg}; color: ${riskStyle.text}; padding: 1.5rem; border-radius: 0.5rem;">
                        <div style="font-size: 0.85rem; margin-bottom: 0.5rem;">Risk Level</div>
                        <div style="font-weight: bold; font-size: 1.3rem;">
                            ${riskStyle.emoji} ${riskLevel}
                        </div>
                    </div>
                    
                    <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem;">
                        <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 0.5rem;">Fraud Probability</div>
                        <div style="font-weight: bold; font-size: 1.3rem; color: #2563eb;">
                            ${(fraudProb * 100).toFixed(2)}%
                        </div>
                    </div>

                    ${prediction.logistic_probability ? `
                        <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem;">
                            <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 0.5rem;">Logistic Regression</div>
                            <div style="font-weight: bold; font-size: 1.3rem; color: #2563eb;">
                                ${(prediction.logistic_probability * 100).toFixed(2)}%
                            </div>
                        </div>
                    ` : ''}

                    ${prediction.forest_probability ? `
                        <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 0.5rem;">
                            <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 0.5rem;">Random Forest</div>
                            <div style="font-weight: bold; font-size: 1.3rem; color: #2563eb;">
                                ${(prediction.forest_probability * 100).toFixed(2)}%
                            </div>
                        </div>
                    ` : ''}
                </div>

                ${prediction.recommendation ? `
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; padding: 1rem; border-radius: 0.5rem; font-size: 0.9rem;">
                        <div style="color: #6b7280; margin-bottom: 0.5rem;">Recommendation:</div>
                        <div>${prediction.recommendation}</div>
                    </div>
                ` : ''}
            </div>
        `;

        resultsDiv.innerHTML = html;
    }
}
