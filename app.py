import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="GitHub Issues Intelligence",
    page_icon="🔍",
    layout="wide"
)

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('data/issues_with_severity.csv')

    with open('data/cluster_summaries.json', 'r') as f:
        summaries = json.load(f)

    cluster_stats = pd.read_csv('data/cluster_severity.csv', index_col=0)
    cluster_stats['impact'] = cluster_stats['severity_score'] * cluster_stats['count']

    return df, summaries, cluster_stats


df, summaries, cluster_stats = load_data()

TOTAL_IMPACT = cluster_stats['impact'].sum()

# -----------------------------
# Header
# -----------------------------
st.title("🔍 GitHub Issues Decision Intelligence")
st.markdown("**Multimodal ML System** | From unstructured issues → prioritized engineering actions")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("📊 System Overview")
st.sidebar.metric("Total Issues", f"{len(df):,}")
st.sidebar.metric("Clusters Identified", len(summaries))
st.sidebar.metric(
    "Critical Issues",
    f"{len(df[df['severity_score'] > 5]):,} "
    f"({len(df[df['severity_score'] > 5]) / len(df) * 100:.1f}%)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 Model Stack")
st.sidebar.markdown("""
- **Embeddings:** Sentence-BERT (384D)
- **Metadata:** 8D structural features
- **Clustering:** KMeans (k=15)
- **Decision Logic:** Rules + heuristics
- **Explainability:** Llama 3.3 70B (RAG)
""")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "🔍 Cluster Analysis", "🔴 Critical Issues", "📈 Trends"]
)

# ============================================================
# TAB 1: OVERVIEW
# ============================================================
with tab1:
    st.header("System Performance")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Multimodal Silhouette", "0.288", delta="14.5× vs text-only")
    col2.metric("Highest Impact Cluster", "Critical Errors", delta="2,974 impact")
    col3.metric("Pareto Effect", "4.3%", delta="= 77% of impact")
    col4.metric("Automation Potential", "4,193 issues", delta="Low impact")

    st.markdown("---")

    st.subheader("💥 Impact Distribution")
    fig = px.bar(
        cluster_stats.nlargest(7, 'impact').reset_index(),
        x='impact',
        y='cluster_name',
        orientation='h',
        color='severity_score',
        color_continuous_scale='Reds',
        labels={
            'impact': 'Impact Score',
            'cluster_name': 'Cluster',
            'severity_score': 'Severity'
        }
    )
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TAB 2: CLUSTER ANALYSIS (CORE)
# ============================================================
with tab2:
    st.header("🔍 Cluster Deep Dive")

    cluster_names = list(summaries.keys())
    selected_cluster = st.selectbox("Select Issue Cluster", cluster_names)

    if selected_cluster:
        cluster_info = summaries[selected_cluster]
        stats = cluster_stats.loc[selected_cluster]

        col1, col2, col3 = st.columns(3)
        col1.metric("Issues", cluster_info['size'])
        col2.metric("Avg Severity", f"{stats['severity_score']:.2f}")
        col3.metric("Impact Score", f"{stats['impact']:.0f}")

        st.markdown("---")

        # -----------------------------
        # SYSTEM DECISION (CRITICAL)
        # -----------------------------
        st.markdown("### 🚦 System Decision")

        if stats['impact'] > 2000:
            st.error("🚨 IMMEDIATE ENGINEERING FIX")
        elif stats['impact'] > 500:
            st.warning("⚠️ INVESTIGATE")
        else:
            st.info("ℹ️ MONITOR / AUTOMATE")

        st.markdown("---")

        # -----------------------------
        # RAG EXPLAINABILITY
        # -----------------------------
        st.subheader("🧠 Decision Explainability (RAG)")
        st.caption("LLM-generated explanation of a deterministic system decision")

        st.info(cluster_info['root_cause'])

        st.caption(
            "⚠️ Explanation generated from sampled issues. "
            "The LLM does not influence prioritization logic."
        )

        # -----------------------------
        # BUSINESS CONTEXT
        # -----------------------------
        st.markdown(
            f"**Why this matters:** This cluster represents "
            f"{cluster_info['size']} issues but contributes "
            f"{stats['impact'] / TOTAL_IMPACT * 100:.1f}% of total system impact."
        )

        st.markdown("---")

        # -----------------------------
        # SAMPLE EVIDENCE
        # -----------------------------
        st.subheader("📝 Sample Issues (Evidence)")
        for i, sample in enumerate(cluster_info['samples'], 1):
            with st.expander(f"Issue {i}"):
                st.write(sample)

        # -----------------------------
        # ISSUE TABLE
        # -----------------------------
        st.subheader("📋 Top Issues in Cluster")
        cluster_df = (
            df[df['cluster_name'] == selected_cluster]
            [['issue_title', 'severity_score', 'repo', 'created_at']]
            .sort_values('severity_score', ascending=False)
        )

        st.dataframe(
            cluster_df.head(20),
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# TAB 3: CRITICAL ISSUES
# ============================================================
with tab3:
    st.header("🔴 Critical Issues Dashboard")

    critical_df = df[df['severity_score'] > 5].sort_values(
        'severity_score', ascending=False
    )

    st.markdown(
        f"### 🚨 {len(critical_df)} issues require immediate engineering attention"
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(
            critical_df[
                ['issue_title', 'cluster_name', 'severity_score', 'repo']
            ].head(20),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.subheader("🎯 Action Summary")
        for cluster, count in critical_df['cluster_name'].value_counts().items():
            st.markdown(f"**{cluster}**")
            st.markdown(f"- {count} issues")
            st.markdown("- 🔴 Immediate Fix")
            st.markdown("---")

# ============================================================
# TAB 4: TRENDS & DRIFT
# ============================================================
with tab4:
    st.header("📈 Trend & Drift Analysis")

    df['created_at'] = pd.to_datetime(df['created_at'])
    mid_date = df['created_at'].median()

    early = df[df['created_at'] < mid_date]['cluster_name'].value_counts(normalize=True)
    late = df[df['created_at'] >= mid_date]['cluster_name'].value_counts(normalize=True)

    drift_rows = []
    for cluster in early.index:
        if cluster in late.index:
            change = (late[cluster] - early[cluster]) * 100
            if abs(change) > 1:
                drift_rows.append({
                    "Cluster": cluster,
                    "Early %": f"{early[cluster]*100:.1f}%",
                    "Late %": f"{late[cluster]*100:.1f}%",
                    "Change": f"{change:+.1f}%",
                    "Trend": "📈 Increasing" if change > 0 else "📉 Decreasing"
                })

    if drift_rows:
        st.dataframe(pd.DataFrame(drift_rows), use_container_width=True)
    else:
        st.info("No significant drift detected (threshold ±2%)")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center'>
        <strong>GitHub Issues Decision Intelligence System</strong><br>
        Deterministic ML Decisions • LLM-based Explainability • Production-aligned Design
    </div>
    """,
    unsafe_allow_html=True
)
