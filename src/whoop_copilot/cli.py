import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime, timedelta
import json

from .oauth_whoop import authorize_and_cache_tokens, get_valid_token
from .whoop_api import get_whoop_client
from .copilot_money import get_copilot_client
from .analyzer import get_analyzer

console = Console()

@click.group()
def cli():
    """Whoop + Copilot CLI - Combine fitness and financial data"""
    pass

@cli.command()
def hello():
    """Test command"""
    console.print('CLI is working :rocket:')

@cli.command()
def auth():
    """Authenticate with WHOOP API"""
    try:
        console.print("🔐 Starting WHOOP authentication...")
        tokens = authorize_and_cache_tokens()
        console.print("✅ Authentication successful!")
        console.print(f"Access token: {tokens.get('access_token', 'N/A')[:20]}...")
        console.print(f"Refresh token: {tokens.get('refresh_token', 'N/A')[:20]}...")
    except Exception as e:
        console.print(f"❌ Authentication failed: {e}", style="red")

@cli.command()
@click.option('--days', default=30, help='Number of days to look back')
def whoop_status(days):
    """Get current WHOOP status and recent data"""
    try:
        client = get_whoop_client()
        
        # Get user profile
        profile = client.get_user_profile()
        console.print(Panel(f"👤 {profile.get('first_name', 'User')} {profile.get('last_name', '')}", title="WHOOP Profile"))
        
        # Get recent data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        recovery_data = client.get_recovery_data(start_date, end_date)
        workout_data = client.get_workout_data(start_date, end_date)
        sleep_data = client.get_sleep_data(start_date, end_date)
        
        # Display summary
        table = Table(title=f"WHOOP Data Summary (Last {days} days)")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Recovery Scores", str(len(recovery_data)))
        table.add_row("Workouts", str(len(workout_data)))
        table.add_row("Sleep Sessions", str(len(sleep_data)))
        
        if recovery_data:
            recent_scores = [r.get('score', 0) for r in recovery_data[-7:] if r.get('score')]
            if recent_scores:
                table.add_row("Recent Avg Recovery", f"{sum(recent_scores)/len(recent_scores):.1f}%")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error fetching WHOOP data: {e}", style="red")

@cli.command()
@click.option('--days', default=30, help='Number of days to look back')
def copilot_status(days):
    """Get current Copilot Money status and recent data"""
    try:
        client = get_copilot_client()
        
        # Get accounts
        accounts = client.get_accounts()
        console.print(Panel(f"💰 {len(accounts)} Financial Accounts", title="Copilot Money"))
        
        # Get recent transactions
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        transactions = client.get_transactions(start_date, end_date, limit=100)
        
        # Display summary
        table = Table(title=f"Copilot Money Summary (Last {days} days)")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Accounts", str(len(accounts)))
        table.add_row("Recent Transactions", str(len(transactions)))
        
        if transactions:
            amounts = [t.get('amount', 0) for t in transactions if t.get('amount')]
            if amounts:
                table.add_row("Total Spending", f"${sum(amounts):.2f}")
                table.add_row("Avg Transaction", f"${sum(amounts)/len(amounts):.2f}")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error fetching Copilot data: {e}", style="red")

