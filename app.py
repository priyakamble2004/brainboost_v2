from dotenv import load_dotenv
load_dotenv()
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from database import db
from routes.auth import auth_bp
from routes.sections import sections_bp
from routes.questions import questions_bp
from routes.quiz import quiz_bp
from routes.psychometric import psycho_bp
from routes.leaderboard import leaderboard_bp
import config, os

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config.Config)
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Register blueprints ───────────────────────────────────
    app.register_blueprint(auth_bp,        url_prefix='/api/auth')
    app.register_blueprint(sections_bp,    url_prefix='/api/sections')
    app.register_blueprint(questions_bp,   url_prefix='/api/questions')
    app.register_blueprint(quiz_bp,        url_prefix='/api/quiz')
    app.register_blueprint(psycho_bp,      url_prefix='/api/psychometric')
    app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')

    # ── Serve frontend HTML at root ──────────────────────────
    
    @app.route('/')
    def index():
        return send_from_directory(os.path.dirname(__file__), 'index.html')

    # ── Create tables + auto-seed on first run ───────────────
    with app.app_context():
        db.create_all()
        from seed import seed_all
        seed_all()

    # ── JSON error handlers for /api/* so the frontend never gets HTML back ──
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify(error='Not found', path=request.path), 404
        return e

    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith('/api/'):
            return jsonify(error='Internal server error'), 500
        return e

    return app

# Module-level app object — REQUIRED for gunicorn/production WSGI servers.
# Render's start command (e.g. `gunicorn app:app`) imports this module and
# looks for `app` at import time; without this line it can't find your app
# at all, and every request falls back to Render's own HTML error page.
app = create_app()

if __name__ == '__main__':
    # Only used for local development (python app.py).
    app.run(debug=True, host='0.0.0.0', port=5000)
