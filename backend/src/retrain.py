import os
import json
import zipfile
import logging
import requests
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

RAW_PATH       = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROCESSED_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
LOG_PATH       = os.path.join(os.path.dirname(__file__), '..', 'data', 'retrain_log.json')
STATUS_PATH    = os.path.join(os.path.dirname(__file__), '..', 'data', 'download_status.json')

CRICSHEET_URL  = 'https://cricsheet.org/downloads/odis_csv2.zip'
RETRAIN_INTERVAL_DAYS = 30


# ── Download status tracker ──────────────────────────────────────────────────

def _read_status():
    try:
        if os.path.exists(STATUS_PATH):
            with open(STATUS_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _write_status(status):
    try:
        os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
        with open(STATUS_PATH, 'w') as f:
            json.dump(status, f, indent=2)
    except Exception as e:
        log.error(f"Could not write download status: {e}")


def _days_since(iso_date_str):
    """Return how many days since the given ISO date string. None if never."""
    if not iso_date_str:
        return None
    try:
        last = datetime.fromisoformat(iso_date_str)
        now  = datetime.now()
        return (now - last).days
    except Exception:
        return None


def get_download_status():
    """Return human-readable status of last downloads."""
    status = _read_status()
    result = {}
    for sport in ('cricket', 'football'):
        info = status.get(sport, {})
        last = info.get('last_download')
        days = _days_since(last)
        result[sport] = {
            'last_download':    last or 'Never',
            'days_ago':         days,
            'next_update_in':   max(0, RETRAIN_INTERVAL_DAYS - days) if days is not None else 0,
            **{k: v for k, v in info.items() if k != 'last_download'},
        }
    return result


# ── Data fetchers ────────────────────────────────────────────────────────────

def fetch_cricket_data(force=False):
    """
    Download Cricsheet ODI zip and extract only NEW match files.
    Skips entirely if last download was less than RETRAIN_INTERVAL_DAYS ago.
    """
    status = _read_status()
    cricket_status = status.get('cricket', {})
    days = _days_since(cricket_status.get('last_download'))

    if not force and days is not None and days < RETRAIN_INTERVAL_DAYS:
        log.info(
            f"Cricket data is {days} days old — skipping download "
            f"(updates every {RETRAIN_INTERVAL_DAYS} days)"
        )
        return 0

    log.info("Downloading latest Cricsheet ODI data...")
    try:
        os.makedirs(RAW_PATH, exist_ok=True)

        # Get existing match IDs so we only extract new ones
        existing = {f for f in os.listdir(RAW_PATH) if f.endswith('.csv')}

        resp = requests.get(CRICSHEET_URL, timeout=180, stream=True)
        resp.raise_for_status()

        zip_path = os.path.join(RAW_PATH, '_cricsheet.zip')
        with open(zip_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)

        new_files = []
        with zipfile.ZipFile(zip_path, 'r') as z:
            all_csvs = [n for n in z.namelist() if n.endswith('.csv')]
            # Extract only files not already on disk
            new_files = [n for n in all_csvs if os.path.basename(n) not in existing]
            if new_files:
                z.extractall(RAW_PATH, members=new_files)
            else:
                log.info("No new cricket match files found in latest zip")

        os.remove(zip_path)

        total_on_disk = len([f for f in os.listdir(RAW_PATH) if f.endswith('.csv')])
        log.info(
            f"Cricket: {len(new_files)} new files added "
            f"({total_on_disk} total on disk)"
        )

        status['cricket'] = {
            'last_download':   datetime.now().isoformat(),
            'total_files':     total_on_disk,
            'new_files_added': len(new_files),
        }
        _write_status(status)
        return len(new_files)

    except Exception as e:
        log.error(f"Cricket fetch failed: {e}")
        return 0


def fetch_football_data(force=False):
    """
    Fetch current PL season from football-data.org and append only NEW matches.
    Skips entirely if last download was less than RETRAIN_INTERVAL_DAYS ago.
    """
    status = _read_status()
    football_status = status.get('football', {})
    days = _days_since(football_status.get('last_download'))

    if not force and days is not None and days < RETRAIN_INTERVAL_DAYS:
        log.info(
            f"Football data is {days} days old — skipping download "
            f"(updates every {RETRAIN_INTERVAL_DAYS} days)"
        )
        return 0

    api_key = os.getenv('FOOTBALL_API_KEY')
    if not api_key:
        log.warning("FOOTBALL_API_KEY not set — skipping football fetch")
        return 0

    now    = datetime.now()
    season = now.year - 1 if now.month < 8 else now.year

    log.info(f"Fetching PL season {season} from football-data.org...")
    try:
        resp = requests.get(
            'https://api.football-data.org/v4/competitions/PL/matches',
            headers={'X-Auth-Token': api_key},
            params={'season': str(season), 'status': 'FINISHED'},
            timeout=30,
        )
        resp.raise_for_status()
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
                'matchday':   m['matchday'],
                'result':     'H' if home > away else 'A' if away > home else 'D',
            })

        new_df = pd.DataFrame(rows)
        raw_path = os.path.join(PROCESSED_PATH, 'football_raw.csv')

        # Append new matchdays to existing data instead of replacing
        if os.path.exists(raw_path):
            existing_df  = pd.read_csv(raw_path)
            existing_days = set(existing_df['matchday'].unique())
            new_days      = set(new_df['matchday'].unique())
            added_days    = new_days - existing_days
            new_rows      = new_df[new_df['matchday'].isin(added_days)]

            if not new_rows.empty:
                combined = pd.concat([existing_df, new_rows], ignore_index=True)
                combined.to_csv(raw_path, index=False)
                new_match_count = len(new_rows)
                log.info(
                    f"Football: {new_match_count} new matches added "
                    f"({len(combined)} total)"
                )
            else:
                log.info("Football: no new matches found since last download")
                new_match_count = 0
        else:
            os.makedirs(PROCESSED_PATH, exist_ok=True)
            new_df.to_csv(raw_path, index=False)
            new_match_count = len(new_df)
            log.info(f"Football: {new_match_count} matches saved (first download)")

        total = len(pd.read_csv(raw_path))
        status['football'] = {
            'last_download':    datetime.now().isoformat(),
            'season':           season,
            'total_matches':    total,
            'new_matches_added': new_match_count,
        }
        _write_status(status)
        return new_match_count

    except Exception as e:
        log.error(f"Football fetch failed: {e}")
        return 0


