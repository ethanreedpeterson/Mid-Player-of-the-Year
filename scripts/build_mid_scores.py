import pandas as pd
import numpy as np

# --------------------------------------------------
# Load raw data
# --------------------------------------------------

player_stats = pd.read_csv("data/raw/all_player_stats_backup.csv")
league_averages = pd.read_csv("data/raw/all_league_averages_backup.csv")

# --------------------------------------------------
# Calculate MID for a single season
# --------------------------------------------------
def calculate_mid_for_season(season_df: pd.DataFrame,
                             league_df: pd.DataFrame) -> pd.DataFrame:
    # --- Determine season safely ---
    season_vals = season_df["Season"].unique()
    if len(season_vals) != 1:
        raise ValueError("Expected exactly one season per group")

    season = int(season_vals[0])

    # --- Era-based metric selection ---
    if season < 1974:
        metrics = ["PTS", "TRB", "AST", "FG%"]
    elif season < 1979:
        metrics = ["PTS", "TRB", "AST", "STL", "BLK", "FG%"]
    else:
        metrics = ["PTS", "TRB", "AST", "STL", "BLK", "eFG%"]

    # --- Pull league averages for this season ---
    league_row = league_df.loc[league_df["Season"] == season]
    if league_row.shape[0] != 1:
        raise ValueError(f"League averages missing or duplicated for season {season}")

    league_row = league_row.iloc[0]

    # --- Z-score calculation ---
    for metric in metrics:
        mean_val = league_row[metric]
        sd_val = season_df[metric].std(skipna=True, ddof=1)  # matches R sd()

        season_df[f"Z_{metric}"] = (season_df[metric] - mean_val) / sd_val

    # --- MID score ---
    z_cols = [f"Z_{m}" for m in metrics]
    season_df["MID"] = season_df[z_cols].abs().sum(axis=1, skipna=True)

    # --- Final output ---
    out_cols = ["Player", "Team", "Season"] + metrics + ["MID"]

    return (
        season_df[out_cols]
        .sort_values("MID", ascending=True)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# Apply to all seasons
# --------------------------------------------------
all_mid_scores = (
    player_stats
        .groupby("Season", group_keys=False)
        .apply(
            lambda df: calculate_mid_for_season(
                df.copy(),
                league_df=league_averages
            )
        )
        .reset_index(drop=True)
)

# --------------------------------------------------
# Save processed output
# --------------------------------------------------
all_mid_scores["MID"] = all_mid_scores["MID"].map(lambda x: f"{x:.3f}")

all_mid_scores.to_csv(
    "data/processed/all_mid_scores_by_season.csv",
    index = False
)