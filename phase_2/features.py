'''import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import re

print("🔧 MULTIMODAL FEATURE ENGINEERING\n")

# Load augmented data
df = pd.read_csv('data/cleaned_issues_with_features.csv')
embeddings = np.load('data/embeddings.npy')

print(f"✅ Loaded {len(df)} issues")
print(f"✅ Loaded embeddings: {embeddings.shape}")

# ===== EXTRACT MULTIMODAL FEATURES =====

print("\n📊 Extracting multimodal features...")

# 1. Binary features (0/1)
df['has_image'] = df['has_image'].astype(int)
df['has_error'] = df['has_error_trace'].astype(int)
df['has_question'] = df['has_question'].astype(int)

# 2. Numeric features
df['url_count'] = df['url_count'].fillna(0).astype(int)
df['text_length'] = df['text_length'].fillna(0).astype(int)
df['word_count'] = df['word_count'].fillna(0).astype(int)

# 3. Categorical → Numeric (already done)
# keyword_severity: 0-13 range
# user_weight: 1, 2, 3

# 4. NEW: Issue complexity score
def complexity_score(row):
    """Estimate issue complexity from multiple signals"""
    score = 0
    score += row['has_error'] * 2      # Errors = more complex
    score += row['has_image'] * 1      # Screenshots = visual issue
    score += row['url_count'] * 0.5    # External links = context needed
    score += min(row['keyword_severity'], 5) * 0.5  # Severity words
    score += 1 if row['word_count'] > 100 else 0    # Long description
    return score

df['complexity_score'] = df.apply(complexity_score, axis=1)

# ===== CREATE FEATURE MATRIX =====

print("\n🔢 Building feature matrix...")

# Select features for multimodal clustering
metadata_features = df[[
    'has_image',           # Binary: has screenshot
    'has_error',           # Binary: contains error trace
    'has_question',        # Binary: is a question
    'url_count',           # Numeric: number of URLs
    'text_length',         # Numeric: length of text
    'keyword_severity',    # Numeric: severity keyword count
    'user_weight',         # Numeric: 1, 2, or 3
    'complexity_score'     # Numeric: derived complexity
]].values

print(f"✅ Metadata features: {metadata_features.shape}")

# Normalize metadata (important!)
scaler = StandardScaler()
metadata_scaled = scaler.fit_transform(metadata_features)

print("\n📊 Feature statistics (after scaling):")
print(f"  - Mean: {metadata_scaled.mean(axis=0)}")
print(f"  - Std:  {metadata_scaled.std(axis=0)}")

# ===== CREATE MULTIMODAL EMBEDDINGS =====

print("\n🎯 Creating multimodal embeddings...")

# Strategy: Concatenate text embeddings + scaled metadata
multimodal_embeddings = np.hstack([
    embeddings,           # 384 dimensions (text semantics)
    metadata_scaled       # 8 dimensions (structured features)
])

print(f"✅ Multimodal embeddings: {multimodal_embeddings.shape}")
print(f"   - Text component: 384D")
print(f"   - Metadata component: 8D")
print(f"   - Total: {multimodal_embeddings.shape[1]}D")

# ===== SAVE EVERYTHING =====

print("\n💾 Saving features...")

# Save metadata features
np.save('data/metadata_features.npy', metadata_scaled)

# Save multimodal embeddings
np.save('data/multimodal_embeddings.npy', multimodal_embeddings)

# Save text-only embeddings separately (for comparison)
np.save('data/text_embeddings.npy', embeddings)

# Save feature names for interpretation
feature_names = [
    'has_image', 'has_error', 'has_question', 'url_count',
    'text_length', 'keyword_severity', 'user_weight', 'complexity_score'
]

import json
with open('data/feature_names.json', 'w') as f:
    json.dump(feature_names, f)

print("✅ Saved:")
print("  - data/metadata_features.npy")
print("  - data/multimodal_embeddings.npy")
print("  - data/text_embeddings.npy")
print("  - data/feature_names.json")

# ===== SHOW SAMPLE =====

print("\n📋 Sample feature vectors:")
print("\nIssue 1 (text-only embedding, first 5 dims):")
print(embeddings[0][:5])

print("\nIssue 1 (metadata features, scaled):")
print(metadata_scaled[0])

print("\nIssue 1 (multimodal, first 10 dims):")
print(multimodal_embeddings[0][:10])

# ===== FEATURE IMPORTANCE PREVIEW =====

print("\n📊 Feature distribution:")
for i, name in enumerate(feature_names):
    orig_values = metadata_features[:, i]
    print(f"\n  {name}:")
    print(f"    Range: [{orig_values.min():.1f}, {orig_values.max():.1f}]")
    print(f"    Mean: {orig_values.mean():.2f}")
    print(f"    Non-zero: {(orig_values > 0).sum()} ({(orig_values > 0).sum()/len(orig_values)*100:.1f}%)")

print("\n" + "="*70)
print("✅ MULTIMODAL FEATURES READY FOR CLUSTERING")
print("="*70)'''

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import json

