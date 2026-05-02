import os
import joblib
import numpy as np

MODELS_PATH = os.path.join(os.path.dirname(__file__), '..', 'models')

try:
    _cricket_model   = joblib.load(os.path.join(MODELS_PATH, 'cricket_model.pkl'))
    _cricket_encoder = joblib.load(os.path.join(MODELS_PATH, 'cricket_team_encoder.pkl'))
    _cricket_feats   = joblib.load(os.path.join(MODELS_PATH, 'cricket_features.pkl'))
    print("[predictor] Cricket model loaded")
except Exception as e:
    _cricket_model = _cricket_encoder = _cricket_feats = None
    print(f"[predictor] Cricket model load failed: {e}")

try:
    _football_model    = joblib.load(os.path.join(MODELS_PATH, 'football_model.pkl'))
    _football_feats    = joblib.load(os.path.join(MODELS_PATH, 'football_features.pkl'))
    _football_team_map = joblib.load(os.path.join(MODELS_PATH, 'football_team_mapping.pkl'))
    print("[predictor] Football model loaded")
except Exception as e:
    _football_model = _football_feats = _football_team_map = None
    print(f"[predictor] Football model load failed: {e}")


def reload_models():
    """Hot-reload all models from disk after retraining — no restart needed."""
    global _cricket_model, _cricket_encoder, _cricket_feats
    global _football_model, _football_feats, _football_team_map
    try:
        _cricket_model   = joblib.load(os.path.join(MODELS_PATH, 'cricket_model.pkl'))
        _cricket_encoder = joblib.load(os.path.join(MODELS_PATH, 'cricket_team_encoder.pkl'))
        _cricket_feats   = joblib.load(os.path.join(MODELS_PATH, 'cricket_features.pkl'))
        print("[predictor] Cricket model reloaded")
    except Exception as e:
        print(f"[predictor] Cricket reload failed: {e}")
    try:
        _football_model    = joblib.load(os.path.join(MODELS_PATH, 'football_model.pkl'))
        _football_feats    = joblib.load(os.path.join(MODELS_PATH, 'football_features.pkl'))
        _football_team_map = joblib.load(os.path.join(MODELS_PATH, 'football_team_mapping.pkl'))
        print("[predictor] Football model reloaded")
    except Exception as e:
        print(f"[predictor] Football reload failed: {e}")


def predict_cricket(team1, team2, inn1_runs, inn1_wickets, inn1_balls):
    if _cricket_model is None:
        return {'error': 'Cricket model is not loaded'}

    known = list(_cricket_encoder.classes_)
    if team1 not in known:
        return {'error': f"Unknown team '{team1}'", 'known_teams': known}
    if team2 not in known:
        return {'error': f"Unknown team '{team2}'", 'known_teams': known}

    try:
        t1_enc = int(_cricket_encoder.transform([team1])[0])
        t2_enc = int(_cricket_encoder.transform([team2])[0])

        X = np.array([[t1_enc, t2_enc, inn1_runs, inn1_wickets, inn1_balls]])
        pred  = int(_cricket_model.predict(X)[0])
        proba = _cricket_model.predict_proba(X)[0]

        # 1 = team1 wins, 0 = team2 wins
        classes  = list(_cricket_model.classes_)
        winner   = team1 if pred == 1 else team2
        win_prob = float(proba[classes.index(pred)]) * 100

        return {
            'winner':          winner,
            'win_probability': round(win_prob, 1),
            'team1':           team1,
            'team2':           team2,
        }
    except Exception as e:
        return {'error': str(e)}


def predict_football(home_team, away_team, matchday,
                     home_recent_goals=0.0, away_recent_goals=0.0):
    if _football_model is None:
        return {'error': 'Football model is not loaded'}

    if home_team not in _football_team_map:
        return {'error': f"Unknown team '{home_team}'",
                'known_teams': sorted(_football_team_map.keys())}
    if away_team not in _football_team_map:
        return {'error': f"Unknown team '{away_team}'",
                'known_teams': sorted(_football_team_map.keys())}

    try:
        home_code = _football_team_map[home_team]
        away_code = _football_team_map[away_team]

        X = np.array([[home_code, away_code, matchday,
                       home_recent_goals, away_recent_goals]])
        pred  = int(_football_model.predict(X)[0])
        proba = _football_model.predict_proba(X)[0]

        # classes_ order may not be [0,1,2] — index safely
        classes = list(_football_model.classes_)
        def p(cls):
            return round(float(proba[classes.index(cls)]) * 100, 1) if cls in classes else 0.0

        result_label = {1: 'Home Win', 0: 'Draw', 2: 'Away Win'}

        return {
            'result':        result_label[pred],
            'home_win_prob': p(1),
            'draw_prob':     p(0),
            'away_win_prob': p(2),
            'home_team':     home_team,
            'away_team':     away_team,
        }
    except Exception as e:
        return {'error': str(e)}
