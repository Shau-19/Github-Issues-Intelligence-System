import pandas as pd

# Load data
df = pd.read_csv('data/issues_with_severity.csv')
decisions = pd.read_csv('data/cluster_severity.csv', index_col=0)

print("="*70)
print("WEEK 3: DECISION INTELLIGENCE REPORT")
print("="*70)

# Critical clusters (severity > 5)
print("\n🔴 CRITICAL CLUSTERS\n")
critical = decisions[decisions['severity_score'] > 5]
for name, row in critical.iterrows():
    print(f"  • {name}")
    print(f"    {row['count']} issues, severity {row['severity_score']:.1f}\n")

# High impact (top 5)
print("💥 TOP 5 IMPACT CLUSTERS\n")
decisions['impact'] = decisions['severity_score'] * decisions['count']
top5 = decisions.nlargest(5, 'impact')

for name, row in top5.iterrows():
    print(f"  • {name}")
    print(f"    Impact: {row['impact']:.0f}")
    print(f"    ({row['severity_score']:.1f} severity × {row['count']} issues)\n")

# Stats
total_critical = df[df['severity_score'] > 5].shape[0]
total_issues = len(df)

print("📊 SUMMARY\n")
print(f"  Total issues: {total_issues}")
print(f"  Critical issues: {total_critical} ({total_critical/total_issues*100:.1f}%)")
print(f"  Clusters analyzed: {len(decisions)}")
print(f"  High-severity clusters: {len(critical)}")

print("\n" + "="*70)
print("✅ WEEK 3 COMPLETE")
print("="*70)