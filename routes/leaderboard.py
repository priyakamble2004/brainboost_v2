from flask import Blueprint, jsonify
from models import QuizAttempt, User, Level, Section, LevelProgress
from database import db
from sqlalchemy import func

leaderboard_bp = Blueprint('leaderboard', __name__)


@leaderboard_bp.route('/global', methods=['GET'])
def global_leaderboard():
    """
    GET /api/leaderboard/global
    Top 20 players ranked by total score across all sections and levels.
    """
    results = (
        db.session.query(
            User.id,
            User.username,
            func.sum(QuizAttempt.score).label('total_score'),
            func.sum(QuizAttempt.stars).label('total_stars'),
            func.count(QuizAttempt.id).label('games_played'),
            func.sum(db.cast(QuizAttempt.is_perfect, db.Integer)).label('perfect_count')
        )
        .join(QuizAttempt, User.id == QuizAttempt.user_id)
        .group_by(User.id, User.username)
        .order_by(func.sum(QuizAttempt.score).desc())
        .limit(20)
        .all()
    )
    return jsonify({'leaderboard': [
        {
            'rank':          i + 1,
            'user_id':       r.id,
            'username':      r.username,
            'total_score':   int(r.total_score),
            'total_stars':   int(r.total_stars),
            'games_played':  int(r.games_played),
            'perfect_count': int(r.perfect_count or 0)
        }
        for i, r in enumerate(results)
    ]})


@leaderboard_bp.route('/section/<int:section_id>', methods=['GET'])
def section_leaderboard(section_id):
    """
    GET /api/leaderboard/section/<id>
    Top 20 players for a specific section, ranked by best combined score.
    """
    Section.query.get_or_404(section_id)
    level_ids = [lv.id for lv in Level.query.filter_by(section_id=section_id).all()]
    if not level_ids:
        return jsonify({'leaderboard': []})

    results = (
        db.session.query(
            User.id,
            User.username,
            func.sum(LevelProgress.best_score).label('section_score'),
            func.sum(LevelProgress.best_stars).label('section_stars'),
            func.sum(db.cast(LevelProgress.is_perfect, db.Integer)).label('perfects')
        )
        .join(LevelProgress, User.id == LevelProgress.user_id)
        .filter(LevelProgress.level_id.in_(level_ids))
        .group_by(User.id, User.username)
        .order_by(func.sum(LevelProgress.best_score).desc())
        .limit(20)
        .all()
    )
    return jsonify({'leaderboard': [
        {
            'rank':          i + 1,
            'user_id':       r.id,
            'username':      r.username,
            'section_score': int(r.section_score),
            'section_stars': int(r.section_stars),
            'perfects':      int(r.perfects or 0)
        }
        for i, r in enumerate(results)
    ]})
