'''import pandas as pd
import numpy as np
from collections import Counter
import json

print("🤖 LLM-POWERED CLUSTER NAMING\n")

# Load clustered data
df = pd.read_csv('data/clustered_issues.csv')

print(f"✅ Loaded {len(df)} clustered issues")
print(f"📋 Available columns: {df.columns.tolist()}\n")

# ===== HELPER: Safe column access =====
def safe_mean(df, col_name, default=0):
    """Safely get mean of a column, return default if missing"""
    if col_name in df.columns:
        return df[col_name].mean()
    return default

def safe_has(df, col_name):
    """Check if column exists and return it, else create dummy"""
    if col_name in df.columns:
        return df[col_name]
    return pd.Series([0] * len(df))

# ===== RE-EXTRACT FEATURES FROM TEXT (if missing) =====
if 'complexity_score' not in df.columns:
    print("⚠️ Some features missing, re-extracting from text...")
    
    # Re-extract basic features
    df['has_question'] = df['issue_text'].str.contains(r'\?', na=False).astype(int)
    df['url_count'] = df['issue_text'].str.count(r'https?://')
    df['text_length'] = df['issue_text'].str.len()
    
    # Re-calculate keyword severity
    SEVERE_KEYWORDS = [
        'crash', 'error', 'exception', 'fatal', 'failed', 
        'broken', 'not working', 'timeout', 'panic'
    ]
    df['keyword_severity'] = df['issue_text'].apply(
        lambda x: sum(1 for kw in SEVERE_KEYWORDS if kw in str(x).lower())
    )
    
    # Re-calculate complexity
    def calc_complexity(row):
        score = 0
        score += row.get('keyword_severity', 0) * 0.5
        score += min(row.get('url_count', 0), 5) * 0.5
        score += 1 if row.get('text_length', 0) > 300 else 0
        return score
    
    df['complexity_score'] = df.apply(calc_complexity, axis=1)
    
    print("✅ Features re-extracted")

# ===== ANALYZE EACH CLUSTER =====

cluster_analysis = {}

for cluster_id in range(15):
    cluster_mask = df['cluster_multimodal'] == cluster_id
    cluster_df = df[cluster_mask]
    
    print(f"\n{'='*70}")
    print(f"🔷 CLUSTER {cluster_id} ({len(cluster_df)} issues, {len(cluster_df)/len(df)*100:.1f}%)")
    print(f"{'='*70}")
    
    # ===== SAFE FEATURE EXTRACTION =====
    
    # Sample titles
    sample_titles = cluster_df['issue_title'].head(10).tolist()
    
    # Aggregate features (safely)
    feature_summary = {
        'has_question': safe_mean(cluster_df, 'has_question'),
        'avg_url_count': safe_mean(cluster_df, 'url_count'),
        'avg_text_length': safe_mean(cluster_df, 'text_length'),
        'avg_complexity': safe_mean(cluster_df, 'complexity_score'),
        'avg_severity': safe_mean(cluster_df, 'keyword_severity'),
    }
    
    # Optional features
    if 'has_image' in cluster_df.columns:
        feature_summary['has_image'] = cluster_df['has_image'].mean()
    
    if 'has_error_trace' in cluster_df.columns:
        feature_summary['has_error_trace'] = cluster_df['has_error_trace'].mean()
    
    # Top repos
    if 'repo' in cluster_df.columns:
        top_repos = cluster_df['repo'].value_counts().head(3).to_dict()
    else:
        top_repos = {}
    
    # Tier distribution
    if 'repo_tier' in cluster_df.columns:
        tier_dist = cluster_df['repo_tier'].value_counts().to_dict()
    else:
        tier_dist = {}
    
    # ===== DISPLAY ANALYSIS =====
    
    print("\n📊 Cluster Characteristics:")
    print(f"  • Has questions: {feature_summary['has_question']*100:.1f}%")
    print(f"  • Avg URLs: {feature_summary['avg_url_count']:.1f}")
    print(f"  • Avg text length: {feature_summary['avg_text_length']:.0f} chars")
    print(f"  • Avg complexity: {feature_summary['avg_complexity']:.2f}")
    print(f"  • Avg severity: {feature_summary['avg_severity']:.2f}")
    
    if 'has_error_trace' in feature_summary:
        print(f"  • Has error traces: {feature_summary['has_error_trace']*100:.1f}%")
    if 'has_image' in feature_summary:
        print(f"  • Has images: {feature_summary['has_image']*100:.1f}%")
    
    if top_repos:
        print("\n🏢 Top Repos:")
        for repo, count in list(top_repos.items())[:3]:
            print(f"  • {repo}: {count} issues")
    
    if tier_dist:
        print("\n🏷️ Tier Distribution:")
        for tier, count in tier_dist.items():
            print(f"  • {tier}: {count} ({count/len(cluster_df)*100:.1f}%)")
    
    # ===== RULE-BASED NAMING =====
    
    def generate_cluster_name(features, titles):
        """Generate cluster name based on characteristics"""
        
        # High error rate → Error/Bug cluster
        if features.get('has_error_trace', 0) > 0.5:
            return "Critical Errors & Crashes"
        
        # High question rate → Help/Support cluster
        if features['has_question'] > 0.6:
            return "User Questions & Help Requests"
        
        # High complexity + long text → Technical Deep-Dive
        if features['avg_complexity'] > 2.0 and features['avg_text_length'] > 400:
            return "Complex Technical Issues"
        
        # High URL count → Reference-heavy
        if features['avg_url_count'] > 3.0:
            return "Cross-Reference & Dependencies"
        
        # High image rate → UI issues
        if features.get('has_image', 0) > 0.15:
            return "UI/Visual Issues"
        
        # Short text + low complexity → Simple reports
        if features['avg_text_length'] < 150 and features['avg_complexity'] < 1.0:
            return "Simple Bug Reports"
        
        # Long text + low questions → Detailed descriptions
        if features['avg_text_length'] > 400 and features['has_question'] < 0.3:
            return "Detailed Technical Reports"
        
        # High severity keywords
        if features['avg_severity'] > 1.5:
            return "High-Severity Issues"
        
        # Medium text, medium complexity
        if 200 < features['avg_text_length'] < 400:
            return "Standard Issue Reports"
        
        # Default
        return "General Issues"
    
    cluster_name = generate_cluster_name(feature_summary, sample_titles)
    
    print(f"\n🏷️ GENERATED NAME: {cluster_name}")
    
    # ===== SAMPLE ISSUES =====
    
    print("\n📝 Sample Issues:")
    for i, title in enumerate(sample_titles[:5], 1):
        print(f"  {i}. {title[:70]}...")
    
    # Store analysis
    cluster_analysis[cluster_id] = {
        'name': cluster_name,
        'size': len(cluster_df),
        'percentage': len(cluster_df)/len(df)*100,
        'features': feature_summary,
        'top_repos': top_repos,
        'tier_distribution': tier_dist,
        'sample_titles': sample_titles[:5]
    }

# ===== SAVE CLUSTER NAMES =====

print("\n\n" + "="*70)
print("💾 SAVING CLUSTER ANALYSIS")
print("="*70)

# Add cluster names to dataframe
df['cluster_name'] = df['cluster_multimodal'].map(
    lambda x: cluster_analysis[x]['name']
)

df.to_csv('data/clustered_issues_named.csv', index=False)

# Save cluster analysis JSON
with open('data/cluster_analysis.json', 'w') as f:
    json.dump(cluster_analysis, f, indent=2, default=str)

print("\n✅ Saved:")
print("  - data/clustered_issues_named.csv")
print("  - data/cluster_analysis.json")

# ===== SUMMARY TABLE =====

print("\n\n📊 CLUSTER SUMMARY TABLE")
print("="*70)
print(f"{'ID':<4} {'Name':<45} {'Size':<8} {'%':<6}")
print("-"*70)

for cid in range(15):
    info = cluster_analysis[cid]
    print(f"{cid:<4} {info['name']:<45} {info['size']:<8} {info['percentage']:>5.1f}%")

print("="*70)
print(f"{'TOTAL':<4} {'':<45} {len(df):<8} {'100.0%':>6}")
print("="*70)

# ===== BUSINESS IMPACT PREVIEW =====

print("\n\n💼 BUSINESS IMPACT ANALYSIS")
print("="*70)

# Identify high-priority clusters
high_priority = []
for cid, info in cluster_analysis.items():
    features = info['features']
    if any([
        features.get('has_error_trace', 0) > 0.3,
        features['avg_severity'] > 1.5,
        'Critical' in info['name'] or 'High-Severity' in info['name']
    ]):
        high_priority.append((cid, info))

if high_priority:
    print(f"\n⚠️ HIGH-PRIORITY CLUSTERS ({len(high_priority)} clusters, {sum(info['size'] for _, info in high_priority)} issues):")
    for cid, info in high_priority:
        print(f"\n  📍 Cluster {cid}: {info['name']}")
        print(f"     Size: {info['size']} issues ({info['percentage']:.1f}%)")
        print(f"     Avg severity: {info['features']['avg_severity']:.2f}")
        print(f"     Avg complexity: {info['features']['avg_complexity']:.2f}")
else:
    print("\n✅ No critical high-priority clusters detected")

# Medium priority
medium_priority = []
for cid, info in cluster_analysis.items():
    if cid not in [c for c, _ in high_priority]:
        features = info['features']
        if features['avg_complexity'] > 1.5 or features['avg_text_length'] > 300:
            medium_priority.append((cid, info))

if medium_priority:
    print(f"\n⚙️ MEDIUM-PRIORITY CLUSTERS ({len(medium_priority)} clusters, {sum(info['size'] for _, info in medium_priority)} issues):")
    for cid, info in medium_priority[:3]:  # Show top 3
        print(f"  • Cluster {cid}: {info['name']} ({info['size']} issues)")

print("\n" + "="*70)
print("✅ WEEK 2 COMPLETE: MULTIMODAL CLUSTERING & NAMING")
print("="*70)
print("\n🎯 Next Steps:")
print("  1. Review cluster_analysis.json for detailed profiles")
print("  2. Proceed to Week 3: Severity Scoring & Decision Engine")'''


