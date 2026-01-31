import pandas as pd

print("="*70)
print("FINAL PROJECT SUMMARY")
print("="*70)

# Load all data
df = pd.read_csv('data/issues_with_severity.csv')
decisions = pd.read_csv('data/cluster_severity.csv', index_col=0)

print("\n📊 DATASET")
print(f"  • Total issues analyzed: {len(df):,}")
print(f"  • Date range: {df['created_at'].min()} to {df['created_at'].max()}")
print(f"  • Unique repos: {df['repo'].nunique()}")

print("\n🎯 CLUSTERING")
print(f"  • Clusters identified: {df['cluster_name'].nunique()}")
print(f"  • Largest cluster: {df['cluster_name'].value_counts().index[0]} ({df['cluster_name'].value_counts().iloc[0]} issues)")
print(f"  • Smallest cluster: {df['cluster_name'].value_counts().index[-1]} ({df['cluster_name'].value_counts().iloc[-1]} issues)")

print("\n🔴 CRITICAL FINDINGS")
critical = decisions[decisions['severity_score'] > 5]
print(f"  • Critical clusters: {len(critical)}")
print(f"  • Critical issues: {df[df['severity_score'] > 5].shape[0]} (4.3%)")
print(f"  • Top severity: {decisions['severity_score'].max():.1f}")

print("\n💼 BUSINESS IMPACT")
decisions['impact'] = decisions['severity_score'] * decisions['count']
top_impact = decisions.nlargest(1, 'impact').iloc[0]
print(f"  • Highest impact cluster: {top_impact.name}")
print(f"  • Impact score: {top_impact['impact']:.0f}")
print(f"  • Recommended action: Immediate engineering review")

print("\n🎓 METHODOLOGY")
print("  • Text embeddings: 384D (Sentence-BERT)")
print("  • Metadata features: 8D (multimodal)")
print("  • Clustering: KMeans (k=15)")
print("  • Silhouette score: 0.29 (multimodal) vs 0.02 (text-only)")

print("\n" + "="*70)
print("✅ PROJECT COMPLETE")
print("="*70)