# ── Main pipeline ────────────────────────────────────────────────────────────

def run_full_retrain(force=False):
    """
    Smart retrain pipeline:
    - Skips data download if last download < 30 days ago (unless force=True)
    - Only downloads NEW matches/files
    - Retrains models with all accumulated data
    - Logs results with timestamps
    """
    from src.data_collector import _parse_cricsheet_file
    from src.feature_engineer import build_cricket_features, build_football_features, save_features
    from src.train_cricket import train_cricket_model
    from src.train_football import train_football_model

    started = datetime.now().isoformat()
    log.info(f"=== Retrain pipeline started {started} (force={force}) ===")
    results = {'started_at': started, 'cricket': {}, 'football': {}}

    # ── Cricket ──────────────────────────────────────────────────────────────
    try:
        new_files = fetch_cricket_data(force=force)
        results['cricket']['new_files'] = new_files

        all_files = [f for f in os.listdir(RAW_PATH) if f.endswith('.csv')]
        dfs = []
        for fname in all_files:
            df = _parse_cricsheet_file(os.path.join(RAW_PATH, fname))
            if df is not None:
                dfs.append(df)

        if not dfs:
            raise ValueError("No valid cricket CSV files found in data/raw/")

        raw = pd.concat(dfs, ignore_index=True)
        raw.to_csv(os.path.join(PROCESSED_PATH, 'cricket_raw.csv'), index=False)

        features = build_cricket_features(raw)
        save_features(features, 'cricket_features.csv')

        accuracy = train_cricket_model()
        results['cricket']['total_matches'] = len(features)
        results['cricket']['accuracy']      = round(accuracy * 100, 2)
        log.info(f"Cricket done — {len(features)} matches, {accuracy:.2%} accuracy")
    except Exception as e:
        log.error(f"Cricket pipeline error: {e}")
        results['cricket']['error'] = str(e)

    # ── Football ─────────────────────────────────────────────────────────────
    try:
        new_matches = fetch_football_data(force=force)
        results['football']['new_matches'] = new_matches

        raw_path = os.path.join(PROCESSED_PATH, 'football_raw.csv')
        raw      = pd.read_csv(raw_path)

        features = build_football_features(raw)
        save_features(features, 'football_features.csv')

        accuracy = train_football_model()
        results['football']['total_matches'] = len(features)
        results['football']['accuracy']      = round(accuracy * 100, 2)
        log.info(f"Football done — {len(features)} matches, {accuracy:.2%} accuracy")
    except Exception as e:
        log.error(f"Football pipeline error: {e}")
        results['football']['error'] = str(e)

    results['completed_at'] = datetime.now().isoformat()
    _append_log(results)
    log.info("=== Retrain pipeline completed ===")
    return results


# ── Log helpers ──────────────────────────────────────────────────────────────

def _append_log(result):
    try:
        history = []
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH) as f:
                history = json.load(f)
        history.append(result)
        history = history[-24:]
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        log.error(f"Failed to write retrain log: {e}")


def get_retrain_history():
    try:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return []


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    run_full_retrain()
