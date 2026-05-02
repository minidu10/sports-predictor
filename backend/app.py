import logging
from flask import Flask
from flask_cors import CORS
from routes.cricket import cricket_bp
from routes.football import football_bp
from routes.admin import admin_bp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s — %(message)s',
)

app = Flask(__name__)
CORS(app, origins=[
    'http://localhost:5173', 'http://127.0.0.1:5173',
    'http://localhost:5174', 'http://127.0.0.1:5174',
])

app.register_blueprint(cricket_bp,  url_prefix='/api')
app.register_blueprint(football_bp, url_prefix='/api')
app.register_blueprint(admin_bp,    url_prefix='/api')


@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Sports Predictor API is running'}


if __name__ == '__main__':
    from config import DEBUG, PORT

    # Flask debug mode spawns a reloader child process — only start the
    # scheduler in the actual worker process, not the parent watcher.
    import os
    is_worker = not DEBUG or os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    if is_worker:
        from scheduler import start_scheduler
        start_scheduler()

    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')
