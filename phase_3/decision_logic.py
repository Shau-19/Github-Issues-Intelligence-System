import pandas as pd

cluster_severity = pd.read_csv('data/cluster_severity.csv')

# Simple decision rules
def decide_action(row):
    severity = row['severity_score']
    count = row['count']
    
    if severity > 10:
        return "🔴 IMMEDIATE FIX"
    elif severity > 5:
        return "🟡 INVESTIGATE"
    elif count > 1000:
        return "🔵 AUTOMATE RESPONSE"
    else:
        return "🟢 MONITOR"

cluster_severity['action'] = cluster_severity.apply(decide_action, axis=1)

# Impact score (severity × frequency)
cluster_severity['impact'] = cluster_severity['severity_score'] * cluster_severity['count']
cluster_severity = cluster_severity.sort_values('impact', ascending=False)

print("💼 Decision Matrix\n")
print(cluster_severity[['severity_score', 'count', 'impact', 'action']])

cluster_severity.to_csv('data/decisions.csv')
print("\n✅ Saved: decisions.csv")