print("🔧 MULTIMODAL FEATURE ENGINEERING\n")

# Load data
df = pd.read_csv('data/cleaned_issues_with_features.csv')
embeddings = np.load('data/embeddings.npy')

print(f"✅ Loaded {len(df)} issues, embeddings: {embeddings.shape}")

# ===== CREATE MISSING FEATURES =====

# Ensure binary features exist
if 'has_image' not in df.columns:
    df['has_image'] = df['issue_text'].str.contains(r'!\[.*?\]\(.*?\)', na=False).astype(int)

if 'has_error_trace' not in df.columns:
    df['has_error_trace'] = df['issue_text'].str.contains(r'error:|exception|traceback', case=False, na=False).astype(int)

if 'has_question' not in df.columns:
    df['has_question'] = df['issue_text'].str.contains(r'\?', na=False).astype(int)

if 'url_count' not in df.columns:
    df['url_count'] = df['issue_text'].str.count(r'https?://')

if 'text_length' not in df.columns:
    df['text_length'] = df['issue_text'].str.len()

# ===== CREATE COMPLEXITY SCORE =====

def calc_complexity(row):
    """Calculate issue complexity from multiple signals"""
    score = 0
    score += row.get('has_error_trace', 0) * 2
    score += row.get('has_image', 0) * 1
    score += min(row.get('url_count', 0), 5) * 0.5
    score += min(row.get('keyword_severity', 0), 5) * 0.5
    score += 1 if row.get('text_length', 0) > 300 else 0
    return score

df['complexity_score'] = df.apply(calc_complexity, axis=1)

# ===== EXTRACT METADATA FEATURES =====

metadata_features = df[[
    'has_image',
    'has_error_trace',
    'has_question',
    'url_count',
    'text_length',
    'keyword_severity',
    'user_weight',
    'complexity_score'
]].values

print(f"✅ Metadata features extracted: {metadata_features.shape}")

# ===== NORMALIZE =====

scaler = StandardScaler()
metadata_scaled = scaler.fit_transform(metadata_features)

# ===== COMBINE =====

multimodal_embeddings = np.hstack([embeddings, metadata_scaled])

print(f"✅ Multimodal: {multimodal_embeddings.shape} (384D text + 8D metadata)")

# ===== SAVE =====

np.save('data/metadata_features.npy', metadata_scaled)
np.save('data/multimodal_embeddings.npy', multimodal_embeddings)
np.save('data/text_embeddings.npy', embeddings)

feature_names = [
    'has_image', 'has_error_trace', 'has_question', 'url_count',
    'text_length', 'keyword_severity', 'user_weight', 'complexity_score'
]

with open('data/feature_names.json', 'w') as f:
    json.dump(feature_names, f)

# Save updated dataframe with complexity score
df.to_csv('data/cleaned_issues_with_features.csv', index=False)

print("\n✅ Saved: multimodal_embeddings.npy, metadata_features.npy, feature_names.json")