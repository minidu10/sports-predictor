import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROCESSED_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')

CRICSHEET_BALL_COLUMNS = [
    'record_type', 'innings', 'over_ball', 'batting_team',
    'striker', 'non_striker', 'bowler', 'runs_off_bat', 'extras',
    'wides', 'noballs', 'byes', 'legbyes', 'penalty',
    'wicket_type', 'player_out'
]

def _parse_cricsheet_file(path):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('ball,'):
                parts = line.rstrip('\n').split(',')
                padded = parts + [''] * (len(CRICSHEET_BALL_COLUMNS) - len(parts))
                rows.append(padded[:len(CRICSHEET_BALL_COLUMNS)])
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=CRICSHEET_BALL_COLUMNS)
    df['match_id'] = os.path.splitext(os.path.basename(path))[0]
    return df

def load_cricket_data():
    all_files = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith('.csv')]

    if not all_files:
        print("No CSV files found in data/raw/ folder")
        return None

    dfs = []
    for file in all_files:
        path = os.path.join(RAW_DATA_PATH, file)
        try:
            df = _parse_cricsheet_file(path)
            if df is not None:
                dfs.append(df)
        except Exception as e:
            print(f"Skipping {file}: {e}")

    if not dfs:
        print("No valid CSV files could be loaded")
        return None

    combined = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(combined)} ball rows from {len(dfs)} files")
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    combined.to_csv(os.path.join(PROCESSED_DATA_PATH, 'cricket_raw.csv'), index=False)
    print(f"Saved cricket_raw.csv with {len(combined)} rows")
    return combined

def save_processed_cricket(df):
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    out = os.path.join(PROCESSED_DATA_PATH, 'cricket_processed.csv')
    df.to_csv(out, index=False)
    print(f"Saved processed data to {out}")

def fetch_football_data():
    api_key = os.getenv('FOOTBALL_API_KEY')

    if not api_key:
        print("No API key found in .env file")
        return None

    url = 'https://api.football-data.org/v4/competitions/PL/matches'
    headers = {'X-Auth-Token': api_key}
    params = {'season': '2023', 'status': 'FINISHED'}

    print("Fetching Premier League matches...")
    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        print(f"API error: {resp.status_code} - {resp.text}")
        return None

    matches = resp.json().get('matches', [])
    rows = []

    for m in matches:
        home = m['score']['fullTime']['home']
        away = m['score']['fullTime']['away']
        if home is None or away is None:
            continue
        rows.append({
            'home_team': m['homeTeam']['name'],
            'away_team': m['awayTeam']['name'],
            'home_goals': home,
            'away_goals': away,
            'matchday': m['matchday'],
            'result': 'H' if home > away else 'A' if away > home else 'D'
        })

    df = pd.DataFrame(rows)
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    df.to_csv(os.path.join(PROCESSED_DATA_PATH, 'football_raw.csv'), index=False)
    print(f"Saved {len(df)} football matches")
    return df

if __name__ == '__main__':
    df = load_cricket_data()
    if df is not None:
        print(df.head())
        print(f"Columns: {list(df.columns)}")

    fetch_football_data()
