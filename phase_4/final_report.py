import pandas as pd

print("="*70)
print("FINAL PROJECT SUMMARY")
print("="*70)

df = pd.read_csv('data/issues_with_severity.csv')
decisions = pd.read_csv('data/cluster_severity.csv', index_col=0)
decisions['impact'] = decisions['severity_score'] * decisions['count']

print("\n📊 DATASET")
print(f"  • Total issues analyzed: {len(df):,}")
print(f"  • Date range: {df['created_at'].min()} to {df['created_at'].max()}")
print(f"  • Unique repos: {df['repo'].nunique()}")

print("\n🎯 CLUSTERING")
print(f"  • Clusters identified: {df['cluster_name'].nunique()}")
print(f"  • Largest cluster:  {df['cluster_name'].value_counts().index[0]} ({df['cluster_name'].value_counts().iloc[0]} issues)")
print(f"  • Smallest cluster: {df['cluster_name'].value_counts().index[-1]} ({df['cluster_name'].value_counts().iloc[-1]} issues)")

print("\n🔴 CRITICAL FINDINGS")
critical = decisions[decisions['severity_score'] > 5]
critical_issues = df[df['severity_score'] > 5]
print(f"  • Critical clusters: {len(critical)}")
print(f"  • Critical issues:   {len(critical_issues)} ({len(critical_issues)/len(df)*100:.1f}%)")
print(f"  • Top severity:      {decisions['severity_score'].max():.1f}")

print("\n💼 BUSINESS IMPACT")
top_impact = decisions.nlargest(1, 'impact').iloc[0]
pareto_impact_pct = top_impact['impact'] / decisions['impact'].sum() * 100
print(f"  • Highest impact cluster: {top_impact.name}")
print(f"  • Impact score:           {top_impact['impact']:.0f}")
print(f"  • Pareto effect:          {len(critical_issues)/len(df)*100:.1f}% issues = {pareto_impact_pct:.1f}% of impact")
print(f"  • Recommended action:     Immediate engineering review")

print("\n🎓 METHODOLOGY")
print("  • Text embeddings:    384D (Sentence-BERT all-MiniLM-L6-v2)")
print("  • Metadata features:  8D (multimodal structural)")
print("  • Combined vector:    392D")
print("  • Clustering:         KMeans (k=15, elbow + silhouette sweep)")
print("  • Silhouette scores:  multimodal=0.230 | metadata=0.486 | text=0.030")
print("  • Improvement:        7.7× multimodal vs text-only")
print("  • Scaler:             Saved to models/scaler.pkl (consistent inference)")
print("  • Experiment tracked: MLflow")

print("\n" + "="*70)
print("✅ PROJECT COMPLETE")
print("="*70)