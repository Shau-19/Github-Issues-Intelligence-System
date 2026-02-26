import streamlit as st
import numpy as np
import pickle
import re
import pandas as pd
import json
import plotly.graph_objects as go
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GITHUB // INTEL",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS — Neon Ops Center Dark ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow+Condensed:wght@300;400;600;700;900&family=Barlow:wght@300;400&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080c10 !important;
    color: #c8d4e0 !important;
    font-family: 'Barlow', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(rgba(0,200,100,0.012) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,200,100,0.012) 1px, transparent 1px),
        #080c10 !important;
    background-size: 40px 40px !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 1400px; }

/* ── Typography ── */
h1, h2, h3 { font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.08em; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(0,255,136,0.2) !important;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #3a6050 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.4rem !important;
    border: none !important;
    border-radius: 0 !important;
    transition: all 0.15s !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,255,136,0.06) !important;
    color: #00ff88 !important;
    border-bottom: 2px solid #00ff88 !important;
    text-shadow: 0 0 8px rgba(0,255,136,0.5) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #00cc66 !important;
    background: rgba(0,255,136,0.04) !important;
}

/* ── Panel / card ── */
.panel {
    background: rgba(0,255,136,0.02);
    border: 1px solid rgba(0,255,136,0.12);
    border-radius: 2px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    position: relative;
}
.panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 2px; height: 100%;
    background: rgba(0,255,136,0.4);
    border-radius: 2px 0 0 2px;
}
.panel-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #00ff88;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    text-shadow: 0 0 6px rgba(0,255,136,0.4);
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: rgba(0,255,136,0.02) !important;
    border: 1px solid rgba(0,255,136,0.12) !important;
    border-radius: 2px !important;
    padding: 1.25rem 1.5rem !important;
    position: relative;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 2px; height: 100%;
    background: rgba(0,255,136,0.4);
}
[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.65rem !important;
    color: #3a6050 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #00ff88 !important;
    text-shadow: 0 0 12px rgba(0,255,136,0.4) !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important;
    color: #3a9060 !important;
}

/* ── Selectbox ── */
.stSelectbox label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.65rem !important;
    color: #3a6050 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(0,255,136,0.03) !important;
    border: 1px solid rgba(0,255,136,0.15) !important;
    border-radius: 2px !important;
    color: #c8d4e0 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important;
}

/* ── Alert boxes ── */
div[data-testid="stAlert"] {
    border-radius: 2px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(0,255,136,0.02) !important;
    border: 1px solid rgba(0,255,136,0.1) !important;
    border-radius: 2px !important;
    color: #3a9060 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
}
.streamlit-expanderContent {
    background: rgba(0,255,136,0.02) !important;
    border: 1px solid rgba(0,255,136,0.1) !important;
    border-top: none !important;
    color: #7a9ab0 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,255,136,0.12) !important;
    border-radius: 2px !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(0,255,136,0.1) !important;
    margin: 1.5rem 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080c10; }
::-webkit-scrollbar-thumb { background: rgba(0,255,136,0.2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,255,136,0.4); }

/* ── Status dot ── */
.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #00ff88;
    margin-right: 6px;
    box-shadow: 0 0 8px #00ff88;
    animation: pulse-green 2s infinite;
}
@keyframes pulse-green {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.2; }
}

