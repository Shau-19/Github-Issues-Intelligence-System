import pandas as pd

# Load clustered data
df = pd.read_csv('data/clustered_issues_named.csv')

# Simple severity formula
def calculate_severity(row):
    score = 0
    
    # Error traces are critical
    if row['has_error_trace']:
        score += 5
    
    # Keyword severity
    score += row['keyword_severity']
    
    # User weight (enterprise = higher priority)
    score *= row['user_weight']
    
    return score

df['severity_score'] = df.apply(calculate_severity, axis=1)

# Cluster-level severity (average)
cluster_severity = df.groupby('cluster_name').agg({
    'severity_score': 'mean',
    'issue_title': 'count'
}).rename(columns={'issue_title': 'count'})

cluster_severity = cluster_severity.sort_values('severity_score', ascending=False)

print("📊 Cluster Severity Ranking\n")
print(cluster_severity)

# Save
df.to_csv('data/issues_with_severity.csv', index=False)
cluster_severity.to_csv('data/cluster_severity.csv')

print("\n✅ Saved: issues_with_severity.csv")