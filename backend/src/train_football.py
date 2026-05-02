import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

PROCESSED_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
MODELS_PATH = os.path.join(os.path.dirname(__file__), '..', 'models')

def train_football_model():
    # Load features
    df = pd.read_csv(os.path.join(PROCESSED_PATH, 'football_features.csv'))
    print(f"Training on {len(df)} matches")

    # Features the model learns from
    feature_cols = [
        'home_team_code',
        'away_team_code',
        'matchday',
        'home_recent_goals',
        'away_recent_goals',
    ]

    X = df[feature_cols]
    y = df['result_encoded']  # 1=Home win, 0=Draw, 2=Away win

    # Split into train and test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train the model
    print("Training RandomForest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred,
          target_names=['Draw', 'Home Win', 'Away Win']))

    # Save model and team name mapping
    os.makedirs(MODELS_PATH, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_PATH, 'football_model.pkl'))
    joblib.dump(feature_cols, os.path.join(MODELS_PATH, 'football_features.pkl'))

    # Save team name to code mapping for API use later
    team_mapping = dict(zip(df['home_team'], df['home_team_code']))
    team_mapping.update(dict(zip(df['away_team'], df['away_team_code'])))
    joblib.dump(team_mapping, os.path.join(MODELS_PATH, 'football_team_mapping.pkl'))
    print(f"\nModel saved to models/football_model.pkl")

    return accuracy

if __name__ == '__main__':
    train_football_model()