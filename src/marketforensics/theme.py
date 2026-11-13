"""Premium fintech theme shared by every MarketForensics page."""

from __future__ import annotations

PALETTE = {
    "bg": "#0B1220",
    "panel": "rgba(17, 26, 45, 0.76)",
    "green": "#19C3B1",
    "red": "#F06A73",
    "amber": "#F5B544",
    "cyan": "#6E8BFF",
    "violet": "#8B7CFF",
    "ink": "#F8FAFC",
    "muted": "#94A3B8",
    "grid": "rgba(148,163,184,0.14)",
}

LABEL_COLOR = {
    "market_wide": "#6E8BFF",
    "stock_specific": "#F5B544",
    "volume_shock": "#19C3B1",
    "unknown": "#94A3B8",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@500;600;700&display=swap');

:root {
  --bg: #0B1220;
  --surface: #111A2D;
  --surface-2: #162138;
  --paper: #F7F9FC;
  --primary: #3B5BFF;
  --accent: #19C3B1;
  --text: #F8FAFC;
  --muted: #94A3B8;
  --stroke: rgba(148,163,184,.16);
}

html, body, [class*="css"] { font-family: "Inter", "Segoe UI", sans-serif; color: var(--text); }
h1, h2, h3, .hero h1, [data-testid="stHeading"] {
  font-family: "Sora", "Segoe UI", sans-serif !important;
  letter-spacing: -0.035em;
}
.stApp {
  background:
    radial-gradient(700px 420px at 86% -10%, rgba(59,91,255,.16), transparent 58%),
    radial-gradient(540px 360px at 10% 8%, rgba(25,195,177,.08), transparent 62%),
    var(--bg);
}
header[data-testid="stHeader"] { background: rgba(11,18,32,.72); backdrop-filter: blur(16px); }
section[data-testid="stSidebar"] {
  background: rgba(11,18,32,.94);
  border-right: 1px solid var(--stroke);
  backdrop-filter: blur(18px);
}
.block-container {
  max-width: 1220px;
  padding-top: 1.5rem;
  padding-bottom: 3rem;
  animation: enter .42s cubic-bezier(.2,.8,.2,1);
}
@keyframes enter { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }

.brand-lockup { margin: .3rem 0 1.2rem; }
.brand-lockup strong { font-family: "Sora"; letter-spacing: -.02em; }
.brand-lockup span { display:block; color:var(--muted); font-size:.78rem; margin-top:.2rem; }

.tape {
  overflow: hidden; white-space: nowrap;
  border: 1px solid var(--stroke);
  border-radius: 999px;
  background: rgba(17,26,45,.68);
  margin: 0 0 1rem;
}
.tape span { display: inline-block; padding: .48rem 0; animation: tape 38s linear infinite; font-size:.78rem; }
@keyframes tape { from { transform: translateX(0); } to { transform: translateX(-50%); } }
.up { color: var(--accent); font-weight: 600; }
.down { color: #F06A73; font-weight: 600; }

.hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0,1.08fr) minmax(280px,.92fr);
  gap: 2rem;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(59,91,255,.10), rgba(17,26,45,.78) 48%, rgba(25,195,177,.06));
  border: 1px solid var(--stroke);
  border-radius: 24px;
  padding: clamp(1.4rem,3vw,2.4rem);
  box-shadow: 0 24px 70px rgba(0,0,0,.24);
}
.hero-copy { align-self:center; position:relative; z-index:2; }
.hero h1 { font-size: clamp(2.2rem,5vw,4.1rem); line-height:1.02; margin:.35rem 0 .7rem; max-width:680px; }
.hero p { color:#C8D1E0; font-size:1.02rem; line-height:1.65; max-width:38rem; margin:0; }
.kicker { color:#8EA2FF; text-transform:uppercase; letter-spacing:.16em; font-size:.7rem; font-weight:600; }
.terminal-card {
  align-self:stretch; min-height:260px;
  background:rgba(9,15,27,.66);
  border:1px solid rgba(110,139,255,.24);
  border-radius:20px; padding:1rem;
  transform:perspective(900px) rotateY(-4deg) rotateX(2deg);
  transition:transform .35s ease, border-color .25s ease;
}
.terminal-card:hover { transform:perspective(900px) rotateY(0) rotateX(0) translateY(-3px); border-color:rgba(25,195,177,.5); }
.terminal-top { display:flex; justify-content:space-between; color:var(--muted); font-size:.72rem; margin-bottom:.8rem; }
.chart-line { width:100%; height:120px; }
.chart-line path { stroke-dasharray:700; stroke-dashoffset:700; animation:draw 2.2s ease forwards; }
@keyframes draw { to { stroke-dashoffset:0; } }
.terminal-row { display:flex; justify-content:space-between; border-top:1px solid var(--stroke); padding:.62rem .1rem; font-size:.78rem; }
.terminal-row b { color:var(--text); } .terminal-row span { color:var(--accent); }

.kpis { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.9rem; margin-top:1rem; }
.bento { display:grid; grid-template-columns:1.2fr .8fr .8fr; gap:.9rem; margin-top:.9rem; }
.glass {
  background:rgba(17,26,45,.76);
  border:1px solid var(--stroke);
  border-radius:20px;
  padding:1.05rem 1.1rem;
  transition:transform .25s ease,border-color .25s ease,background .25s ease;
}
.glass:hover { transform:translateY(-4px); border-color:rgba(59,91,255,.52); background:rgba(22,33,56,.9); }
.kpi .n { font-family:"Sora"; font-size:1.75rem; color:#AAB7FF; line-height:1.1; }
.kpi .label { color:var(--muted); font-size:.8rem; margin-top:.2rem; }
.bento h3 { margin:.1rem 0 .4rem; font-size:1rem; }
.bento p { margin:0; color:var(--muted); font-size:.86rem; line-height:1.45; }
.trust-strip {
  display:grid; grid-template-columns:repeat(4,1fr); gap:1px;
  margin-top:1rem; overflow:hidden; border:1px solid var(--stroke); border-radius:16px;
  background:var(--stroke);
}
.trust-strip div { background:#10192B; padding:.8rem; text-align:center; color:#C9D3E2; font-size:.78rem; }

.chip { display:inline-block; margin:.15rem .3rem .15rem 0; padding:.3rem .7rem; border-radius:999px; border:1px solid var(--stroke); background:rgba(11,18,32,.5); font-size:.8rem; }
.foot { margin-top:1.6rem; padding-top:.9rem; border-top:1px solid var(--stroke); color:var(--muted); font-size:.78rem; display:flex; justify-content:space-between; gap:1rem; }

div[data-testid="stMetric"], div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] {
  background:rgba(17,26,45,.58);
  border:1px solid var(--stroke);
  border-radius:18px;
  padding:.35rem .45rem .15rem;
}
div.stButton > button, button[kind="primary"], button[kind="secondary"] {
  border:0 !important; border-radius:12px !important;
  background:var(--primary) !important; color:white !important;
  font-family:"Inter" !important; font-weight:600 !important;
  padding:.58rem 1.2rem !important;
  box-shadow:0 10px 25px rgba(59,91,255,.22);
  transition:transform .2s ease,box-shadow .2s ease,filter .2s ease !important;
}
div.stButton > button:hover { transform:translateY(-2px); box-shadow:0 15px 34px rgba(59,91,255,.34); filter:brightness(1.08); }
div.stButton > button:active { transform:scale(.98); }

div[data-testid="stSidebar"] div[role="radiogroup"] label {
  border-radius:10px; padding:.42rem .65rem; margin-bottom:.12rem;
  border:1px solid transparent; transition:all .2s ease;
}
div[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:rgba(59,91,255,.08); transform:translateX(2px); }
div[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background:rgba(59,91,255,.14); border-color:rgba(59,91,255,.45); }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
  border-radius:12px !important; background:rgba(17,26,45,.85) !important; border-color:var(--stroke) !important;
}

@media (max-width:900px) {
  .hero { grid-template-columns:1fr; }
  .terminal-card { min-height:230px; transform:none; }
  .kpis { grid-template-columns:1fr 1fr; }
  .bento { grid-template-columns:1fr 1fr; }
  .trust-strip { grid-template-columns:1fr 1fr; }
}
@media (max-width:560px) {
  .block-container { padding-left:.8rem; padding-right:.8rem; }
  .hero { border-radius:18px; padding:1.2rem; }
  .kpis,.bento,.trust-strip { grid-template-columns:1fr; }
  .hero h1 { font-size:2.35rem; }
  .foot { display:block; }
}
"""


def inject_css() -> None:
    import streamlit as st

    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
