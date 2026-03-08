from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory
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
        html = os.path.join(os.path.dirname(__file__), 'brain-boost-v2-connected.html')
        if os.path.exists(html):
            return send_from_directory(os.path.dirname(__file__), 'index.html')
        return '<h2 style="font-family:sans-serif;padding:40px">Place brain-boost-v2-connected.html in the brainboost_v2/ folder, then refresh.</h2>', 404

    # ── Create tables + auto-seed on first run ───────────────
    with app.app_context():
        db.create_all()
        from seed import seed_all
        seed_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
