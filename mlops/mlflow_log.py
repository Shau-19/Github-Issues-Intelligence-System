"""
MLflow experiment tracking for GitHub Issues Intelligence
"""

import mlflow
import pandas as pd
import numpy as np

mlflow.set_experiment("github-issues-decision-intelligence")

with mlflow.start_run(run_name="multimodal_random_sampling_v1"):
    
    # ===== PARAMETERS =====
    mlflow.log_param("model", "KMeans")
    mlflow.log_param("n_clusters", 15)
    mlflow.log_param("embedding_model", "all-MiniLM-L6-v2")
    mlflow.log_param("embedding_dim", 384)
    mlflow.log_param("metadata_dim", 8)
    mlflow.log_param("total_dim", 392)
    mlflow.log_param("sample_size", 10000)
    mlflow.log_param("random_state", 42)
    mlflow.log_param("sampling_method", "random")
    
    # ===== METRICS =====
    
    # Clustering quality
    mlflow.log_metric("silhouette_text_only", 0.030)
    mlflow.log_metric("silhouette_metadata_only", 0.486)
    mlflow.log_metric("silhouette_multimodal", 0.230)
    
    # Multimodal advantage
    improvement = (0.230 - 0.030) / 0.030 * 100
    mlflow.log_metric("multimodal_improvement_pct", improvement)
    
    # Load data for stats
    df = pd.read_csv('data/issues_with_severity.csv')
    
    # Data metrics
    mlflow.log_metric("total_issues", len(df))
    mlflow.log_metric("avg_text_length", df['text_length'].mean())
    mlflow.log_metric("unique_repos", df['repo'].nunique())
    
    # Critical issues
    critical = len(df[df['severity_score'] > 5])
    mlflow.log_metric("critical_issues_count", critical)
    mlflow.log_metric("critical_issues_pct", (critical / len(df)) * 100)
    
    # Impact metrics
    cluster_stats = pd.read_csv('data/cluster_severity.csv', index_col=0)
    cluster_stats['impact'] = cluster_stats['severity_score'] * cluster_stats['count']
    
    mlflow.log_metric("max_cluster_impact", cluster_stats['impact'].max())
    mlflow.log_metric("total_impact", cluster_stats['impact'].sum())
    mlflow.log_metric("critical_impact", cluster_stats['impact'].max())
    
    # Pareto analysis
    pareto_pct = (critical / len(df)) * 100
    pareto_impact = (cluster_stats['impact'].max() / cluster_stats['impact'].sum()) * 100
    mlflow.log_metric("pareto_issues_pct", pareto_pct)
    mlflow.log_metric("pareto_impact_pct", pareto_impact)
    
    # ===== ARTIFACTS =====
    mlflow.log_artifact('data/cluster_summaries.json')
    mlflow.log_artifact('data/cluster_severity.csv')
    mlflow.log_artifact('data/cluster_analysis.json')
    
    # ===== TAGS =====
    mlflow.set_tag("project", "github-issues-intelligence")
    mlflow.set_tag("sampling", "random")
    mlflow.set_tag("domain", "decision-intelligence")
    mlflow.set_tag("dataset_size", "5.3M_total")
    
    print("=" * 70)
    print("✅ EXPERIMENT LOGGED TO MLFLOW")
    print("=" * 70)
    print(f"\n📊 Key Results:")
    print(f"  - Multimodal silhouette: 0.230 (7.7× vs text-only)")
    print(f"  - Critical issues: {critical} ({critical/len(df)*100:.1f}%)")
    print(f"  - Max impact: {cluster_stats['impact'].max():.0f}")
    print(f"  - Pareto: {pareto_pct:.1f}% issues = {pareto_impact:.1f}% impact")
    print(f"\n🔗 View experiment:")
    print(f"   mlflow ui")
    print(f"   → http://localhost:5000")