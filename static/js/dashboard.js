// Dashboard page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadDashboardData);
    }

    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
});

async function loadDashboardData() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.status === 'success') {
            updateDashboard(data.stats);
            updateSystemStatus(data.stats);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateDashboard(stats) {
    // Update stat cards
    const totalTransactions = document.getElementById('totalTransactions');
    const uniqueCardholders = document.getElementById('uniqueCardholders');
    const totalAmount = document.getElementById('totalAmount');
    const avgTransaction = document.getElementById('avgTransaction');

    if (totalTransactions) {
        totalTransactions.textContent = stats.total_transactions || 0;
    }

    if (uniqueCardholders) {
        uniqueCardholders.textContent = stats.unique_cardholders || 0;
    }

    if (totalAmount) {
        const amount = (stats.total_amount || 0).toFixed(2);
        totalAmount.textContent = '$' + amount;
    }

    if (avgTransaction) {
        const avg = (stats.avg_transaction_amount || 0).toFixed(2);
        avgTransaction.textContent = '$' + avg;
    }

    // Update high-risk transactions
    const highRiskDiv = document.getElementById('highRiskTransactions');
    if (highRiskDiv && stats.high_risk_transactions) {
        const count = stats.high_risk_transactions.length;
        const html = `
            <div style="background: white; border-radius: 0.5rem; padding: 1.5rem;">
                <div style="font-weight: bold; color: #ef4444; margin-bottom: 1rem;">
                    🚨 HIGH-RISK TRANSACTIONS (${count})
                </div>
                ${count > 0 ? `
                    <div style="max-height: 300px; overflow-y: auto;">
                        ${stats.high_risk_transactions.map((tx, idx) => `
                            <div style="padding: 1rem; border-bottom: 1px solid #f3f4f6; font-size: 0.9rem;">
                                <div style="font-weight: bold;">#${idx + 1}: ${tx.merchant_name}</div>
                                <div style="color: #6b7280; margin-top: 0.5rem;">
                                    Amount: $${tx.amount.toFixed(2)} | Score: ${(tx.fraud_score * 100).toFixed(1)}%
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div style="color: #6b7280;">No high-risk transactions detected</div>
                `}
            </div>
        `;
        highRiskDiv.innerHTML = html;
    }

    // Update daily statistics
    const dailyStatsDiv = document.getElementById('dailyStats');
    if (dailyStatsDiv && stats.daily_stats) {
        const html = `
            <div style="background: white; border-radius: 0.5rem; padding: 1.5rem;">
                <div style="font-weight: bold; margin-bottom: 1rem;">DAILY SUMMARY</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; font-size: 0.9rem;">
                    <div>
                        <div style="color: #6b7280;">Transactions Today</div>
                        <div style="font-weight: bold; font-size: 1.3rem; color: #2563eb;">
                            ${stats.daily_stats.transactions_today || 0}
                        </div>
                    </div>
                    <div>
                        <div style="color: #6b7280;">Today's Volume</div>
                        <div style="font-weight: bold; font-size: 1.3rem; color: #2563eb;">
                            $${(stats.daily_stats.volume_today || 0).toFixed(2)}
                        </div>
                    </div>
                    <div>
                        <div style="color: #6b7280;">Fraud Alerts</div>
                        <div style="font-weight: bold; font-size: 1.3rem; color: #ef4444;">
                            ${stats.daily_stats.fraud_alerts_today || 0}
                        </div>
                    </div>
                    <div>
                        <div style="color: #6b7280;">Avg Transaction</div>
                        <div style="font-weight: bold; font-size: 1.3rem; color: #2563eb;">
                            $${(stats.daily_stats.avg_transaction_today || 0).toFixed(2)}
                        </div>
                    </div>
                </div>
            </div>
        `;
        dailyStatsDiv.innerHTML = html;
    }
}

function updateSystemStatus(stats) {
    const statusDiv = document.getElementById('systemStatus');
    if (statusDiv) {
        const engineStatus = stats.fraud_engine_status || 'ACTIVE';
        const mlStatus = stats.ml_engine_status || 'READY';

        const html = `
            <div style="background: white; border-radius: 0.5rem; padding: 1.5rem;">
                <div style="font-weight: bold; margin-bottom: 1rem;">SYSTEM STATUS</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%; margin-right: 0.5rem;"></div>
                        <div>
                            <div style="color: #6b7280; font-size: 0.85rem;">Fraud Engine</div>
                            <div style="font-weight: bold; color: #10b981;">${engineStatus}</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%; margin-right: 0.5rem;"></div>
                        <div>
                            <div style="color: #6b7280; font-size: 0.85rem;">ML Engine</div>
                            <div style="font-weight: bold; color: #10b981;">${mlStatus}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        statusDiv.innerHTML = html;
    }
}