@cli.command()
@click.option('--days', default=30, help='Number of days to analyze')
@click.option('--output', help='Output file for detailed report (JSON)')
def analyze(days, output):
    """Analyze correlation between WHOOP fitness data and Copilot Money data"""
    try:
        console.print("🔍 Starting analysis...")
        
        analyzer = get_analyzer()
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        report = analyzer.generate_health_finance_report(start_date, end_date)
        
        # Display summary
        console.print(Panel(f"📊 Health & Finance Analysis ({start_date} to {end_date})", title="Analysis Results"))
        
        # Summary table
        summary_table = Table(title="Data Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        for key, value in report["summary"].items():
            summary_table.add_row(key.replace("_", " ").title(), str(value))
        
        console.print(summary_table)
        
        # Recovery analysis
        if "recovery_analysis" in report:
            recovery_table = Table(title="Recovery Analysis")
            recovery_table.add_column("Metric", style="cyan")
            recovery_table.add_column("Value", style="green")
            
            recovery = report["recovery_analysis"]
            recovery_table.add_row("Average Score", f"{recovery['average_score']:.1f}%")
            recovery_table.add_row("Best Score", f"{recovery['best_score']:.1f}%")
            recovery_table.add_row("Worst Score", f"{recovery['worst_score']:.1f}%")
            
            console.print(recovery_table)
        
        # Financial analysis
        if "financial_analysis" in report:
            finance_table = Table(title="Financial Analysis")
            finance_table.add_column("Metric", style="cyan")
            finance_table.add_column("Value", style="green")
            
            finance = report["financial_analysis"]
            finance_table.add_row("Total Spending", f"${finance['total_spending']:.2f}")
            finance_table.add_row("Average Transaction", f"${finance['average_transaction']:.2f}")
            finance_table.add_row("Largest Transaction", f"${finance['largest_transaction']:.2f}")
            
            console.print(finance_table)
        
        # Correlation insights
        if "correlations" in report:
            console.print("\n🔗 Correlation Insights:")
            
            # Spending vs Recovery
            spending_corr = report["correlations"]["spending_vs_recovery"]
            if "correlation" in spending_corr and spending_corr["correlation"] is not None:
                corr_value = spending_corr["correlation"]
                if abs(corr_value) > 0.3:
                    direction = "positive" if corr_value > 0 else "negative"
                    console.print(f"📈 Strong {direction} correlation between recovery and spending: {corr_value:.3f}")
                else:
                    console.print(f"📊 Weak correlation between recovery and spending: {corr_value:.3f}")
            
            # Workout impact
            workout_impact = report["correlations"]["workout_impact"]
            if "spending_difference" in workout_impact:
                diff = workout_impact["spending_difference"]
                if abs(diff) > 10:
                    direction = "more" if diff > 0 else "less"
                    console.print(f"💪 Workout days: {direction} spending (${abs(diff):.2f} difference)")
                else:
                    console.print(f"💪 Minimal spending difference on workout days: ${diff:.2f}")
        
        # Save detailed report if requested
        if output:
            with open(output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            console.print(f"💾 Detailed report saved to: {output}")
        
    except Exception as e:
        console.print(f"❌ Analysis failed: {e}", style="red")

@cli.command()
@click.option('--days', default=7, help='Number of days to look back')
def quick_insights(days):
    """Get quick insights from recent data"""
    try:
        console.print("💡 Generating quick insights...")
        
        analyzer = get_analyzer()
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get recent data
        whoop_data, copilot_data = analyzer.get_date_range_data(start_date, end_date)
        
        insights = []
        
        # WHOOP insights
        if whoop_data["recovery"]:
            recent_recovery = [r.get('score', 0) for r in whoop_data["recovery"][-3:] if r.get('score')]
            if recent_recovery:
                avg_recent = sum(recent_recovery) / len(recent_recovery)
                if avg_recent < 50:
                    insights.append("⚠️  Recent recovery scores are low - consider rest days")
                elif avg_recent > 80:
                    insights.append("🎯 Great recovery! You're ready for intense workouts")
        
        if whoop_data["workouts"]:
            workout_count = len(whoop_data["workouts"])
            if workout_count == 0:
                insights.append("🏃‍♂️ No workouts recorded - time to get moving!")
            elif workout_count >= 5:
                insights.append("🔥 High workout frequency - monitor recovery carefully")
        
        # Financial insights
        if copilot_data["transactions"]:
            recent_transactions = copilot_data["transactions"][-10:]
            amounts = [t.get('amount', 0) for t in recent_transactions if t.get('amount')]
            if amounts:
                avg_recent = sum(amounts) / len(amounts)
                if avg_recent > 100:
                    insights.append("💰 High recent spending - review budget")
                elif avg_recent < 20:
                    insights.append("💡 Low recent spending - good budget control")
        
        # Display insights
        if insights:
            console.print(Panel("\n".join(insights), title="Quick Insights"))
        else:
            console.print("📊 No specific insights for this time period")
        
    except Exception as e:
        console.print(f"❌ Error generating insights: {e}", style="red")

if __name__ == '__main__':
    cli()
