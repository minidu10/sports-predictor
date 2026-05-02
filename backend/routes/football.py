from flask import Blueprint, request, jsonify
from src.predictor import predict_football

football_bp = Blueprint('football', __name__)

REQUIRED = ['home_team', 'away_team', 'matchday']

@football_bp.route('/predict/football', methods=['POST'])
def predict_football_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body provided'}), 400

    missing = [f for f in REQUIRED if f not in data]
    if missing:
        return jsonify({'error': f'Missing fields: {missing}'}), 400

    result = predict_football(
        home_team=str(data['home_team']),
        away_team=str(data['away_team']),
        matchday=int(data['matchday']),
    )

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)
