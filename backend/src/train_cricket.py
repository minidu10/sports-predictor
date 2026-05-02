import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

PROCESSED_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
MODELS_PATH = os.path.join(os.path.dirname(__file__), '..', 'models')

def train_cricket_model():
    # Load features
    df = pd.read_csv(os.path.join(PROCESSED_PATH, 'cricket_features.csv'))
    print(f"Training on {len(df)} matches")

    # Encode team names to numbers
    le_team1 = LabelEncoder()
    le_team2 = LabelEncoder()

    all_teams = pd.concat([df['team1'], df['team2']]).unique()
    le_team1.fit(all_teams)
    le_team2.fit(all_teams)

    df['team1_encoded'] = le_team1.transform(df['team1'])
    df['team2_encoded'] = le_team2.transform(df['team2'])

    # Features the model learns from
    # Remove run_difference — it leaks the answer
    feature_cols = [
        'team1_encoded',
        'team2_encoded',
        'inn1_runs',
        'inn1_wickets',
        'inn1_balls',
    ]
    X = df[feature_cols]
    y = df['winner']  # 1 = team1 wins, 0 = team2 wins

    # Split into train and test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train the model
    print("Training RandomForest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save model and encoders
    os.makedirs(MODELS_PATH, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_PATH, 'cricket_model.pkl'))
    joblib.dump(le_team1, os.path.join(MODELS_PATH, 'cricket_team_encoder.pkl'))
    joblib.dump(feature_cols, os.path.join(MODELS_PATH, 'cricket_features.pkl'))
    print(f"\nModel saved to models/cricket_model.pkl")

    return accuracy

if __name__ == '__main__':
    train_cricket_model()