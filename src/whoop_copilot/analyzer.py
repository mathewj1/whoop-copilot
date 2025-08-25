import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json

from .whoop_api import WhoopAPI
from .copilot_money import CopilotMoneyAPI


class WhoopCopilotAnalyzer:
    """Analyzer for combining WHOOP fitness data with Copilot Money data"""
    
    def __init__(self):
        self.whoop_client = WhoopAPI()
        self.copilot_client = CopilotMoneyAPI()
    
    def get_date_range_data(self, 
                           start_date: str,
                           end_date: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Get data from both APIs for a date range"""
        # Get WHOOP data
        whoop_data = {
            "sleep": self.whoop_client.get_sleep_data(start_date, end_date),
            "recovery": self.whoop_client.get_recovery_data(start_date, end_date),
            "workouts": self.whoop_client.get_workout_data(start_date, end_date),
            "cycles": self.whoop_client.get_cycle_data(start_date, end_date)
        }
        
        # Get Copilot Money data
        copilot_data = {
            "transactions": self.copilot_client.get_transactions(start_date, end_date),
            "accounts": self.copilot_client.get_accounts(),
            "insights": self.copilot_client.get_insights(start_date, end_date)
        }
        
        return whoop_data, copilot_data
    
    def analyze_spending_vs_recovery(self, 
                                   start_date: str,
                                   end_date: str) -> Dict[str, Any]:
        """Analyze correlation between spending patterns and recovery scores"""
        whoop_data, copilot_data = self.get_date_range_data(start_date, end_date)
        
        # Create DataFrames for analysis
        recovery_df = pd.DataFrame(whoop_data["recovery"])
        transactions_df = pd.DataFrame(copilot_data["transactions"])
        
        if recovery_df.empty or transactions_df.empty:
            return {"error": "No data available for analysis"}
        
        # Convert dates and merge data
        if "date" in recovery_df.columns:
            recovery_df["date"] = pd.to_datetime(recovery_df["date"])
        if "date" in transactions_df.columns:
            transactions_df["date"] = pd.to_datetime(transactions_df["date"])
        
        # Group transactions by date and calculate daily spending
        daily_spending = transactions_df.groupby(transactions_df["date"].dt.date)["amount"].sum().reset_index()
        daily_spending["date"] = pd.to_datetime(daily_spending["date"])
        
        # Merge recovery and spending data
        merged_data = pd.merge(
            recovery_df[["date", "score"]],
            daily_spending[["date", "amount"]],
            on="date",
            how="outer"
        )
        
        # Calculate correlations
        correlation = merged_data["score"].corr(merged_data["amount"])
        
        # Group by recovery score ranges and analyze spending
        recovery_df["recovery_category"] = pd.cut(
            recovery_df["score"], 
            bins=[0, 33, 66, 100], 
            labels=["Low", "Medium", "High"]
        )
        
        spending_by_recovery = {}
        for category in ["Low", "Medium", "High"]:
            category_dates = recovery_df[recovery_df["recovery_category"] == category]["date"]
            if not category_dates.empty:
                category_transactions = transactions_df[
                    transactions_df["date"].isin(category_dates)
                ]
                spending_by_recovery[category] = {
                    "total_spending": category_transactions["amount"].sum(),
                    "avg_daily_spending": category_transactions["amount"].mean(),
                    "transaction_count": len(category_transactions)
                }
        
        return {
            "correlation": correlation,
            "spending_by_recovery": spending_by_recovery,
            "data_points": len(merged_data),
            "date_range": {"start": start_date, "end": end_date}
        }
    
    def analyze_workout_impact_on_spending(self,
                                          start_date: str,
                                          end_date: str) -> Dict[str, Any]:
        """Analyze how workouts affect spending patterns"""
        whoop_data, copilot_data = self.get_date_range_data(start_date, end_date)
        
        workouts_df = pd.DataFrame(whoop_data["workouts"])
        transactions_df = pd.DataFrame(copilot_data["transactions"])
        
        if workouts_df.empty or transactions_df.empty:
            return {"error": "No data available for analysis"}
        
        # Convert dates
        if "date" in workouts_df.columns:
            workouts_df["date"] = pd.to_datetime(workouts_df["date"])
        if "date" in transactions_df.columns:
            transactions_df["date"] = pd.to_datetime(transactions_df["date"])
        
        # Analyze spending on workout vs non-workout days
        workout_dates = set(workouts_df["date"].dt.date)
        
        workout_day_spending = []
        non_workout_day_spending = []
        
        for date in transactions_df["date"].dt.date.unique():
            daily_transactions = transactions_df[transactions_df["date"].dt.date == date]
            daily_total = daily_transactions["amount"].sum()
            
            if date in workout_dates:
                workout_day_spending.append(daily_total)
            else:
                non_workout_day_spending.append(daily_total)
        
        analysis = {
            "workout_days": {
                "count": len(workout_day_spending),
                "avg_spending": sum(workout_day_spending) / len(workout_day_spending) if workout_day_spending else 0,
                "total_spending": sum(workout_day_spending)
            },
            "non_workout_days": {
                "count": len(non_workout_day_spending),
                "avg_spending": sum(non_workout_day_spending) / len(non_workout_day_spending) if non_workout_day_spending else 0,
                "total_spending": sum(non_workout_day_spending)
            },
            "date_range": {"start": start_date, "end": end_date}
        }
        
        # Calculate difference
        if workout_day_spending and non_workout_day_spending:
            analysis["spending_difference"] = (
                analysis["workout_days"]["avg_spending"] - 
                analysis["non_workout_days"]["avg_spending"]
            )
        
        return analysis
    
    def generate_health_finance_report(self,
                                     start_date: str,
                                     end_date: str) -> Dict[str, Any]:
        """Generate comprehensive health and finance correlation report"""
        whoop_data, copilot_data = self.get_date_range_data(start_date, end_date)
        
        # Basic metrics
        report = {
            "date_range": {"start": start_date, "end": end_date},
            "summary": {
                "sleep_sessions": len(whoop_data["sleep"]),
                "workouts": len(whoop_data["workouts"]),
                "recovery_scores": len(whoop_data["recovery"]),
                "transactions": len(copilot_data["transactions"]),
                "accounts": len(copilot_data["accounts"])
            }
        }
        
        # Recovery analysis
        if whoop_data["recovery"]:
            recovery_scores = [r.get("score", 0) for r in whoop_data["recovery"] if r.get("score")]
            if recovery_scores:
                report["recovery_analysis"] = {
                    "average_score": sum(recovery_scores) / len(recovery_scores),
                    "best_score": max(recovery_scores),
                    "worst_score": min(recovery_scores),
                    "score_distribution": {
                        "low": len([s for s in recovery_scores if s <= 33]),
                        "medium": len([s for s in recovery_scores if 33 < s <= 66]),
                        "high": len([s for s in recovery_scores if s > 66])
                    }
                }
        
        # Financial analysis
        if copilot_data["transactions"]:
            transactions_df = pd.DataFrame(copilot_data["transactions"])
            if "amount" in transactions_df.columns:
                amounts = transactions_df["amount"].dropna()
                if not amounts.empty:
                    report["financial_analysis"] = {
                        "total_spending": amounts.sum(),
                        "average_transaction": amounts.mean(),
                        "largest_transaction": amounts.max(),
                        "transaction_count": len(amounts)
                    }
        
        # Add correlation analyses
        report["correlations"] = {
            "spending_vs_recovery": self.analyze_spending_vs_recovery(start_date, end_date),
            "workout_impact": self.analyze_workout_impact_on_spending(start_date, end_date)
        }
        
        return report


def get_analyzer() -> WhoopCopilotAnalyzer:
    """Get a configured analyzer instance"""
    return WhoopCopilotAnalyzer()
