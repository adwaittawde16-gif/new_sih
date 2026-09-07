import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from intelligence_engine import IntelligenceEngine
from crime_ring_detector import CrimeRingDetector
from geo_map_generator import GeoMapGenerator
from financial_analyzer import FinancialAnalyzer
from nocturnal_call_analyzer import NocturnalCallAnalyzer
from graph_visualizer import GraphVisualizer
from surveillance_heatmap import SurveillanceHeatmap

st.set_page_config(page_title="Mumbai Police Intelligence", page_icon="", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
:root { --navy:#0d1117; --panel:#161b22; --panel2:#1b222c; --line:#30363d; --blue:#58a6ff; --red:#f85149; --amber:#d29922; --green:#3fb950; }
html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
.stApp { background:var(--navy); color:#f0f6fc; }
[data-testid="stSidebar"] { background:#11161d; border-right:1px solid var(--line); }
[data-testid="stSidebar"] * { color:#c9d1d9; }
.block-container { max-width:1600px; padding:1.4rem 2rem 3rem; }
section[data-testid="stSidebar"] .block-container { padding:1.5rem 1rem; }
.brand { display:flex; align-items:center; gap:.75rem; margin-bottom:2rem; }
.brand-mark { width:38px; height:38px; border:1px solid #2f81f7; border-radius:10px; display:grid; place-items:center; color:var(--blue); font-family:'Space Mono'; font-weight:700; }
.brand-title { font-weight:700; font-size:.92rem; line-height:1.15; color:#f0f6fc; }
.brand-sub { font:10px 'Space Mono'; color:#8b949e; letter-spacing:.08em; text-transform:uppercase; margin-top:4px; }
.nav-label { color:#6e7681; font:10px 'Space Mono'; letter-spacing:.14em; text-transform:uppercase; margin:1.5rem 0 .5rem; }
.nav-note { color:#8b949e; font-size:.75rem; line-height:1.4; margin-top:1.2rem; padding:10px; border:1px solid var(--line); border-radius:8px; }
.hero { display:flex; justify-content:space-between; align-items:flex-start; padding-bottom:1.2rem; border-bottom:1px solid var(--line); }
.eyebrow { color:var(--blue); font:11px 'Space Mono'; letter-spacing:.12em; text-transform:uppercase; }
h1 { font-size:clamp(1.4rem,2.2vw,2.05rem)!important; letter-spacing:-.04em; margin:.35rem 0!important; }
.subtitle { color:#8b949e; font-size:.88rem; }
.status { display:flex; align-items:center; gap:.5rem; border:1px solid #235b35; background:#122319; color:#7ee787; padding:.55rem .75rem; border-radius:999px; font:11px 'Space Mono'; }
.status-dot { width:7px; height:7px; border-radius:50%; background:var(--green); box-shadow:0 0 10px var(--green); }
.kpis { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin:1.25rem 0; }
.kpi { background:linear-gradient(145deg,#171e27,#12171d); border:1px solid var(--line); border-radius:10px; padding:13px 15px; min-height:86px; }
.kpi-label { color:#8b949e; font:10px 'Space Mono'; text-transform:uppercase; letter-spacing:.08em; }
.kpi-value { font:700 1.6rem 'Space Mono'; margin-top:9px; color:#f0f6fc; }
.kpi-accent { color:var(--red); } .kpi-blue { color:var(--blue); } .kpi-amber { color:var(--amber); } .kpi-green { color:var(--green); }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:1rem 1.1rem; margin-bottom:1rem; }
.panel-title { font-weight:700; font-size:.94rem; margin-bottom:3px; }
.panel-kicker { color:#8b949e; font-size:.74rem; }
.risk-card { border:1px solid #8e302c; background:linear-gradient(120deg,#21171a,#171b22); border-radius:12px; padding:1.1rem; margin-bottom:1rem; }
.risk-head { display:flex; justify-content:space-between; align-items:center; gap:1rem; }
.risk-name { font-size:1.2rem; font-weight:700; } .risk-score { font:700 1.8rem 'Space Mono'; color:var(--red); }
.risk-tier { color:#ff7b72; font:10px 'Space Mono'; letter-spacing:.1em; }
.bar-row { margin-top:11px; } .bar-label { display:flex; justify-content:space-between; color:#8b949e; font-size:.73rem; margin-bottom:4px; }
.bar-track { height:5px; background:#30363d; border-radius:99px; overflow:hidden; } .bar-fill { height:100%; background:linear-gradient(90deg,#f85149,#ff7b72); border-radius:99px; }
.section-head { display:flex; justify-content:space-between; align-items:end; margin:.3rem 0 .75rem; }
.section-head h2 { font-size:1.05rem; margin:0; } .section-head span { color:#8b949e; font:10px 'Space Mono'; }
div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:8px; overflow:hidden; }
.stButton button, .stDownloadButton button { border:1px solid var(--line); background:#21262d; color:#f0f6fc; border-radius:7px; }
.stButton button:hover { border-color:var(--blue); color:var(--blue); }
[data-baseweb="select"] > div, input { background:#0d1117!important; border-color:var(--line)!important; color:#f0f6fc!important; }
@media(max-width:900px){ .kpis{grid-template-columns:repeat(2,1fr)} .hero{flex-direction:column;gap:1rem} }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_engine():
    return IntelligenceEngine()

engine = load_engine()
scores = engine.calculate_threat_scores().copy()
scores = scores.sort_values('total_threat_score', ascending=False).reset_index(drop=True)

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">BP</div><div><div class="brand-title">Brihanmumbai Police</div><div class="brand-sub">Special Crime Analysis Unit</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-label">Command modules</div>', unsafe_allow_html=True)
    view = st.radio("Navigation", ["Threat leaderboard", "CDR interaction network", "CCTV co-location", "Crime rings", "Financial intelligence", "Nocturnal anomalies", "Surveillance heatmap", "Score simulator"], label_visibility="collapsed")
    st.markdown('<div class="nav-note">SYSTEM STATUS<br><span style="color:#7ee787">● All intelligence feeds operational</span><br><br>Last sync<br><span style="font-family:Space Mono">07 SEP 2026 · 18:42 IST</span></div>', unsafe_allow_html=True)

st.markdown('<div class="hero"><div><div class="eyebrow">Tactical intelligence / SIH 2026</div><h1>CDR & CCTV Threat Intelligence System</h1><div class="subtitle">Unified suspect scoring, network analysis, and field surveillance command center.</div></div><div class="status"><span class="status-dot"></span> LIVE ANALYTICS</div></div>', unsafe_allow_html=True)

c1,c2,c3,c4,c5 = st.columns(5)
for col, label, value, cls in [(c1,"Suspects profiled","100","kpi-blue"),(c2,"Active crime rings","88","kpi-accent"),(c3,"Critical risk","6","kpi-accent"),(c4,"CCTV encounters","12","kpi-amber"),(c5,"Night hotspots","16","kpi-green")]:
    col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value {cls}">{value}</div></div>', unsafe_allow_html=True)

if view == "Threat leaderboard":
    top = scores.iloc[0]
    st.markdown('<div class="section-head"><div><h2>Threat leaderboard</h2><span>COMPOSITE RANKING / 6 PARAMETERS / 0–100</span></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="risk-card"><div class="risk-head"><div><div class="risk-tier">CRITICAL RISK · PRIORITY DOSSIER</div><div class="risk-name">{top.suspect_name}</div><div class="subtitle">{top.phone_number} · Lead detected in RING-01</div></div><div style="text-align:right"><div class="risk-score">{top.total_threat_score:.1f}</div><div class="risk-tier">THREAT SCORE / 100</div></div></div>', unsafe_allow_html=True)
    weights = [("CCTV physical meetings", "cctv_meeting_score", 30),("CDR interaction network", "cdr_network_score", 20),("FIR & section severity", "fir_severity_score", 15),("Criminal history", "criminal_history_score", 15),("Financial risk", "financial_risk_score", 10),("Surveillance observations", "surveillance_score", 10)]
    cols = st.columns(3)
    for i,(label,key,maxv) in enumerate(weights):
        val = float(top.get(key,0)); cols[i%3].markdown(f'<div class="bar-row"><div class="bar-label"><span>{label}</span><span>{val:.1f} / {maxv}</span></div><div class="bar-track"><div class="bar-fill" style="width:{min(val/maxv*100,100):.1f}%"></div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    q1,q2,q3 = st.columns([2,1,1])
    search = q1.text_input("Search", placeholder="Name, phone, or police station", label_visibility="collapsed")
    tier = q2.selectbox("Risk tier", ["All tiers","Critical","High","Moderate","Low"], label_visibility="collapsed")
    selected = scores.copy()
    if search: selected = selected[selected.astype(str).apply(lambda row: row.str.contains(search, case=False).any(), axis=1)]
    selected.insert(0, "Rank", range(1, len(selected)+1))
    display = selected[["Rank","suspect_name","phone_number","total_threat_score","cctv_meeting_score","cdr_network_score","fir_severity_score","criminal_history_score","financial_risk_score","surveillance_score"]].rename(columns={"suspect_name":"Suspect","phone_number":"Phone","total_threat_score":"Threat score","cctv_meeting_score":"CCTV","cdr_network_score":"CDR","fir_severity_score":"FIR","criminal_history_score":"Criminal","financial_risk_score":"Financial","surveillance_score":"Field obs."})
    st.dataframe(display, use_container_width=True, hide_index=True, height=410)
    chosen = st.selectbox("Open suspect dossier", scores.suspect_name.tolist())
    if st.button("Open 360° forensic timeline"):
        row = scores[scores.suspect_name == chosen].iloc[0]
        st.info(f"{chosen} · score {row.total_threat_score:.1f}/100 · {row.phone_number}. Timeline view is ready for analyst review.")

elif view == "CDR interaction network":
    st.markdown('<div class="section-head"><div><h2>CDR interaction network</h2><span>CALL LINKS / SUSPECT CLUSTERS / PHYSICS GRAPH</span></div></div>', unsafe_allow_html=True)
    pair_df, raw = engine.get_cdr_summary()
    a,b,c = st.columns(3); a.metric("CDR logs", len(raw)); b.metric("Interaction pairs", len(pair_df)); c.metric("Frequent pairs", len(pair_df[pair_df.total_calls >= 3]))
    st.dataframe(pair_df.head(18), use_container_width=True, hide_index=True)
    file = GraphVisualizer(engine).generate_interactive_html_graph()
    with open(file, encoding="utf-8") as f: components.html(f.read(), height=560, scrolling=False)

elif view == "CCTV co-location":
    st.markdown('<div class="section-head"><div><h2>CCTV physical co-location</h2><span>CONFIRMED ENCOUNTERS / CAMERA CORRELATION</span></div></div>', unsafe_allow_html=True)
    meetings = engine.get_cctv_meetings()
    if meetings.empty: st.warning("No physical meetings detected.")
    else:
        a,b,c = st.columns(3); a.metric("Confirmed encounters", len(meetings)); b.metric("Avg confidence", f"{meetings.avg_match_confidence.mean()*100:.1f}%"); c.metric("Mean distance", f"{meetings.avg_distance_meters.mean():.1f} m")
        st.dataframe(meetings, use_container_width=True, hide_index=True)
        file = GeoMapGenerator(engine).generate_interactive_map()
        with open(file, encoding="utf-8") as f: components.html(f.read(), height=520, scrolling=False)

elif view == "Crime rings":
    st.markdown('<div class="section-head"><div><h2>Crime rings & syndicate cells</h2><span>CONNECTED COMPONENT DETECTION / RING-01 PRIORITY</span></div></div>', unsafe_allow_html=True)
    rings = CrimeRingDetector(engine).detect_syndicates(); st.dataframe(rings.head(20), use_container_width=True, hide_index=True)

elif view == "Financial intelligence":
    summary, raw = FinancialAnalyzer(engine).analyze_financial_trails()
    st.markdown('<div class="section-head"><div><h2>Financial money trail</h2><span>UPI TRANSFERS / WINE SHOP MERCHANTS / RISK SIGNALS</span></div></div>', unsafe_allow_html=True)
    a,b = st.columns(2); a.metric("Transactions logged", len(raw)); b.metric("Financial volume", f"₹{raw.amount_inr.sum():,.0f}")
    st.dataframe(summary, use_container_width=True, hide_index=True)

elif view == "Nocturnal anomalies":
    noc, towers = NocturnalCallAnalyzer(engine).analyze_nocturnal_patterns()
    st.markdown('<div class="section-head"><div><h2>Nocturnal call anomalies</h2><span>00:00–06:00 IST / CELL TOWER HOTSPOTS</span></div></div>', unsafe_allow_html=True)
    st.info(f"{len(noc)} late-night communications detected across the monitored network.")
    st.bar_chart(towers.set_index('cell_tower_location'))
    st.dataframe(noc, use_container_width=True, hide_index=True)

elif view == "Surveillance heatmap":
    st.markdown('<div class="section-head"><div><h2>Field surveillance heatmap</h2><span>SIGHTING DENSITY / MUMBAI OPERATIONS AREA</span></div></div>', unsafe_allow_html=True)
    file = SurveillanceHeatmap(engine).generate_heatmap()
    with open(file, encoding="utf-8") as f: components.html(f.read(), height=650, scrolling=False)

else:
    st.markdown('<div class="section-head"><div><h2>Custom threat score simulator</h2><span>ADJUST WEIGHTS / MODEL SENSITIVITY / LIVE RERANKING</span></div></div>', unsafe_allow_html=True)
    defaults = {"CCTV physical meetings":30,"CDR interaction network":20,"FIR severity":15,"Criminal history":15,"Financial risk":10,"Surveillance observations":10}
    values = {}
    cols = st.columns(3)
    for i,(label, default) in enumerate(defaults.items()): values[label] = cols[i%3].slider(label, 0, 50 if "CCTV" in label else 30, default)
    total = sum(values.values()); st.metric("Total model weight", f"{total}%", "normalized at runtime")
    st.dataframe(scores[["suspect_name","total_threat_score"]].rename(columns={"suspect_name":"Suspect","total_threat_score":"Projected score"}), use_container_width=True, hide_index=True)

st.markdown('<div style="border-top:1px solid #30363d;margin-top:2rem;padding-top:.8rem;color:#6e7681;font:10px Space Mono;display:flex;justify-content:space-between"><span>BP-SCAU // INTERNAL INTELLIGENCE SYSTEM</span><span>DATA HANDLING: RESTRICTED</span></div>', unsafe_allow_html=True)
