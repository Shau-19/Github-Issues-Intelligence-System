import pandas as pd

df = pd.read_csv('data/issues_with_severity.csv')
df['created_at'] = pd.to_datetime(df['created_at'])

# Split data: first half vs second half
mid_date = df['created_at'].median()
early = df[df['created_at'] < mid_date]
late = df[df['created_at'] >= mid_date]

# Cluster distribution shift
early_dist = early['cluster_name'].value_counts(normalize=True)
late_dist = late['cluster_name'].value_counts(normalize=True)

print("🔍 CLUSTER DRIFT DETECTION\n")

for cluster in early_dist.index:
    if cluster in late_dist.index:
        change = (late_dist[cluster] - early_dist[cluster]) * 100
        
        if abs(change) > 1:  # >2% change is notable
            emoji = "📈" if change > 0 else "📉"
            print(f"{emoji} {cluster}")
            print(f"   Early: {early_dist[cluster]*100:.1f}%")
            print(f"   Late: {late_dist[cluster]*100:.1f}%")
            print(f"   Change: {change:+.1f}%\n")

print("✅ Drift analysis complete")