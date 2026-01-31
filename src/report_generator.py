"""
Advanced Fraud Analysis Report Generator
Creates detailed reports and statistics on fraud detection
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict
from src.transaction import Transaction, TransactionHistory, MerchantCategory, TransactionType
from src.analysis_engine import FraudAnalysisEngine, FraudAnalysisResult


class FraudAnalysisReportGenerator:
    """Generates detailed fraud analysis reports"""
    
    def __init__(self, engine: FraudAnalysisEngine, results: List[FraudAnalysisResult]):
        self.engine = engine
        self.results = results
    
    def generate_cardholder_report(self, cardholder_id: str) -> Dict:
        """Generate detailed report for specific cardholder"""
        cardholder_results = [
            r for r in self.results 
            if r.cardholder_id == cardholder_id
        ]
        
        if not cardholder_results:
            return {"error": f"No transactions found for {cardholder_id}"}
        
        high_risk = [r for r in cardholder_results if r.risk_level in ["HIGH", "CRITICAL"]]
        medium_risk = [r for r in cardholder_results if r.risk_level == "MEDIUM"]
        
        # Analyze fraud indicators
        indicator_stats = {}
        for result in cardholder_results:
            for indicator, (triggered, confidence) in result.fraud_indicators.items():
                if indicator not in indicator_stats:
                    indicator_stats[indicator] = {
                        "triggered_count": 0,
                        "total_count": 0,
                        "avg_confidence": 0,
                        "confidences": []
                    }
                indicator_stats[indicator]["total_count"] += 1
                if triggered:
                    indicator_stats[indicator]["triggered_count"] += 1
                indicator_stats[indicator]["confidences"].append(confidence)
        
        # Calculate averages
        for indicator in indicator_stats:
            stats = indicator_stats[indicator]
            stats["avg_confidence"] = sum(stats["confidences"]) / len(stats["confidences"])
            stats["trigger_rate"] = stats["triggered_count"] / stats["total_count"]
            del stats["confidences"]
        
        return {
            "cardholder_id": cardholder_id,
            "total_transactions": len(cardholder_results),
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "average_fraud_score": sum(r.fraud_score for r in cardholder_results) / len(cardholder_results),
            "max_fraud_score": max(r.fraud_score for r in cardholder_results),
            "min_fraud_score": min(r.fraud_score for r in cardholder_results),
            "fraud_indicators": indicator_stats,
            "high_risk_transactions": [
                {
                    "transaction_id": r.transaction_id,
                    "fraud_score": r.fraud_score,
                    "recommendation": r.recommendation
                }
                for r in high_risk
            ]
        }
    
    def generate_fraud_incident_report(self) -> Dict:
        """Generate report of all fraud incidents"""
        fraud_transactions = [
            r for r in self.results 
            if r.risk_level in ["HIGH", "CRITICAL"]
        ]
        
        incidents = []
        for result in fraud_transactions:
            triggered_indicators = [
                name for name, (triggered, _) in result.fraud_indicators.items()
                if triggered
            ]
            
            incidents.append({
                "transaction_id": result.transaction_id,
                "cardholder_id": result.cardholder_id,
                "fraud_score": result.fraud_score,
                "risk_level": result.risk_level,
                "recommendation": result.recommendation,
                "triggered_indicators": triggered_indicators,
                "timestamp": result.details.get("timestamp"),
                "amount": result.details.get("transaction_amount"),
                "merchant": result.details.get("merchant_name")
            })
        
        return {
            "total_incidents": len(incidents),
            "incidents": sorted(incidents, key=lambda x: x["fraud_score"], reverse=True)
        }
    
    def generate_indicator_analysis(self) -> Dict:
        """Analyze effectiveness of each fraud indicator"""
        indicator_data = {}
        
        for result in self.results:
            for indicator, (triggered, confidence) in result.fraud_indicators.items():
                if indicator not in indicator_data:
                    indicator_data[indicator] = {
                        "occurrences": 0,
                        "high_risk_correlation": 0,
                        "medium_risk_correlation": 0,
                        "avg_confidence_when_triggered": 0,
                        "confidence_values": []
                    }
                
                if triggered:
                    indicator_data[indicator]["occurrences"] += 1
                    if result.risk_level in ["HIGH", "CRITICAL"]:
                        indicator_data[indicator]["high_risk_correlation"] += 1
                    elif result.risk_level == "MEDIUM":
                        indicator_data[indicator]["medium_risk_correlation"] += 1
                    indicator_data[indicator]["confidence_values"].append(confidence)
        
        # Calculate effectiveness scores
        analysis = {}
        for indicator, data in indicator_data.items():
            if data["occurrences"] > 0:
                data["avg_confidence_when_triggered"] = (
                    sum(data["confidence_values"]) / len(data["confidence_values"])
                )
                data["effectiveness_score"] = (
                    (data["high_risk_correlation"] * 1.0 + 
                     data["medium_risk_correlation"] * 0.5) / 
                    data["occurrences"]
                )
            del data["confidence_values"]
            analysis[indicator] = data
        
        return {
            "total_indicators": len(analysis),
            "indicator_analysis": sorted(
                analysis.items(),
                key=lambda x: x[1]["effectiveness_score"],
                reverse=True
            )
        }
    
    def generate_timeline_analysis(self) -> Dict:
        """Analyze fraud patterns over time"""
        timeline = {}
        
        for result in self.results:
            timestamp = result.details.get("timestamp")
            if not timestamp:
                continue
            
            # Parse timestamp and get date
            try:
                dt = datetime.fromisoformat(timestamp)
                date_key = dt.date().isoformat()
            except:
                continue
            
            if date_key not in timeline:
                timeline[date_key] = {
                    "total_transactions": 0,
                    "high_risk_count": 0,
                    "medium_risk_count": 0,
                    "avg_fraud_score": 0,
                    "fraud_scores": []
                }
            
            timeline[date_key]["total_transactions"] += 1
            if result.risk_level in ["HIGH", "CRITICAL"]:
                timeline[date_key]["high_risk_count"] += 1
            elif result.risk_level == "MEDIUM":
                timeline[date_key]["medium_risk_count"] += 1
            timeline[date_key]["fraud_scores"].append(result.fraud_score)
        
        # Calculate averages
        for date_key in timeline:
            scores = timeline[date_key]["fraud_scores"]
            if scores:
                timeline[date_key]["avg_fraud_score"] = sum(scores) / len(scores)
            del timeline[date_key]["fraud_scores"]
        
        return {
            "dates_analyzed": len(timeline),
            "timeline": dict(sorted(timeline.items()))
        }
    
    def generate_merchant_analysis(self) -> Dict:
        """Analyze fraud patterns by merchant"""
        merchant_data = {}
        
        for result in self.results:
            merchant = result.details.get("merchant_name")
            if not merchant:
                continue
            
            if merchant not in merchant_data:
                merchant_data[merchant] = {
                    "transaction_count": 0,
                    "fraud_count": 0,
                    "avg_fraud_score": 0,
                    "fraud_scores": [],
                    "category": result.details.get("merchant_category")
                }
            
            merchant_data[merchant]["transaction_count"] += 1
            if result.risk_level in ["HIGH", "CRITICAL"]:
                merchant_data[merchant]["fraud_count"] += 1
            merchant_data[merchant]["fraud_scores"].append(result.fraud_score)
        
        # Calculate averages and fraud rate
        for merchant in merchant_data:
            data = merchant_data[merchant]
            if data["fraud_scores"]:
                data["avg_fraud_score"] = sum(data["fraud_scores"]) / len(data["fraud_scores"])
                data["fraud_rate"] = data["fraud_count"] / data["transaction_count"]
            del data["fraud_scores"]
        
        # Sort by fraud rate
        sorted_merchants = sorted(
            merchant_data.items(),
            key=lambda x: x[1].get("fraud_rate", 0),
            reverse=True
        )
        
        return {
            "total_merchants": len(merchant_data),
            "high_fraud_merchants": [m for m in sorted_merchants if m[1].get("fraud_rate", 0) > 0.5],
            "all_merchants": dict(sorted_merchants)
        }
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive fraud analysis report"""
        return {
            "report_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_transactions_analyzed": len(self.results),
                "critical_risk": sum(1 for r in self.results if r.risk_level == "CRITICAL"),
                "high_risk": sum(1 for r in self.results if r.risk_level == "HIGH"),
                "medium_risk": sum(1 for r in self.results if r.risk_level == "MEDIUM"),
                "low_risk": sum(1 for r in self.results if r.risk_level == "LOW"),
                "overall_avg_fraud_score": sum(r.fraud_score for r in self.results) / len(self.results) if self.results else 0
            },
            "fraud_incidents": self.generate_fraud_incident_report(),
            "indicator_effectiveness": self.generate_indicator_analysis(),
            "timeline_analysis": self.generate_timeline_analysis(),
            "merchant_analysis": self.generate_merchant_analysis()
        }


