#!/usr/bin/env python3
"""
DataAnalystAgent Examples
==========================

Demonstrates statistical analysis, trend detection,
anomaly detection, and automated insights.
"""

import random
from agentic_ai.agents.data_analyst import DataAnalystAgent


def example_statistical_analysis():
    """Example: Statistical analysis."""
    print("=" * 70)
    print("Example 1: Statistical Analysis")
    print("=" * 70)
    print()
    
    analyst = DataAnalystAgent()
    
    # Create dataset
    print("Creating dataset...")
    dataset = analyst.register_dataset(
        name="E-commerce Sales",
        source="database",
        columns=['date', 'revenue', 'customers', 'orders', 'avg_order_value'],
        row_count=365,
    )
    
    print(f"  Dataset: {dataset.name}")
    print(f"  Columns: {', '.join(dataset.columns)}")
    print()
    
    # Generate sample data
    print("Loading data...")
    data = []
    for i in range(365):
        data.append({
            'date': f"2025-{(i//30)+1:02d}-{(i%30)+1:02d}",
            'revenue': float(random.randint(5000, 20000)),
            'customers': float(random.randint(100, 500)),
            'orders': float(random.randint(200, 800)),
            'avg_order_value': float(random.randint(20, 50)),
        })
    
    analyst.load_data(dataset.dataset_id, data)
    print(f"  Loaded {len(data)} rows")
    print()
    
    # Calculate statistics
    print("Calculating statistics for 'revenue'...")
    stats = analyst.calculate_statistics(dataset.dataset_id, 'revenue')
    
    print(f"  Count: {stats['count']}")
    print(f"  Mean: ${stats['mean']:,.2f}")
    print(f"  Median: ${stats['median']:,.2f}")
    print(f"  Std Dev: ${stats['std_dev']:,.2f}")
    print(f"  Min: ${stats['min']:,.2f}")
    print(f"  Max: ${stats['max']:,.2f}")
    print(f"  P25: ${stats['p25']:,.2f}")
    print(f"  P75: ${stats['p75']:,.2f}")
    print(f"  P95: ${stats['p95']:,.2f}")


def example_correlation_analysis():
    """Example: Correlation analysis."""
    print("\n" + "=" * 70)
    print("Example 2: Correlation Analysis")
    print("=" * 70)
    print()
    
    analyst = DataAnalystAgent()
    
    # Create dataset with correlated data
    dataset = analyst.register_dataset(
        name="Marketing Performance",
        source="analytics",
        columns=['ad_spend', 'website_traffic', 'conversions', 'revenue'],
    )
    
    # Generate correlated data
    data = []
    for i in range(100):
        ad_spend = float(random.randint(1000, 10000))
        traffic = ad_spend * 0.5 + random.randint(-100, 100)  # Correlated
        conversions = traffic * 0.03 + random.randint(-5, 5)  # Correlated
        revenue = conversions * 50 + random.randint(-50, 50)  # Correlated
        
        data.append({
            'ad_spend': ad_spend,
            'website_traffic': max(0, traffic),
            'conversions': max(0, conversions),
            'revenue': max(0, revenue),
        })
    
    analyst.load_data(dataset.dataset_id, data)
    
    print("Analyzing correlations...\n")
    
    # Check correlations
    pairs = [
        ('ad_spend', 'website_traffic'),
        ('website_traffic', 'conversions'),
        ('conversions', 'revenue'),
        ('ad_spend', 'revenue'),
    ]
    
    for col1, col2 in pairs:
        corr = analyst.detect_correlations(dataset.dataset_id, col1, col2)
        if 'error' not in corr:
            print(f"  {col1} ↔ {col2}")
            print(f"    Correlation: {corr['correlation']:.3f}")
            print(f"    Strength: {corr['strength']}")
            print(f"    Direction: {corr['direction']}")
            print()


def example_trend_detection():
    """Example: Trend detection."""
    print("=" * 70)
    print("Example 3: Trend Detection")
    print("=" * 70)
    print()
    
    analyst = DataAnalystAgent()
    
    # Create time-series dataset
    dataset = analyst.register_dataset(
        name="Monthly Revenue Trend",
        source="finance",
        columns=['month', 'revenue'],
    )
    
    # Generate trending data (growth)
    data = []
    base = 100000
    for i in range(24):  # 24 months
        month = f"2024-{(i//12)+1:02d}"
        revenue = base * (1.05 ** i) + random.randint(-5000, 5000)  # 5% growth
        data.append({'month': month, 'revenue': revenue})
    
    analyst.load_data(dataset.dataset_id, data)
    
    print("Analyzing revenue trend...\n")
    
    trend = analyst.detect_trends(dataset.dataset_id, 'revenue', 'month')
    
    print(f"  Trend: {trend['trend'].upper()}")
    print(f"  Slope: {trend['slope']:,.2f}")
    print(f"  Growth Rate: {trend['growth_rate_percent']:.1f}%")
    print(f"  Start Value: ${trend['start_value']:,.0f}")
    print(f"  End Value: ${trend['end_value']:,.0f}")
    print(f"  Data Points: {trend['data_points']}")


