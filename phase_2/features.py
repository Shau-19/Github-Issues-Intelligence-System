"""
features.py — Multimodal Feature Engineering
Extracts 8D metadata features, scales them, concatenates with 384D text
embeddings to produce a 392D multimodal vector for clustering.

FIX: StandardScaler is now fitted once and saved to models/scaler.pkl
     so that inference (app.py live tab) loads the SAME scaler used here.
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from sklearn.preprocessing import StandardScaler

print("🔧 MULTIMODAL FEATURE ENGINEERING\n")

# ── Load ─────────────────────────────────────────────────────────────────────
df = pd.read_csv('data/cleaned_issues_with_features.csv')
embeddings = np.load('data/embeddings.npy')

print(f"✅ Loaded {len(df)} issues, embeddings: {embeddings.shape}")

# ── Ensure all features exist ─────────────────────────────────────────────────
if 'has_image' not in df.columns:
    df['has_image'] = df['issue_text'].str.contains(
        r'!\[.*?\]\(.*?\)', na=False).astype(int)

if 'has_error_trace' not in df.columns:
    df['has_error_trace'] = df['issue_text'].str.contains(
        r'error:|exception|traceback', case=False, na=False).astype(int)

if 'has_question' not in df.columns:
    df['has_question'] = df['issue_text'].str.contains(
        r'\?', na=False).astype(int)

if 'url_count' not in df.columns:
    df['url_count'] = df['issue_text'].str.count(r'https?://')

if 'text_length' not in df.columns:
    df['text_length'] = df['issue_text'].str.len()

# ── Complexity score ──────────────────────────────────────────────────────────
def calc_complexity(row):
    score  = row.get('has_error_trace', 0) * 2
    score += row.get('has_image', 0) * 1
    score += min(row.get('url_count', 0), 5) * 0.5
    score += min(row.get('keyword_severity', 0), 5) * 0.5
    score += 1 if row.get('text_length', 0) > 300 else 0
    return score

df['complexity_score'] = df.apply(calc_complexity, axis=1)

# ── Build raw metadata matrix ─────────────────────────────────────────────────
FEATURE_COLS = [
    'has_image',
    'has_error_trace',
    'has_question',
    'url_count',
    'text_length',
    'keyword_severity',
    'user_weight',
    'complexity_score',
]

metadata_features = df[FEATURE_COLS].fillna(0).values
print(f"✅ Metadata matrix: {metadata_features.shape}")

# ── Fit and SAVE scaler ───────────────────────────────────────────────────────
# IMPORTANT: save the fitted scaler so inference uses identical scaling
scaler = StandardScaler()
metadata_scaled = scaler.fit_transform(metadata_features)

os.makedirs('models', exist_ok=True)
with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("✅ Saved models/scaler.pkl  (use this at inference time)")

# ── Multimodal concatenation ──────────────────────────────────────────────────
multimodal_embeddings = np.hstack([embeddings, metadata_scaled])
print(f"✅ Multimodal: {multimodal_embeddings.shape}  (384D text + 8D metadata)")

# ── Save arrays ──────────────────────────────────────────────────────────────
np.save('data/metadata_features.npy',    metadata_scaled)
np.save('data/multimodal_embeddings.npy', multimodal_embeddings)
np.save('data/text_embeddings.npy',      embeddings)

with open('data/feature_names.json', 'w') as f:
    json.dump(FEATURE_COLS, f)

df.to_csv('data/cleaned_issues_with_features.csv', index=False)

print("\n✅ Saved:")
print("  - data/metadata_features.npy")
print("  - data/multimodal_embeddings.npy")
print("  - data/text_embeddings.npy")
print("  - data/feature_names.json")
print("  - models/scaler.pkl          ← critical for consistent inference")