import threading
from flask import Blueprint, jsonify, request
from src.retrain import run_full_retrain, get_retrain_history, get_download_status
from src.predictor import reload_models

admin_bp = Blueprint('admin', __name__)

_retrain_running = False


@admin_bp.route('/admin/retrain', methods=['POST'])
def trigger_retrain():
    global _retrain_running
    if _retrain_running:
        return jsonify({'error': 'Retrain already in progress'}), 409

    force = request.get_json(silent=True, force=True) or {}
    force_download = bool(force.get('force', False))

    def _task():
        global _retrain_running
        _retrain_running = True
        try:
            run_full_retrain(force=force_download)
            reload_models()
        finally:
            _retrain_running = False

    threading.Thread(target=_task, daemon=True).start()
    return jsonify({
        'message': 'Retrain started in background',
        'force':   force_download,
        'status_url': '/api/admin/status',
    })


@admin_bp.route('/admin/status', methods=['GET'])
def retrain_status():
    history = get_retrain_history()
    return jsonify({
        'retrain_running':   _retrain_running,
        'download_status':   get_download_status(),
        'total_runs':        len(history),
        'last_run':          history[-1] if history else None,
        'history':           history,
    })
