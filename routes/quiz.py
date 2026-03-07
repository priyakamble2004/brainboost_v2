from flask import Blueprint, request, jsonify
from models import QuizAttempt, AttemptAnswer, Question, Level, LevelProgress, Section
from database import db
from routes.auth import token_required
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)


def calc_stars(score):
    """Convert 0-10 score into 1-5 stars."""
    if score == 10: return 5
    if score >= 8:  return 4
    if score >= 6:  return 3
    if score >= 4:  return 2
    return 1


def result_message(score, is_perfect):
    if is_perfect:  return '🏆 PERFECT! Level unlocked — you are a true Brain Boost Champion!'
    if score >= 8:  return '🌟 So close! Just 10/10 unlocks the next level. Try again!'
    if score >= 5:  return '👍 Good effort! Study more and aim for a perfect 10/10!'
    return '📚 Keep practising! Review the topics and try again for 10/10!'


# ── Submit quiz ───────────────────────────────────────────────
@quiz_bp.route('/submit', methods=['POST'])
@token_required
def submit_quiz(current_user):
    """
    POST /api/quiz/submit
    Body: {
        level_id: int,
        time_taken: int,          (seconds for entire quiz)
        answers: [
            { question_id: int, selected_option: int|null, time_taken: int }
        ]
    }
    Returns: {
        attempt_id, score, stars, is_perfect,
        next_level_unlocked, message,
        correct_map: { "<question_id>": { is_correct, correct_option } }
    }
    """
    data       = request.get_json()
    level_id   = data.get('level_id')
    answers    = data.get('answers', [])
    time_taken = data.get('time_taken', 0)

    if not level_id:
        return jsonify({'error': 'level_id is required'}), 400
    if len(answers) != 10:
        return jsonify({'error': f'Expected 10 answers, got {len(answers)}'}), 400

    level   = Level.query.get_or_404(level_id)

    # ── Server-side answer validation ────────────────────────
    score          = 0
    answer_records = []
    correct_map    = {}

    for ans in answers:
        q = Question.query.get(ans.get('question_id'))
        if not q:
            return jsonify({'error': f"Question {ans.get('question_id')} not found"}), 404

        selected   = ans.get('selected_option')
        is_correct = (selected is not None) and (int(selected) == q.correct_option)
        if is_correct:
            score += 1

        correct_map[str(q.id)] = {
            'is_correct':     is_correct,
            'correct_option': q.correct_option
        }
        answer_records.append({
            'question_id':     q.id,
            'selected_option': selected,
            'is_correct':      is_correct,
            'time_taken':      ans.get('time_taken', 0)
        })

    is_perfect = (score == 10)
    stars      = calc_stars(score)

    # ── Persist attempt ───────────────────────────────────────
    attempt = QuizAttempt(
        user_id    = current_user.id,
        level_id   = level_id,
        score      = score,
        stars      = stars,
        is_perfect = is_perfect,
        time_taken = time_taken
    )
    db.session.add(attempt)
    db.session.flush()   # get attempt.id before committing

    for ar in answer_records:
        db.session.add(AttemptAnswer(
            attempt_id      = attempt.id,
            question_id     = ar['question_id'],
            selected_option = ar['selected_option'],
            is_correct      = ar['is_correct'],
            time_taken      = ar['time_taken']
        ))

    # ── Update level progress (best score only goes up) ───────
    prog = LevelProgress.query.filter_by(
        user_id=current_user.id, level_id=level_id
    ).first()

    if not prog:
        prog = LevelProgress(
            user_id    = current_user.id,
            level_id   = level_id,
            best_score = score,
            best_stars = stars,
            is_perfect = is_perfect,
            attempts   = 1
        )
        db.session.add(prog)
    else:
        prog.attempts += 1
        if score > prog.best_score: prog.best_score = score
        if stars > prog.best_stars: prog.best_stars = stars
        if is_perfect:              prog.is_perfect = True   # never goes back to False
        prog.updated_at = datetime.utcnow()

    db.session.commit()

    # ── Did this score unlock the next level? ─────────────────
    next_level_unlocked = False
    if is_perfect and level.level_number < 5:
        next_lv = Level.query.filter_by(
            section_id   = level.section_id,
            level_number = level.level_number + 1
        ).first()
        next_level_unlocked = (next_lv is not None)

    return jsonify({
        'attempt_id':          attempt.id,
        'score':               score,
        'stars':               stars,
        'is_perfect':          is_perfect,
        'next_level_unlocked': next_level_unlocked,
        'message':             result_message(score, is_perfect),
        'correct_map':         correct_map,
        'time_taken':          time_taken
    })


# ── Progress ──────────────────────────────────────────────────
@quiz_bp.route('/progress', methods=['GET'])
@token_required
def get_progress(current_user):
    """GET /api/quiz/progress  →  all level progress rows for current user"""
    progress = LevelProgress.query.filter_by(user_id=current_user.id).all()
    return jsonify({'progress': [p.to_dict() for p in progress]})


@quiz_bp.route('/progress/section/<int:section_id>', methods=['GET'])
@token_required
def section_progress(current_user, section_id):
    """GET /api/quiz/progress/section/<id>  →  progress + unlock status per level"""
    levels    = Level.query.filter_by(section_id=section_id).all()
    level_ids = [lv.id for lv in levels]
    rows      = LevelProgress.query.filter(
        LevelProgress.user_id  == current_user.id,
        LevelProgress.level_id.in_(level_ids)
    ).all()
    prog_map  = {r.level_id: r.to_dict() for r in rows}

    result = []
    for lv in sorted(levels, key=lambda x: x.level_number):
        p = prog_map.get(lv.id, {
            'level_id': lv.id, 'best_score': 0,
            'best_stars': 0, 'is_perfect': False, 'attempts': 0
        })
        if lv.level_number == 1:
            p['unlocked'] = True
        else:
            prev  = next((x for x in levels if x.level_number == lv.level_number - 1), None)
            prevp = prog_map.get(prev.id, {}) if prev else {}
            p['unlocked'] = prevp.get('is_perfect', False)
        result.append(p)

    return jsonify({'progress': result})


@quiz_bp.route('/history/level/<int:level_id>', methods=['GET'])
@token_required
def level_history(current_user, level_id):
    """GET /api/quiz/history/level/<id>  →  last 10 attempts for a level"""
    attempts = (
        QuizAttempt.query
        .filter_by(user_id=current_user.id, level_id=level_id)
        .order_by(QuizAttempt.completed_at.desc())
        .limit(10).all()
    )
    return jsonify({'attempts': [a.to_dict() for a in attempts]})
