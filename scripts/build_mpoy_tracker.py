from nba_api.stats.endpoints import LeagueDashPlayerStats, LeagueDashTeamStats
from nba_api.stats.static import teams
import pandas as pd
import numpy as np
from math import ceil
from pathlib import Path
from nba_api.stats.static import teams

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

SEASON = "2025-26"
SEASON_YEAR = 2026
DATE_FROM = "2025-10-01"
DATE_TO   = "2025-12-31"

QUAL_PCT = 0.70
OUTPUT_PATH = Path("data/processed/mpoy_tracker_latest.csv")

# --------------------------------------------------
# LOAD PLAYER STATS
# --------------------------------------------------

player_stats = (
    LeagueDashPlayerStats(
        season=SEASON,
        season_type_all_star="Regular Season",
        per_mode_detailed="PerGame",
        date_from_nullable=DATE_FROM,
        date_to_nullable=DATE_TO
    )
    .get_data_frames()[0]
)

player_stats.columns = player_stats.columns.str.lower()

# --------------------------------------------------
# LOAD TEAM STATS
# --------------------------------------------------

team_stats = (
    LeagueDashTeamStats(
        season=SEASON,
        season_type_all_star="Regular Season",
        per_mode_detailed="PerGame",
        date_from_nullable=DATE_FROM,
        date_to_nullable=DATE_TO
    )
    .get_data_frames()[0]
)

team_stats.columns = team_stats.columns.str.lower()

# --------------------------------------------------
# TEAM LOOKUP TABLE
# --------------------------------------------------

team_info = (
    pd.DataFrame(teams.get_teams())
    .rename(columns={
        "id": "team_id",
        "abbreviation": "team_abbreviation"
    })[["team_id", "team_abbreviation"]]
)

team_stats = team_stats.merge(
    team_info,
    on="team_id",
    how="left"
)

# --------------------------------------------------
# FILTER QUALIFIED PLAYERS + COMPUTE EFG%
# --------------------------------------------------

qualified_players = (
    player_stats
    .merge(
        team_stats[["team_abbreviation", "gp"]]
            .rename(columns={"gp": "team_gp"}),
        on="team_abbreviation",
        how="left"
    )
)

qualified_players["gp_required"] = np.ceil(
    qualified_players["team_gp"] * QUAL_PCT
)

qualified_players["qualifies"] = (
    qualified_players["gp"] >= qualified_players["gp_required"]
)

qualified_players = (
    qualified_players
    .loc[qualified_players["qualifies"]]
    .assign(
        season=SEASON_YEAR,
        efg_pct=lambda df: (df["fgm"] + 0.5 * df["fg3m"]) / df["fga"]
    )
)

# --------------------------------------------------
# LEAGUE AVERAGES (MID SCORE BASELINE)
# --------------------------------------------------

league_avgs = pd.DataFrame({
    "season": [SEASON_YEAR],
    "pts_lg": [qualified_players["pts"].mean()],
    "reb_lg": [qualified_players["reb"].mean()],
    "ast_lg": [qualified_players["ast"].mean()],
    "stl_lg": [qualified_players["stl"].mean()],
    "blk_lg": [qualified_players["blk"].mean()],
    "efg_pct_lg": [qualified_players["efg_pct"].mean()],
})

# --------------------------------------------------
# MID SCORE CALCULATION
# --------------------------------------------------

def calculate_mid_scores(players: pd.DataFrame, league: pd.DataFrame) -> pd.DataFrame:
    df = players.merge(league, on="season", how="left")

    df["Z_PTS"] = (df["pts"] - df["pts_lg"]) / df["pts"].std(ddof=0)
    df["Z_TRB"] = (df["reb"] - df["reb_lg"]) / df["reb"].std(ddof=0)
    df["Z_AST"] = (df["ast"] - df["ast_lg"]) / df["ast"].std(ddof=0)
    df["Z_STL"] = (df["stl"] - df["stl_lg"]) / df["stl"].std(ddof=0)
    df["Z_BLK"] = (df["blk"] - df["blk_lg"]) / df["blk"].std(ddof=0)
    df["Z_EFF"] = (df["efg_pct"] - df["efg_pct_lg"]) / df["efg_pct"].std(ddof=0)

    df["mid_score"] = (
        df["Z_PTS"].abs() +
        df["Z_TRB"].abs() +
        df["Z_AST"].abs() +
        df["Z_STL"].abs() +
        df["Z_BLK"].abs() +
        df["Z_EFF"].abs()
    )

    return df[
        [
            "season", "player_name", "team_abbreviation",
            "pts", "reb", "ast", "stl", "blk", "efg_pct",
            "mid_score", "player_id"
        ]
    ].sort_values("mid_score")

# --------------------------------------------------
# FINAL OUTPUT
# --------------------------------------------------

player_mid_scores = calculate_mid_scores(
    qualified_players,
    league_avgs
)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

print("FINAL COLUMNS:", player_mid_scores.columns.tolist())
player_mid_scores.to_csv(OUTPUT_PATH, index=False)

print(f"✅ MPOY tracker updated: {OUTPUT_PATH}")
print(f"Season: {SEASON}")
print(f"Qualified players: {len(qualified_players)}")