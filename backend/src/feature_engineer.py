import pandas as pd
import os

PROCESSED_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')

def build_cricket_features(df):
    """
    Input:  raw ball-by-ball dataframe
    Output: one row per match with features for the model
    """
    print(f"Building features from {len(df)} deliveries...")

    match_features = []

    for match_id, match_df in df.groupby('match_id'):
        try:
            # --- Innings 1 ---
            inn1 = match_df[match_df['innings'] == 1]
            inn2 = match_df[match_df['innings'] == 2]

            if inn1.empty or inn2.empty:
                continue

            team1 = inn1['batting_team'].iloc[0] if 'batting_team' in inn1.columns else 'unknown'
            team2 = inn2['batting_team'].iloc[0] if 'batting_team' in inn2.columns else 'unknown'

            inn1_runs = inn1['runs_off_bat'].sum() + inn1['extras'].sum() \
                        if 'extras' in inn1.columns else inn1['runs_off_bat'].sum()
            inn2_runs = inn2['runs_off_bat'].sum() + inn2['extras'].sum() \
                        if 'extras' in inn2.columns else inn2['runs_off_bat'].sum()

            inn1_wickets = inn1['wicket_type'].notna().sum() \
                           if 'wicket_type' in inn1.columns else 0
            inn2_wickets = inn2['wicket_type'].notna().sum() \
                           if 'wicket_type' in inn2.columns else 0

            inn1_balls = len(inn1)
            inn2_balls = len(inn2)

            # --- Winner ---
            winner = 1 if inn1_runs > inn2_runs else 0  # 1 = team1 wins

            match_features.append({
                'match_id':        match_id,
                'team1':           team1,
                'team2':           team2,
                'inn1_runs':       inn1_runs,
                'inn1_wickets':    inn1_wickets,
                'inn1_balls':      inn1_balls,
                'inn2_runs':       inn2_runs,
                'inn2_wickets':    inn2_wickets,
                'inn2_balls':      inn2_balls,
                'run_difference':  inn1_runs - inn2_runs,
                'winner':          winner        # target column
            })

        except Exception as e:
            print(f"Skipping match {match_id}: {e}")
            continue

    features_df = pd.DataFrame(match_features)
    print(f"Built {len(features_df)} match feature rows")
    return features_df


def build_football_features(df):
    print(f"Building football features from {len(df)} matches...")
    df = df.copy()
    df.dropna(subset=['home_goals', 'away_goals'], inplace=True)
    df = df.sort_values('matchday').reset_index(drop=True)

    df['goal_difference']  = df['home_goals'] - df['away_goals']
    df['total_goals']      = df['home_goals'] + df['away_goals']
    df['home_win']         = (df['result'] == 'H').astype(int)

    result_map = {'H': 1, 'D': 0, 'A': 2}
    df['result_encoded']   = df['result'].map(result_map)

    df['home_team_code']   = df['home_team'].astype('category').cat.codes
    df['away_team_code']   = df['away_team'].astype('category').cat.codes

    # Rolling form — last 5 matches avg goals per team
    for team_col, goals_col, form_col in [
        ('home_team', 'home_goals', 'home_recent_goals'),
        ('away_team', 'away_goals', 'away_recent_goals'),
    ]:
        df[form_col] = df.groupby(team_col)[goals_col].transform(
            lambda x: x.shift(1).rolling(5, min_periods=1).mean()
        )

    df.fillna(0, inplace=True)
    print(f"Football features ready: {len(df)} rows")
    return df


def save_features(df, filename):
    os.makedirs(PROCESSED_PATH, exist_ok=True)
    path = os.path.join(PROCESSED_PATH, filename)
    df.to_csv(path, index=False)
    print(f"Saved: {path}")


if __name__ == '__main__':
    # --- Cricket ---
    cricket_raw_path = os.path.join(PROCESSED_PATH, 'cricket_raw.csv')
    if os.path.exists(cricket_raw_path):
        cricket_df = pd.read_csv(cricket_raw_path)
        cricket_features = build_cricket_features(cricket_df)
        save_features(cricket_features, 'cricket_features.csv')
        print(cricket_features.head())
    else:
        print("cricket_raw.csv not found — run data_collector.py first")

    # --- Football ---
    football_raw_path = os.path.join(PROCESSED_PATH, 'football_raw.csv')
    if os.path.exists(football_raw_path):
        football_df = pd.read_csv(football_raw_path)
        football_features = build_football_features(football_df)
        save_features(football_features, 'football_features.csv')
        print(football_features.head())
    else:
        print("football_raw.csv not found — run data_collector.py first")