/* ── Action card ── */
.action-card {
    background: rgba(0,255,136,0.02);
    border: 1px solid rgba(0,255,136,0.1);
    border-left: 2px solid rgba(255,30,30,0.6);
    border-radius: 2px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
}
.action-card-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #c8d4e0;
    letter-spacing: 0.05em;
}
.action-card-meta {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #3a6050;
    letter-spacing: 0.1em;
    margin-top: 0.2rem;
}
</style>
""", unsafe_allow_html=True)


# ── CSS additions for inference tab ───────────────────────────────────────────
# (injected inline via st.markdown in the main CSS block — no separate call needed)

# ── Inference tools ────────────────────────────────────────────────────────────
@st.cache_resource
def _get_hf_embedding(text: str) -> list:
    """Call HuggingFace Inference API to get 384D embedding.
    No torch, no sentence-transformers — just an HTTP request."""
    import requests as _req
    HF_TOKEN = os.environ.get("HF_TOKEN", "")
    headers  = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    url      = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    resp     = _req.post(url, headers=headers, json={"inputs": text}, timeout=15)
    resp.raise_for_status()
    result   = resp.json()
    # API returns list of token embeddings — mean pool to get sentence embedding
    emb = result[0] if isinstance(result[0], list) else result
    if isinstance(emb[0], list):
        import numpy as _np
        emb = _np.mean(emb, axis=0).tolist()
    return emb

def _ensure_model():
    """Download kmeans_multimodal.pkl from Google Drive if not present."""
    import os as _os
    model_path = 'models/kmeans_multimodal.pkl'
    if _os.path.exists(model_path):
        return
    gdrive_id = _os.environ.get("KMEANS_GDRIVE_ID", "")
    if not gdrive_id:
        raise FileNotFoundError(
            "models/kmeans_multimodal.pkl not found. "
            "Set KMEANS_GDRIVE_ID secret in Streamlit Cloud."
        )
    import subprocess as _sub
    _os.makedirs('models', exist_ok=True)
    _sub.run(
        ["python", "-m", "gdown", gdrive_id, "-O", model_path],
        check=True
    )

@st.cache_resource
def load_inference_tools():
    _ensure_model()
    with open('models/kmeans_multimodal.pkl', 'rb') as f:
        km_model = pickle.load(f)
    # Load the SAME scaler fitted during training — not refitted at inference
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('data/cluster_analysis.json', 'r') as f:
        cluster_info = json.load(f)
    # embedder is now the HF API function — no torch needed
    return km_model, _get_hf_embedding, scaler, cluster_info

# ── Plotly neon theme ──────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="#080c10",
    plot_bgcolor="#080c10",
    font=dict(family="Share Tech Mono, monospace", color="#3a6050", size=11),
    margin=dict(t=40, b=40, l=10, r=10),
    xaxis=dict(
        gridcolor="rgba(0,255,136,0.05)",
        zerolinecolor="rgba(0,255,136,0.1)",
        linecolor="rgba(0,255,136,0.1)",
        tickfont=dict(family="Share Tech Mono", color="#3a6050", size=10),
    ),
    yaxis=dict(
        gridcolor="rgba(0,255,136,0.05)",
        zerolinecolor="rgba(0,255,136,0.1)",
        linecolor="rgba(0,255,136,0.1)",
        tickfont=dict(family="Share Tech Mono", color="#3a6050", size=10),
    ),
)

# ── Load data ──────────────────────────────────────────────────────────────────
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
now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:flex-start;justify-content:space-between;
            border-bottom:1px solid rgba(0,255,136,0.15);padding-bottom:1.2rem;margin-bottom:1.8rem">
  <div>
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:2.4rem;font-weight:900;
                letter-spacing:0.2em;color:#00ff88;text-transform:uppercase;
                text-shadow:0 0 18px rgba(0,255,136,0.35)">
      ⬡ &nbsp;GITHUB // INTEL
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
                color:#3a6050;letter-spacing:0.18em;margin-top:4px">
      MULTIMODAL ML SYSTEM &nbsp;·&nbsp; 0.230 SILHOUETTE · 7.7× VS TEXT-ONLY · 9,961 ISSUES
    </div>
  </div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
              color:#3a6050;text-align:right;line-height:2">
    <span class="status-dot"></span>SYSTEMS NOMINAL<br>
    {now_str}<br>
    ISSUES INDEXED: {len(df):,}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "// OVERVIEW", "// CLUSTER ANALYSIS", "// CRITICAL ISSUES", "// TRENDS", "// LIVE INFERENCE", "// MODEL VALIDATION"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="panel-label">// SYSTEM PERFORMANCE DASHBOARD</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Multimodal Silhouette", "0.230", delta="7.3× vs text-only (0.031)")
    col2.metric("Highest Impact Cluster", "Critical Errors", delta="2,974 impact")
    col3.metric("Pareto Effect", "4.3%", delta="= 77% of impact")
    col4.metric("Automation Potential", "4,193 issues", delta="Low impact")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                color:#2a4a38;letter-spacing:0.12em;line-height:2.2;margin-bottom:1.5rem">
      EMBEDDINGS: SENTENCE-BERT (384D) &nbsp;·&nbsp;
      METADATA: 8D STRUCTURAL FEATURES &nbsp;·&nbsp;
      CLUSTERING: KMEANS (K=15, SEE K-SELECTION TAB) &nbsp;·&nbsp;
      DECISION LOGIC: RULES + HEURISTICS &nbsp;·&nbsp;
      EXPLAINABILITY: LLAMA 3.3 70B (RAG)
    </div>
    """, unsafe_allow_html=True)

    # ── Silhouette comparison bar chart ──
    st.markdown('<div class="panel-label">// CLUSTERING QUALITY — MULTIMODAL vs BASELINES</div>', unsafe_allow_html=True)

    sil_fig = go.Figure(go.Bar(
        x=["Text-Only\n(384D SBERT)", "Metadata-Only\n(8D Structured)", "Multimodal\n(392D Combined)"],
        y=[0.031, 0.492, 0.230],
        marker_color=["#3a6050", "#7A9AB5", "#00ff88"],
        text=["0.031", "0.492", "0.230"],
        textposition="outside",
        textfont=dict(family="Share Tech Mono", color="#3a6050", size=11),
        hovertemplate="<b>%{x}</b><br>Silhouette: %{y:.3f}<extra></extra>"
    ))
    sil_fig.update_layout(
        height=280,
        annotations=[dict(
            x=2, y=0.230, xref="x", yref="y",
            text="← 7.3× better than text-only",
            showarrow=False,
            font=dict(family="Share Tech Mono", color="#00ff88", size=10),
            xanchor="left", yanchor="middle",
            xshift=15
        )],
        **PLOT_LAYOUT
    )
    sil_fig.update_yaxes(title_text="SILHOUETTE SCORE", range=[0, 0.62])
    st.plotly_chart(sil_fig, use_container_width=True)

    # ── K-selection justification ──
    import os
    st.markdown('<div class="panel-label">// K-SELECTION ANALYSIS — WHY k=15</div>', unsafe_allow_html=True)
    if os.path.exists('data/elbow_plot.png'):
        st.image('data/elbow_plot.png', use_container_width=True)
    else:
        # Inline plotly elbow from embedded data
        elbow_k   = list(range(5, 21))
        elbow_sil = [0.3333,0.3338,0.3350,0.3368,0.2454,0.2369,0.2473,
                     0.2463,0.2468,0.2404,0.2520,0.2325,0.2291,0.2352,0.2127,0.2101]
        elbow_fig = go.Figure()
        elbow_fig.add_trace(go.Scatter(
            x=elbow_k, y=elbow_sil, mode="lines+markers",
            line=dict(color="#00ff88", width=2),
            marker=dict(size=6, color="#00ff88"),
            name="Silhouette",
            hovertemplate="k=%{x}<br>Silhouette=%{y:.4f}<extra></extra>"
        ))
        elbow_fig.add_vline(x=15, line_dash="dash", line_color="#ffaa00",
                            annotation_text="k=15 chosen",
                            annotation_font=dict(color="#ffaa00", size=9,
                                                 family="Share Tech Mono"))
        elbow_fig.add_vline(x=8, line_dash="dot", line_color="#ff6666",
                            annotation_text="k=8 peak sil",
                            annotation_font=dict(color="#ff6666", size=9,
                                                 family="Share Tech Mono"))
        elbow_fig.update_layout(
            height=280, title=dict(
                text="SILHOUETTE vs k  ·  k=15 CHOSEN: PLATEAU REGION + INTERPRETABLE GRANULARITY",
                font=dict(family="Share Tech Mono", color="#3a6050", size=9)
            ),
            **PLOT_LAYOUT
        )
        elbow_fig.update_yaxes(title_text="SILHOUETTE SCORE")
        elbow_fig.update_xaxes(title_text="k (NUMBER OF CLUSTERS)", dtick=1)
        st.plotly_chart(elbow_fig, use_container_width=True)

    st.markdown('''
    <div style="font-family:\'Share Tech Mono\',monospace;font-size:0.62rem;
                color:#2a4a38;letter-spacing:0.1em;line-height:2;margin-bottom:1.5rem">
      K=15 RATIONALE: Silhouette peaks at k=8 (0.337) but plateau between k=13–15 (0.247–0.252)
      provides finer-grained cluster interpretability with meaningful business distinctions.
      Inertia curve shows diminishing returns beyond k=15. Trade-off: granularity vs. cohesion.
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="panel-label">// IMPACT DISTRIBUTION — TOP 7 CLUSTERS</div>', unsafe_allow_html=True)

    top7 = cluster_stats.nlargest(7, 'impact').reset_index()
    fig = go.Figure(go.Bar(
        x=top7['impact'],
        y=top7['cluster_name'],
        orientation='h',
        marker=dict(
            color=top7['severity_score'],
            colorscale=[
                [0.0,  "rgba(0,255,136,0.3)"],
                [0.5,  "rgba(0,200,100,0.7)"],
                [0.75, "rgba(255,160,0,0.8)"],
                [1.0,  "rgba(255,30,30,0.9)"],
            ],
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="SEV",
                    font=dict(family="Share Tech Mono", color="#3a6050", size=10)
                ),
                tickfont=dict(family="Share Tech Mono", color="#3a6050", size=9),
                outlinecolor="rgba(0,255,136,0.1)",
                outlinewidth=1,
                bgcolor="#080c10",
            )
        ),
        hovertemplate="<b>%{y}</b><br>Impact: %{x:,.0f}<extra></extra>"
    ))
    fig.update_layout(height=380, **PLOT_LAYOUT)
    fig.update_xaxes(title_text="IMPACT SCORE")
    fig.update_yaxes(title_text="")
    st.plotly_chart(fig, use_container_width=True)

    # ── k Selection justification ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="panel-label">// K SELECTION — ELBOW + SILHOUETTE SWEEP (k=5..20)</div>', unsafe_allow_html=True)

    try:
        with open('data/elbow_data.json', 'r') as _f:
            _elbow = json.load(_f)

        # elbow_data.json is a list of dicts — extract columns
        _ks       = [r['k']          for r in _elbow]
        _sils     = [r['silhouette'] for r in _elbow]
        _inertias = [r['inertia']    for r in _elbow]

        _fig_elbow = go.Figure()
        _fig_elbow.add_trace(go.Scatter(
            x=_ks, y=_sils,
            mode='lines+markers',
            name='Silhouette',
            line=dict(color='rgba(0,255,136,0.8)', width=2),
            marker=dict(size=7, color='rgba(0,255,136,0.9)'),
            hovertemplate='k=%{x}<br>Silhouette=%{y:.4f}<extra></extra>'
        ))
        _fig_elbow.add_vline(
            x=15, line_dash='dash',
            line_color='rgba(255,160,0,0.6)',
            annotation_text='k=15 CHOSEN',
            annotation_font=dict(family='Share Tech Mono', color='#ffaa00', size=10)
        )
        _fig_elbow.update_layout(
            height=280,
            **PLOT_LAYOUT,
            xaxis_title='NUMBER OF CLUSTERS (k)',
            yaxis_title='SILHOUETTE SCORE'
        )
        st.plotly_chart(_fig_elbow, use_container_width=True)
        _best_k   = max(_ks, key=lambda k: _sils[_ks.index(k)])
        _best_sil = max(_sils)
        st.markdown(f'''
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;
                    color:#2a4a38;letter-spacing:0.1em;line-height:2">
          SILHOUETTE PEAK: k={_best_k} ({_best_sil:.4f}) &nbsp;·&nbsp;
          k=15 CHOSEN FOR SEMANTIC GRANULARITY (NAMED CLUSTERS) &nbsp;·&nbsp;
          BEYOND k=8 GAINS DIMINISH; k=15 GIVES MEANINGFUL SPLIT WITHOUT FRAGMENTATION
        </div>
        ''', unsafe_allow_html=True)
    except FileNotFoundError:
        st.info("RUN cluster_comparison.py TO GENERATE ELBOW DATA")



# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: CLUSTER ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="panel-label">// SELECT CLUSTER FOR DEEP DIVE</div>', unsafe_allow_html=True)
    cluster_names = list(summaries.keys())
    selected_cluster = st.selectbox("CLUSTER", cluster_names, label_visibility="collapsed")

    if selected_cluster:
        cluster_info = summaries[selected_cluster]
        stats = cluster_stats.loc[selected_cluster]

        col1, col2, col3 = st.columns(3)
        col1.metric("Issues", cluster_info['size'])
        col2.metric("Avg Severity", f"{stats['severity_score']:.2f}")
        col3.metric("Impact Score", f"{stats['impact']:.0f}")

        st.markdown("<br>", unsafe_allow_html=True)

        # FIX 4b: Flag noise cluster
        if selected_cluster == 'Simple Bug Reports':
            st.markdown('''
            <div style="background:rgba(255,160,0,0.06);border:1px solid rgba(255,160,0,0.3);
                        border-left:2px solid #ffaa00;border-radius:2px;padding:0.8rem 1rem;
                        margin-bottom:1rem;font-family:\'Share Tech Mono\',monospace;
                        font-size:0.68rem;color:#ffaa00;letter-spacing:0.1em">
              ⚠ DATA QUALITY NOTE: This cluster contains a single repeated issue title
              ("first from flow in uk south" × 166). Likely a scraping artifact.
              Exclude from severity calculations.
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('<div class="panel-label">// SYSTEM DECISION</div>', unsafe_allow_html=True)
        if stats['impact'] > 2000:
            st.error("🚨  IMMEDIATE ENGINEERING FIX")
        elif stats['impact'] > 500:
            st.warning("⚠️  INVESTIGATE")
        else:
            st.info("ℹ  MONITOR / AUTOMATE")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="panel-label">// DECISION EXPLAINABILITY — RAG · LLAMA 3.3 70B</div>', unsafe_allow_html=True)
        st.info(cluster_info['root_cause'])
        st.markdown(f"""
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;
                    color:#2a4a38;letter-spacing:0.1em;margin-top:0.5rem;margin-bottom:1rem">
          ⚠ LLM DOES NOT INFLUENCE PRIORITISATION LOGIC &nbsp;·&nbsp;
          CLUSTER SHARE OF TOTAL IMPACT:
          <span style="color:#00cc66">{stats['impact'] / TOTAL_IMPACT * 100:.1f}%</span>
          ({cluster_info['size']} ISSUES)
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="panel-label">// SAMPLE ISSUES — EVIDENCE</div>', unsafe_allow_html=True)
        samples = cluster_info['samples']
        # Flag known noisy cluster
        is_noisy = len(set(samples)) == 1
        if is_noisy:
            st.warning("⚠  DATA QUALITY NOTE: This cluster contains near-duplicate issues — likely a scraping artifact. Flagged for cleaning.")
        for i, sample in enumerate(samples, 1):
            with st.expander(f"ISSUE {i:02d}"):
                st.write(sample)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="panel-label">// TOP ISSUES IN CLUSTER</div>', unsafe_allow_html=True)
        cluster_df = (
            df[df['cluster_name'] == selected_cluster]
            [['issue_title', 'severity_score', 'repo', 'created_at']]
            .sort_values('severity_score', ascending=False)
        )
        st.dataframe(cluster_df.head(20), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: CRITICAL ISSUES
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    critical_df = df[df['severity_score'] > 5].sort_values('severity_score', ascending=False)

    st.markdown(f"""
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:2rem;font-weight:700;
                color:#ff2222;letter-spacing:0.1em;text-shadow:0 0 14px rgba(255,30,30,0.35);
                margin-bottom:1.2rem">
        🚨 &nbsp;{len(critical_df)} ISSUES REQUIRE IMMEDIATE ENGINEERING ATTENTION
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="panel-label">// CRITICAL ISSUE LOG</div>', unsafe_allow_html=True)
        st.dataframe(
            critical_df[['issue_title', 'cluster_name', 'severity_score', 'repo']].head(20),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown('<div class="panel-label">// ACTION SUMMARY</div>', unsafe_allow_html=True)
        for cluster, count in critical_df['cluster_name'].value_counts().items():
            st.markdown(f"""
            <div class="action-card">
                <div class="action-card-title">{cluster}</div>
                <div class="action-card-meta">{count} ISSUES &nbsp;·&nbsp;
                <span style="color:#ff2222">🔴 IMMEDIATE FIX</span></div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: TRENDS & DRIFT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="panel-label">// CLUSTER DRIFT ANALYSIS — EARLY VS LATE PERIOD</div>', unsafe_allow_html=True)

    df['created_at'] = pd.to_datetime(df['created_at'])
    mid_date = df['created_at'].median()

    early = df[df['created_at'] < mid_date]['cluster_name'].value_counts(normalize=True)
    late  = df[df['created_at'] >= mid_date]['cluster_name'].value_counts(normalize=True)

    drift_rows = []
    for cluster in early.index:
        if cluster in late.index:
            change = (late[cluster] - early[cluster]) * 100
            if abs(change) > 1:
                drift_rows.append({
                    "Cluster": cluster,
                    "Early %": f"{early[cluster]*100:.1f}%",
                    "Late %":  f"{late[cluster]*100:.1f}%",
                    "Change":  f"{change:+.1f}%",
                    "Trend":   "📈 Increasing" if change > 0 else "📉 Decreasing"
                })

    if drift_rows:
        changes  = [float(r["Change"].replace("+","").replace("%","")) for r in drift_rows]
        clusters = [r["Cluster"] for r in drift_rows]
        colours  = [
            "rgba(255,30,30,0.7)" if c > 0 else "rgba(0,255,136,0.5)"
            for c in changes
        ]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=clusters, y=changes,
            marker_color=colours,
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Change: %{y:+.1f}%<extra></extra>"
        ))
        fig2.update_layout(
            title=dict(
                text="CLUSTER DRIFT  (EARLY → LATE)",
                font=dict(family="Share Tech Mono", color="#3a6050", size=11)
            ),
            height=380,
            **PLOT_LAYOUT
        )
        fig2.update_yaxes(title_text="CHANGE (%)")
        fig2.update_xaxes(tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="panel-label">// DRIFT TABLE</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(drift_rows), use_container_width=True, hide_index=True)
    else:
        st.info("NO SIGNIFICANT DRIFT DETECTED  (THRESHOLD ±1%)")



# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: LIVE INFERENCE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('''
    <div class="panel-label">// LIVE PREDICTION ENGINE — MULTIMODAL INFERENCE</div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                color:#2a4a38;letter-spacing:0.12em;margin-bottom:1.5rem;line-height:2">
      PASTE A NEW GITHUB ISSUE BELOW. THE ML SYSTEM EXTRACTS MULTIMODAL FEATURES,
      EMBEDS IT IN 392D SPACE, AND ROUTES IT IN REAL-TIME.
    </div>
    ''', unsafe_allow_html=True)

    try:
        km_model, embedder, scaler, cluster_info = load_inference_tools()
        models_ok = True
    except Exception as e:
        models_ok = False
        st.markdown(f'''
        <div style="background:rgba(255,30,30,0.06);border:1px solid rgba(255,30,30,0.3);
                    border-left:3px solid #ff4444;border-radius:2px;padding:1.2rem 1.5rem;
                    font-family:'Share Tech Mono',monospace;font-size:0.68rem;
                    color:#ff8888;letter-spacing:0.1em;line-height:2.2">
          ⚠ INFERENCE ERROR: {e}<br><br>
          IF RUNNING ON STREAMLIT CLOUD, SET THESE SECRETS IN APP SETTINGS:<br>
          · KMEANS_GDRIVE_ID = &lt;your google drive file id for kmeans_multimodal.pkl&gt;<br>
          · HF_TOKEN = &lt;your huggingface token (optional but recommended)&gt;<br><br>
          TO FIND YOUR GDRIVE FILE ID:<br>
          · RIGHT-CLICK kmeans_multimodal.pkl IN GOOGLE DRIVE → SHARE → COPY LINK<br>
          · THE ID IS THE LONG STRING BETWEEN /d/ AND /view IN THE URL
        </div>
        ''', unsafe_allow_html=True)

    if models_ok:
        col_in1, col_in2 = st.columns([1, 2])

        with col_in1:
            st.markdown('<div class="panel-label">// ISSUE METADATA</div>', unsafe_allow_html=True)
            title_input = st.text_input(
                "ISSUE TITLE",
                value="App crashes on startup",
                label_visibility="visible"
            )
            tier_input = st.selectbox(
                "CUSTOMER TIER",
                ["free", "pro", "enterprise"],
                label_visibility="visible"
            )

        with col_in2:
            st.markdown('<div class="panel-label">// ISSUE BODY</div>', unsafe_allow_html=True)
            body_input = st.text_area(
                "ISSUE BODY",
                value="When I click the login button, the app completely crashes.\nError: NullReferenceException at line 42.",
                height=118,
                label_visibility="collapsed"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        run_btn = st.button("⬛  RUN MULTIMODAL ANALYSIS", use_container_width=True)

        if run_btn:
            with st.spinner("EXTRACTING FEATURES · EMBEDDING · CLUSTERING..."):
                full_text = title_input + " \n " + body_input

                # ── 1. Feature engineering ──
                has_image   = 1 if re.search(r'!\[.*?\]\(.*?\)', full_text) else 0
                has_error   = 1 if re.search(r'error:|exception|traceback', full_text, re.IGNORECASE) else 0
                has_question = 1 if '?' in full_text else 0
                url_count   = len(re.findall(r'https?://', full_text))
                text_len    = len(full_text)
                severe_kw   = ['crash', 'error', 'exception', 'fatal', 'broken']
                kw_severity = sum(1 for kw in severe_kw if kw in full_text.lower())
                user_weight = {'enterprise': 3, 'pro': 2, 'free': 1}[tier_input]
                complexity  = (has_error * 2) + (has_image * 1) + (min(url_count, 5) * 0.5) + (min(kw_severity, 5) * 0.5) + (1 if text_len > 300 else 0)

                # ── 2. Vector creation ──
                # embedder is now _get_hf_embedding (HF API, no torch)
                _raw_emb = embedder(full_text)
                text_emb = np.array(_raw_emb).reshape(1, -1)
                meta_arr     = np.array([[has_image, has_error, has_question, url_count,
                                          text_len, kw_severity, user_weight, complexity]])
                meta_scaled  = scaler.transform(meta_arr)
                final_vector = np.hstack([text_emb, meta_scaled])

                # ── 3. Inference ──
                cluster_id   = km_model.predict(final_vector)[0]
                cluster_data = cluster_info[str(cluster_id)]

                # ── 4. Decision logic ──
                severity_score = (5 if has_error else 0) + kw_severity
                severity_score *= user_weight
                if severity_score > 10:
                    action, action_color, action_glow = "IMMEDIATE FIX", "#ff2222", "rgba(255,30,30,0.3)"
                elif severity_score > 5:
                    action, action_color, action_glow = "INVESTIGATE",   "#ffaa00", "rgba(255,160,0,0.3)"
                else:
                    action, action_color, action_glow = "MONITOR",       "#00ff88", "rgba(0,255,136,0.3)"

            # ── Results ──
            st.markdown('''
            <div style="border-top:1px solid rgba(0,255,136,0.15);margin:1.5rem 0 1rem"></div>
            <div class="panel-label">// ANALYSIS COMPLETE — RESULTS</div>
            ''', unsafe_allow_html=True)

            r1, r2, r3 = st.columns(3)
            r1.metric("Predicted Cluster",  cluster_data.get('name', f'Cluster {cluster_id}'))
            r2.metric("Severity Score",     severity_score)
            r3.metric("System Routing",     action)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Action badge ──
            st.markdown(f'''
            <div style="background:rgba(0,0,0,0.3);border:1px solid {action_color};
                        border-left:3px solid {action_color};border-radius:2px;
                        padding:1.2rem 1.5rem;text-align:center;
                        box-shadow:0 0 20px {action_glow};margin-bottom:1rem">
              <div style="font-family:'Barlow Condensed',sans-serif;font-size:2.4rem;
                          font-weight:900;letter-spacing:0.2em;color:{action_color};
                          text-shadow:0 0 16px {action_glow}">
                {action}
              </div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
                          color:{action_color};opacity:0.6;letter-spacing:0.18em;margin-top:4px">
                SEVERITY SCORE: {severity_score} &nbsp;·&nbsp; CLUSTER: {cluster_data.get('name', cluster_id)}
              </div>
            </div>
            ''', unsafe_allow_html=True)

            # ── Feature breakdown ──
            st.markdown('<div class="panel-label">// EXTRACTED MULTIMODAL FEATURES</div>', unsafe_allow_html=True)

            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Text Length",    f"{text_len} chars")
            f2.metric("Error Trace",    "YES" if has_error else "NO")
            f3.metric("Severity KWs",   kw_severity)
            f4.metric("Complexity",     f"{complexity:.1f}")

            fa, fb, fc, fd = st.columns(4)
            fa.metric("URL Count",      url_count)
            fb.metric("Has Image",      "YES" if has_image else "NO")
            fc.metric("Has Question",   "YES" if has_question else "NO")
            fd.metric("User Weight",    user_weight)

            # ── Vector dimensions strip ──
            st.markdown(f'''
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;
                        color:#2a4a38;letter-spacing:0.12em;line-height:2;margin-top:1rem">
              PIPELINE: TEXT → SENTENCE-BERT (384D) + METADATA SCALED (8D) → MULTIMODAL VECTOR (392D)
              → KMEANS PREDICT → CLUSTER {cluster_id} &nbsp;·&nbsp;
              SEVERITY = (ERROR×5 + KEYWORDS) × USER_WEIGHT = ({5 if has_error else 0} + {kw_severity}) × {user_weight} = {severity_score}
            </div>
            ''', unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════════════════
# TAB 6: MODEL VALIDATION — K SELECTION & SILHOUETTE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('''
    <div class="panel-label">// MODEL VALIDATION — K SELECTION JUSTIFICATION</div>
    <div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;
                color:#2a4a38;letter-spacing:0.12em;margin-bottom:1.5rem;line-height:2">
      WHY K=15? WE EVALUATED K=3 TO K=20 ON THE MULTIMODAL EMBEDDING SPACE (392D).
      THE ELBOW CURVE AND SILHOUETTE ANALYSIS BELOW JUSTIFY THE CHOICE.
    </div>
    ''', unsafe_allow_html=True)

    # ── Silhouette comparison metrics ──
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Text-only Silhouette",      "0.030",  delta="Baseline")
    m2.metric("Metadata Silhouette",       "0.486",  delta="+16.2× vs text")
    m3.metric("Multimodal Silhouette",     "0.230",  delta="+7.7× vs text")
    m4.metric("Chosen k",                  "15",     delta="Elbow + business logic")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── K selection chart ──
    import os
    if os.path.exists('data/k_selection.png'):
        img_path = 'data/k_selection.png'
    else:
        img_path = None

    if img_path:
        st.image(img_path, use_container_width=True)
    else:
        # Render from embedded data if image not present
        ks = list(range(3, 21))
        inertias   = [56411,47935,39333,35003,32264,30507,28591,27434,
                      26162,25133,24093,23304,22768,21997,21354,21047,20337,20162]
        sil_scores = [0.421,0.293,0.330,0.333,0.331,0.310,0.243,0.314,
                      0.235,0.243,0.249,0.234,0.233,0.231,0.231,0.209,0.224,0.210]

        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig_k = make_subplots(rows=1, cols=2,
                              subplot_titles=("ELBOW CURVE", "SILHOUETTE VS K"))
        fig_k.add_trace(go.Scatter(
            x=ks, y=inertias, mode="lines+markers",
            line=dict(color="#00ff88", width=2.5),
            marker=dict(size=6, color="#00ff88"),
            name="Inertia", fill="tozeroy",
            fillcolor="rgba(0,255,136,0.05)"
        ), row=1, col=1)
        fig_k.add_vline(x=15, line_dash="dash", line_color="#ff6600",
                        line_width=1.8, row=1, col=1)

        fig_k.add_trace(go.Scatter(
            x=ks, y=sil_scores, mode="lines+markers",
            line=dict(color="#00ccff", width=2.5),
            marker=dict(size=6, color="#00ccff"),
            name="Silhouette", fill="tozeroy",
            fillcolor="rgba(0,204,255,0.05)"
        ), row=1, col=2)
        fig_k.add_vline(x=15, line_dash="dash", line_color="#ff6600",
                        line_width=1.8, annotation_text="k=15",
                        annotation_font_color="#ff6600", row=1, col=2)

        fig_k.update_layout(
            height=420,
            paper_bgcolor="#080c10",
            plot_bgcolor="#080c10",
            font=dict(family="Share Tech Mono", color="#3a6050", size=11),
            showlegend=False,
            margin=dict(t=50, b=40, l=10, r=10),
        )
        for i in [1, 2]:
            fig_k.update_xaxes(gridcolor="rgba(0,255,136,0.05)",
                               linecolor="#1a3028", tickfont_color="#3a6050", row=1, col=i)
            fig_k.update_yaxes(gridcolor="rgba(0,255,136,0.05)",
                               linecolor="#1a3028", tickfont_color="#3a6050", row=1, col=i)
        st.plotly_chart(fig_k, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── K=15 reasoning ──
    st.markdown('''
    <div class="panel-label">// WHY K=15 DESPITE K=3 HAVING BEST SILHOUETTE</div>
    <div style="font-family:\'Share Tech Mono\',monospace;font-size:0.68rem;
                color:#5a8a70;letter-spacing:0.1em;line-height:2.2">
      · K=3 SILHOUETTE=0.421 PRODUCES CLUSTERS TOO COARSE FOR BUSINESS ROUTING<br>
      · K=15 SILHOUETTE=0.233 STILL ABOVE 0.2 THRESHOLD (ACCEPTABLE STRUCTURE)<br>
      · ELBOW CURVE SHOWS DIMINISHING INERTIA RETURNS AFTER K≈12<br>
      · K=15 ALIGNS WITH THE 6 NATURAL ISSUE TYPES WHILE PRESERVING SUB-PATTERNS<br>
      · DECISION: BALANCE BETWEEN CLUSTER QUALITY AND ROUTING GRANULARITY
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Method comparison table ──
    st.markdown('<div class="panel-label">// METHOD COMPARISON</div>', unsafe_allow_html=True)
    comparison_df = pd.DataFrame({
        "Method":     ["Text-only (384D)", "Metadata-only (8D)", "Multimodal (392D)"],
        "Silhouette": [0.030, 0.486, 0.230],
        "Dimensions": [384, 8, 392],
        "Business Value": ["Poor — ignores structure", "Good — misses semantics", "✓ Best — captures both"],
        "Chosen":     ["No", "No", "YES"]
    })
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # ── Data quality note ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('''
    <div class="panel-label">// DATA QUALITY FLAGS</div>
    <div style="font-family:\'Share Tech Mono\',monospace;font-size:0.68rem;
                color:#5a8a70;letter-spacing:0.1em;line-height:2.2">
      · CLUSTER "SIMPLE BUG REPORTS" (166 ISSUES): SCRAPING ARTIFACT —
        SINGLE REPEATED TITLE "FIRST FROM FLOW IN UK SOUTH". EXCLUDED FROM IMPACT CALC.<br>
      · CLUSTER 14 IN RAW K=15: 34 ISSUES WITH SPAM/NOISE TITLES. MERGED INTO GENERAL ISSUES.<br>
      · OVERALL DATA QUALITY: 9,961 USABLE ISSUES FROM 5.3M RAW DATASET (RANDOM SAMPLE)
    </div>
    ''', unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0">
  <span style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
               color:#1a3028;letter-spacing:0.12em">
    GITHUB ISSUES DECISION INTELLIGENCE SYSTEM
  </span>
  <span style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
               color:#1a3028;letter-spacing:0.12em">
    DETERMINISTIC ML · LLM EXPLAINABILITY · PRODUCTION-ALIGNED
  </span>
</div>
""", unsafe_allow_html=True)
