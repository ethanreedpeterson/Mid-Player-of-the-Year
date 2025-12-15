import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(layout = "wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-left: 3rem;
        padding-right: 3rem;
    }

    div[data-testid="stDataFrame"] {
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html = True
)

st.title("Season Explorer")

# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/all_mid_scores_by_season.csv")

df = load_data()

# --------------------------------------------------
# Season selector (newest → oldest)
# --------------------------------------------------
st.markdown("")  # small spacing

col1, col2 = st.columns(2)

with col1:
    seasons = sorted(df["Season"].unique(), reverse=True)
    season = st.selectbox(
        "Select season",
        seasons,
        index=0
    )

with col2:
    rows_per_page = st.selectbox(
        "Rows per page",
        ["All", 25, 50, 100],
        index=0
    )

# --------------------------------------------------
# Filter + rank
# --------------------------------------------------
season_df = (
    df[df["Season"] == season]
      .sort_values("MID", ascending=True)
      .reset_index(drop=True)
)

season_df["Rk"] = season_df.index + 1
winner = season_df.iloc[0]

# --------------------------------------------------
# Header
# --------------------------------------------------
st.subheader(f"🏆 {season - 1}–{str(season)[-2:]} MPOY")
st.success(
    f"**{winner['Player']}** ({winner['Team']}) — "
    f"MID Score: **{winner['MID']:.3f}**"
)


# --------------------------------------------------
# Prepare display dataframe
# --------------------------------------------------
season_df_display = season_df.copy()

# Rename MID
season_df_display = season_df_display.rename(columns={"MID": "MID Score"})

# --------------------------------------------------
# Shooting metric logic by era (DEFINE ONCE)
# --------------------------------------------------
shooting_col = None

if season >= 1980 and "eFG%" in season_df_display.columns:
    shooting_col = "eFG%"
    season_df_display["eFG%"] = season_df_display["eFG%"] * 100
    season_df_display = season_df_display.drop(columns=["FG%"], errors="ignore")

elif "FG%" in season_df_display.columns:
    shooting_col = "FG%"
    season_df_display["FG%"] = season_df_display["FG%"] * 100
    season_df_display = season_df_display.drop(columns=["eFG%"], errors="ignore")

mid_min = season_df_display["MID Score"].min()
mid_max = season_df_display["MID Score"].max()

column_order = [
    "Rk",
    "Team",
    "Player",
    "MID Score",
    "PTS",
    "TRB",
    "AST",
    "STL",
    "BLK",
    shooting_col
]

column_order = [c for c in column_order if c is not None and c in season_df_display.columns]
season_df_display = season_df_display[column_order]

# --------------------------------------------------
# Pagination controls
# --------------------------------------------------
if rows_per_page == "All":
    paged_df = season_df_display
else:
    page_size = int(rows_per_page)
    total_rows = len(season_df_display)
    total_pages = (total_rows - 1) // page_size + 1

    page = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1
    )

    start = (page - 1) * page_size
    end = start + page_size
    paged_df = season_df_display.iloc[start:end]

# --------------------------------------------------
# Styling
# --------------------------------------------------
styled_df = (
    paged_df
        .style
        .background_gradient(
            subset=["MID Score"],
            cmap="RdBu_r",
            vmin = mid_min,
            vmax = mid_max
        )
        .set_properties(
            subset=["Team"],
            **{"text-align": "center"}
        )
)


# --------------------------------------------------
# Render table
# --------------------------------------------------
column_config = {
    "Team": st.column_config.TextColumn(),
    "MID Score": st.column_config.NumberColumn(format="%.3f"),
    "PTS": st.column_config.NumberColumn(format="%.1f"),
    "TRB": st.column_config.NumberColumn(format="%.1f"),
    "AST": st.column_config.NumberColumn(format="%.1f"),
    "STL": st.column_config.NumberColumn(format="%.1f"),
    "BLK": st.column_config.NumberColumn(format="%.1f"),
}

if shooting_col:
    column_config[shooting_col] = st.column_config.NumberColumn(format="%.1f")

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True,
    column_config=column_config
)