import pandas as pd
import json

print("🤖 CLUSTER NAMING\n")

df = pd.read_csv('data/clustered_issues.csv')

print(f"✅ Loaded {len(df)} issues")

# Re-extract features if missing
if 'complexity_score' not in df.columns:
    df['has_question'] = df['issue_text'].str.contains(r'\?', na=False).astype(int)
    df['url_count'] = df['issue_text'].str.count(r'https?://')
    df['text_length'] = df['issue_text'].str.len()
    
    SEVERE_KW = ['crash', 'error', 'exception', 'fatal', 'broken']
    df['keyword_severity'] = df['issue_text'].apply(
        lambda x: sum(1 for kw in SEVERE_KW if kw in str(x).lower())
    )
    
    df['complexity_score'] = (
        df.get('keyword_severity', 0) * 0.5 + 
        df.get('url_count', 0).clip(0, 5) * 0.5
    )

cluster_analysis = {}

for cid in range(15):
    cluster_df = df[df['cluster_multimodal'] == cid]
    
    features = {
        'has_error': cluster_df.get('has_error_trace', pd.Series([0])).mean(),
        'has_question': cluster_df['has_question'].mean(),
        'avg_complexity': cluster_df['complexity_score'].mean(),
        'avg_text_length': cluster_df['text_length'].mean(),
        'avg_severity': cluster_df['keyword_severity'].mean(),
        'has_image': cluster_df.get('has_image', pd.Series([0])).mean(),
    }
    
    # Rule-based naming
    if features['has_error'] > 0.5:
        name = "Critical Errors & Crashes"
    elif features['has_question'] > 0.6:
        name = "User Questions & Help Requests"
    elif features['avg_complexity'] > 2.0:
        name = "Complex Technical Issues"
    elif features.get('has_image', 0) > 0.15:
        name = "UI/Visual Issues"
    elif features['avg_text_length'] < 150:
        name = "Simple Bug Reports"
    elif features['avg_text_length'] > 400:
        name = "Detailed Technical Reports"
    elif features['avg_severity'] > 1.5:
        name = "High-Severity Issues"
    else:
        name = "General Issues"
    
    cluster_analysis[cid] = {
        'name': name,
        'size': len(cluster_df),
        'features': features,
        'sample_titles': cluster_df['issue_title'].head(5).tolist()
    }
    
    print(f"Cluster {cid}: {name} ({len(cluster_df)} issues)")

# Save
df['cluster_name'] = df['cluster_multimodal'].map(lambda x: cluster_analysis[x]['name'])
df.to_csv('data/clustered_issues_named.csv', index=False)

with open('data/cluster_analysis.json', 'w') as f:
    json.dump(cluster_analysis, f, indent=2, default=str)

print(f"\n✅ Saved: clustered_issues_named.csv, cluster_analysis.json")