def example_anomaly_detection():
    """Example: Anomaly detection."""
    print("\n" + "=" * 70)
    print("Example 4: Anomaly Detection")
    print("=" * 70)
    print()
    
    analyst = DataAnalystAgent()
    
    # Create dataset with anomalies
    dataset = analyst.register_dataset(
        name="Daily Transactions",
        source="payments",
        columns=['date', 'transaction_count'],
    )
    
    # Generate data with outliers
    data = []
    for i in range(100):
        count = random.randint(800, 1200)  # Normal range
        if i in [25, 50, 75]:  # Inject anomalies
            count = random.choice([50, 3000])  # Very low or very high
        data.append({'date': f"2025-01-{i+1:02d}", 'transaction_count': float(count)})
    
    analyst.load_data(dataset.dataset_id, data)
    
    print("Detecting anomalies (z-score > 2.0)...\n")
    
    anomalies = analyst.detect_anomalies(dataset.dataset_id, 'transaction_count', threshold=2.0)
    
    if anomalies:
        print(f"  Found {len(anomalies)} anomalies:\n")
        for anomaly in anomalies:
            deviation = "↑ ABOVE" if anomaly['deviation'] == 'above' else "↓ BELOW"
            print(f"  [{deviation}] Index {anomaly['index']}: {anomaly['value']:.0f} (z-score: {anomaly['z_score']:.2f})")
    else:
        print("  No anomalies detected")


def example_automated_insights():
    """Example: Automated insights generation."""
    print("\n" + "=" * 70)
    print("Example 5: Automated Insights")
    print("=" * 70)
    print()
    
    analyst = DataAnalystAgent()
    
    # Create comprehensive dataset
    dataset = analyst.register_dataset(
        name="SaaS Metrics",
        source="analytics",
        columns=['mrr', 'customers', 'churn_rate', 'cac', 'ltv'],
    )
    
    # Generate realistic SaaS data
    data = []
    for i in range(50):
        mrr = float(random.randint(50000, 150000))
        customers = float(mrr / 50)  # ~$50/customer
        churn = random.uniform(0.02, 0.08)  # 2-8%
        cac = float(random.randint(100, 300))
        ltv = float(mrr / customers * 12)  # 12-month LTV
        
        data.append({
            'mrr': mrr,
            'customers': customers,
            'churn_rate': churn,
            'cac': cac,
            'ltv': ltv,
        })
    
    analyst.load_data(dataset.dataset_id, data)
    
    print("Generating automated insights...\n")
    
    analysis = analyst.generate_insights(dataset.dataset_id)
    
    print(f"Analysis: {analysis.name}")
    print(f"\nInsights ({len(analysis.insights)}):")
    for insight in analysis.insights[:5]:
        print(f"  • {insight}")
    
    print(f"\nRecommendations ({len(analysis.recommendations)}):")
    for rec in analysis.recommendations:
        print(f"  • {rec}")


def example_report_generation():
    """Example: Report generation."""
    print("\n" + "=" * 70)
    print("Example 6: Report Generation")
    print("=" * 70)
    print()
    
    analyst = DataAnalystAgent()
    
    # Create datasets
    q1 = analyst.register_dataset("Q1 Sales", "database", ['month', 'revenue', 'profit'])
    q2 = analyst.register_dataset("Q2 Sales", "database", ['month', 'revenue', 'profit'])
    
    # Load data
    q1_data = [{'month': f"2025-0{i}", 'revenue': float(100000 * (i+1)), 'profit': float(20000 * i)} for i in range(1, 4)]
    q2_data = [{'month': f"2025-0{i}", 'revenue': float(120000 * i), 'profit': float(25000 * i)} for i in range(4, 7)]
    
    analyst.load_data(q1.dataset_id, q1_data)
    analyst.load_data(q2.dataset_id, q2_data)
    
    print("Generating quarterly report...\n")
    
    report = analyst.generate_report(
        name="H1 2025 Sales Report",
        title="First Half 2025 Sales Analysis",
        dataset_ids=[q1.dataset_id, q2.dataset_id],
    )
    
    print(f"Report: {report.title}")
    print(f"Generated: {report.generated_at}")
    print(f"\nSections: {len(report.sections)}")
    
    for section in report.sections:
        print(f"\n  {section['dataset_name']}:")
        print(f"    Source: {section['source']}")
        print(f"    Rows: {section['row_count']}")
        if 'statistics' in section:
            print(f"    Columns analyzed: {len(section['statistics'])}")


def main():
    """Run all Data Analyst examples."""
    print("\n" + "=" * 70)
    print("DataAnalystAgent - Comprehensive Examples")
    print("=" * 70)
    
    example_statistical_analysis()
    example_correlation_analysis()
    example_trend_detection()
    example_anomaly_detection()
    example_automated_insights()
    example_report_generation()
    
    print("\n" + "=" * 70)
    print("All examples complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  - Connect to your data warehouse")
    print("  - Schedule automated reports")
    print("  - Set up anomaly alerts")
    print("  - Integrate with BI tools")
    print()


if __name__ == "__main__":
    main()