def print_beautiful_report(report: Dict):
    """Print report in beautiful formatted way"""
    print("\n" + "=" * 100)
    print("COMPREHENSIVE FRAUD ANALYSIS REPORT".center(100))
    print("=" * 100 + "\n")
    
    # Summary Section
    summary = report.get("summary", {})
    print("📊 SUMMARY STATISTICS")
    print("-" * 100)
    print(f"  Total Transactions Analyzed: {summary.get('total_transactions_analyzed', 0)}")
    print(f"  🔴 CRITICAL Risk: {summary.get('critical_risk', 0)}")
    print(f"  🟠 HIGH Risk: {summary.get('high_risk', 0)}")
    print(f"  🟡 MEDIUM Risk: {summary.get('medium_risk', 0)}")
    print(f"  🟢 LOW Risk: {summary.get('low_risk', 0)}")
    print(f"  Average Fraud Score: {summary.get('overall_avg_fraud_score', 0):.3f}")
    print()
    
    # Fraud Incidents
    incidents = report.get("fraud_incidents", {})
    if incidents.get("total_incidents", 0) > 0:
        print("⚠️  FRAUD INCIDENTS")
        print("-" * 100)
        print(f"  Total Incidents: {incidents.get('total_incidents', 0)}")
        print("\n  Top Incidents (by fraud score):")
        for incident in incidents.get("incidents", [])[:5]:
            print(f"\n    • Transaction ID: {incident.get('transaction_id')}")
            print(f"      Risk Level: {incident.get('risk_level')} | Score: {incident.get('fraud_score'):.3f}")
            print(f"      Merchant: {incident.get('merchant')} | Amount: ${incident.get('amount', 0):.2f}")
            print(f"      Indicators: {', '.join(incident.get('triggered_indicators', []))}")
        print()
    
    # Indicator Analysis
    indicators = report.get("indicator_effectiveness", {})
    print("🔍 FRAUD INDICATOR EFFECTIVENESS")
    print("-" * 100)
    for indicator, data in indicators.get("indicator_analysis", [])[:8]:
        print(f"  {indicator:30s}: Effectiveness={data.get('effectiveness_score', 0):.2f} | Occurrences={data.get('occurrences', 0)}")
    print()
    
    # Merchant Analysis
    merchants = report.get("merchant_analysis", {})
    print("🏪 HIGH FRAUD MERCHANT ANALYSIS")
    print("-" * 100)
    high_fraud = merchants.get("high_fraud_merchants", [])
    if high_fraud:
        for merchant_name, data in high_fraud[:5]:
            fraud_rate = data.get("fraud_rate", 0)
            print(f"  {merchant_name:40s}: Fraud Rate={fraud_rate:.1%} | Transactions={data.get('transaction_count', 0)}")
    else:
        print("  No merchants with high fraud rates detected")
    print()
    
    print("=" * 100 + "\n")


if __name__ == "__main__":
    # This would be used with actual results
    print("Report generator module loaded successfully")
    print("Use this module to generate detailed fraud analysis reports")
