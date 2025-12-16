import pandas as pd
import streamlit as st
from pathlib import Path

# --------------------------------------------------
# Page config (MUST be first Streamlit call)
# --------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="MPOY Tracker"
)

# --------------------------------------------------
# Load processed data
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data/processed/mpoy_tracker_latest.csv"

df = pd.read_csv(DATA_PATH)

# --------------------------------------------------
# Compute Top 5 MPOY candidates
# --------------------------------------------------
top_5_mpoy = (
    df.sort_values("mid_score")
      .head(5)
      .reset_index(drop=True)
)

# --------------------------------------------------
# Page header
# --------------------------------------------------
st.title("🏀 Mid Player of the Year Tracker")
st.write(f"Total Qualified Players: {len(df)}")

# --------------------------------------------------
# Flashcard-style MPOY candidates
# --------------------------------------------------
st.subheader("🏆 Top 5 MPOY Candidates")

cols = st.columns(5)

for rank, (col, (_, row)) in enumerate(zip(cols, top_5_mpoy.iterrows()), start=1):
    with col:
        headshot_url = (
            f"https://cdn.nba.com/headshots/nba/latest/260x190/"
            f"{int(row['player_id'])}.png"
        )

        st.markdown(
f"""
<div style="
    background: linear-gradient(180deg, #0B6623 0%, #0A4F1A 100%);
    border-radius: 20px;
    padding: 16px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
">

    <div style="font-size: 14px; opacity: 0.85;">#{rank}</div>

    <h4 style="margin: 6px 0 10px 0;">
        {row['player_name'].upper()}
    </h4>

    <img src="{headshot_url}"
         style="width: 100%; border-radius: 12px; margin-bottom: 12px;">

    <div style="
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
        font-size: 14px;
        background: #D9E5D6;
        color: #000;
        border-radius: 10px;
        padding: 8px;
    ">
        <div><b>{row['pts']:.1f}</b><br>PPG</div>
        <div><b>{row['reb']:.1f}</b><br>RPG</div>
        <div><b>{row['ast']:.1f}</b><br>APG</div>
        <div><b>{row['stl']:.1f}</b><br>SPG</div>
        <div><b>{row['blk']:.1f}</b><br>BPG</div>
        <div><b>{row['efg_pct'] * 100:.1f}</b><br>eFG%</div>
    </div>

    <div style="
        margin-top: 10px;
        font-size: 12px;
        letter-spacing: 1px;
        opacity: 0.9;
    ">
        MID SCORE
    </div>

    <div style="
        font-size: 28px;
        font-weight: bold;
        background: #E6E6E6;
        color: #000;
        border-radius: 12px;
        padding: 6px;
        margin-top: 4px;
    ">
        {row['mid_score']:.3f}
    </div>

</div>
""",
unsafe_allow_html=True
)
