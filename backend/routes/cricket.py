from flask import Blueprint, request, jsonify
from src.predictor import predict_cricket

cricket_bp = Blueprint('cricket', __name__)

REQUIRED = ['team1', 'team2', 'inn1_runs', 'inn1_wickets', 'inn1_balls']

@cricket_bp.route('/predict/cricket', methods=['POST'])
def predict_cricket_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body provided'}), 400

    missing = [f for f in REQUIRED if f not in data]
    if missing:
        return jsonify({'error': f'Missing fields: {missing}'}), 400

    result = predict_cricket(
        team1=str(data['team1']),
        team2=str(data['team2']),
        inn1_runs=int(data['inn1_runs']),
        inn1_wickets=int(data['inn1_wickets']),
        inn1_balls=int(data['inn1_balls']),
    )

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)
