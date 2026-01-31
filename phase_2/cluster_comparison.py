'''import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score

print("🎯 MULTIMODAL CLUSTERING COMPARISON (FIXED)\n")

# ===== LOAD DATA =====
df = pd.read_csv('data/cleaned_issues_with_features.csv')

# Load all 3 feature sets
text_embeddings = np.load('data/text_embeddings.npy')
metadata_features = np.load('data/metadata_features.npy')
multimodal_embeddings = np.load('data/multimodal_embeddings.npy')

print(f"✅ Loaded {len(df)} issues")

# ===== CLUSTER WITH k=15 =====
CLUSTER_COUNT = 15

print(f"\n🔄 Clustering all methods with k={CLUSTER_COUNT}...")

# Text-only
km_text = KMeans(n_clusters=CLUSTER_COUNT, random_state=42, n_init=10)
df['cluster_text'] = km_text.fit_predict(text_embeddings)

# Metadata-only
km_meta = KMeans(n_clusters=CLUSTER_COUNT, random_state=42, n_init=10)
df['cluster_metadata'] = km_meta.fit_predict(metadata_features)

# Multimodal
km_multi = KMeans(n_clusters=CLUSTER_COUNT, random_state=42, n_init=10)
df['cluster_multimodal'] = km_multi.fit_predict(multimodal_embeddings)

print("✅ Clustering complete")

# ===== EVALUATE CLUSTERING QUALITY =====
print("\n📊 CLUSTERING QUALITY COMPARISON")
print("="*70)

metrics = {
    'Text-only': {
        'Silhouette': silhouette_score(text_embeddings, df['cluster_text']),
        'Calinski-Harabasz': calinski_harabasz_score(text_embeddings, df['cluster_text']),
    },
    'Metadata-only': {
        'Silhouette': silhouette_score(metadata_features, df['cluster_metadata']),
        'Calinski-Harabasz': calinski_harabasz_score(metadata_features, df['cluster_metadata']),
    },
    'Multimodal': {
        'Silhouette': silhouette_score(multimodal_embeddings, df['cluster_multimodal']),
        'Calinski-Harabasz': calinski_harabasz_score(multimodal_embeddings, df['cluster_multimodal']),
    }
}

for method, scores in metrics.items():
    print(f"\n{method}:")
    for metric, value in scores.items():
        print(f"  {metric}: {value:.3f}")

# ===== SAVE RESULTS =====
df.to_csv('data/clustered_issues.csv', index=False)

import pickle
with open('data/kmeans_multimodal.pkl', 'wb') as f:
    pickle.dump(km_multi, f)

print("\n✅ Saved: data/clustered_issues.csv")

# ===== CLUSTER PROFILES =====
print("\n\n📊 MULTIMODAL CLUSTER PROFILES (Top 5 Clusters)")
print("="*70)

import json
with open('data/feature_names.json', 'r') as f:
    feature_names = json.load(f)

for cluster_id in range(5):
    cluster_mask = df['cluster_multimodal'] == cluster_id
    cluster_df = df[cluster_mask]
    
    print(f"\n🔷 Cluster {cluster_id} ({len(cluster_df)} issues, {len(cluster_df)/len(df)*100:.1f}%)")
    
    # Get cluster center from metadata space
    cluster_center_idx = km_multi.labels_ == cluster_id
    cluster_metadata = metadata_features[cluster_center_idx]
    
    if len(cluster_metadata) > 0:
        avg_features = cluster_metadata.mean(axis=0)
        
        # Show top 3 distinctive features
        feature_values = list(zip(feature_names, avg_features))
        feature_values_sorted = sorted(feature_values, key=lambda x: abs(x[1]), reverse=True)
        
        print("  Key characteristics:")
        for fname, fval in feature_values_sorted[:3]:
            direction = "High" if fval > 0.5 else "Low" if fval < -0.5 else "Medium"
            print(f"    • {fname}: {direction} ({fval:.2f})")
        
        # Show sample titles
        print("  Sample issues:")
        for title in cluster_df['issue_title'].head(3):
            print(f"    - {title[:60]}...")

# ===== CLUSTER OVERLAP ANALYSIS =====
print("\n\n📊 METHOD AGREEMENT ANALYSIS")
print("="*70)

# Text vs Multimodal
text_multi_agree = (df['cluster_text'] == df['cluster_multimodal']).sum()
print(f"\n✅ Text vs. Multimodal agreement: {text_multi_agree}/{len(df)} ({text_multi_agree/len(df)*100:.1f}%)")

# Metadata vs Multimodal
meta_multi_agree = (df['cluster_metadata'] == df['cluster_multimodal']).sum()
print(f"✅ Metadata vs. Multimodal agreement: {meta_multi_agree}/{len(df)} ({meta_multi_agree/len(df)*100:.1f}%)")

# Issues where all 3 methods agree
all_agree = ((df['cluster_text'] == df['cluster_multimodal']) & 
             (df['cluster_metadata'] == df['cluster_multimodal'])).sum()
print(f"✅ All 3 methods agree: {all_agree}/{len(df)} ({all_agree/len(df)*100:.1f}%)")

# Interesting disagreements
disagreements = df[df['cluster_text'] != df['cluster_multimodal']]
print(f"\n🔍 Disagreements: {len(disagreements)} issues ({len(disagreements)/len(df)*100:.1f}%)")

if len(disagreements) > 0:
    print("\n  Sample disagreements (multimodal found different patterns):")
    for i, row in disagreements.head(3).iterrows():
        print(f"\n    Issue: {row['issue_title'][:50]}...")
        print(f"      Text → Cluster {row['cluster_text']}")
        print(f"      Multimodal → Cluster {row['cluster_multimodal']}")
        
        # Show why they differ
        if 'complexity_score' in row.index:
            print(f"      Complexity: {row['complexity_score']:.1f}, Text length: {row['text_length']}")

print("\n" + "="*70)
print("✅ MULTIMODAL CLUSTERING ANALYSIS COMPLETE")
print("="*70)'''


import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pickle

print("🎯 MULTIMODAL CLUSTERING\n")

# Load
df = pd.read_csv('data/cleaned_issues_with_features.csv')
text_emb = np.load('data/text_embeddings.npy')
meta_feat = np.load('data/metadata_features.npy')
multi_emb = np.load('data/multimodal_embeddings.npy')

print(f"✅ Loaded {len(df)} issues")

# Cluster (k=15)
CLUSTERS = 15

km_text = KMeans(n_clusters=CLUSTERS, random_state=42, n_init=10)
km_meta = KMeans(n_clusters=CLUSTERS, random_state=42, n_init=10)
km_multi = KMeans(n_clusters=CLUSTERS, random_state=42, n_init=10)

df['cluster_text'] = km_text.fit_predict(text_emb)
df['cluster_metadata'] = km_meta.fit_predict(meta_feat)
df['cluster_multimodal'] = km_multi.fit_predict(multi_emb)

# Metrics
sil_text = silhouette_score(text_emb, df['cluster_text'])
sil_meta = silhouette_score(meta_feat, df['cluster_metadata'])
sil_multi = silhouette_score(multi_emb, df['cluster_multimodal'])

print(f"\n📊 Silhouette Scores:")
print(f"  Text-only: {sil_text:.3f}")
print(f"  Metadata-only: {sil_meta:.3f}")
print(f"  Multimodal: {sil_multi:.3f}")

# Save
df.to_csv('data/clustered_issues.csv', index=False)
with open('models/kmeans_multimodal.pkl', 'wb') as f:
    pickle.dump(km_multi, f)

print(f"\n✅ Saved: clustered_issues.csv, kmeans_multimodal.pkl")