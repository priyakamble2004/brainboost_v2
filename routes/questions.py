from flask import Blueprint, request, jsonify
from models import Question, Level
from database import db
from routes.auth import token_required

questions_bp = Blueprint('questions', __name__)


@questions_bp.route('/level/<int:level_id>', methods=['GET'])
@token_required
def get_questions(current_user, level_id):
    """
    GET /api/questions/level/<level_id>
    Returns 10 randomised questions WITHOUT correct_option.
    Correct answers are only revealed by /api/quiz/submit after all answers are sent.
    """
    Level.query.get_or_404(level_id)
    questions = (
        Question.query
        .filter_by(level_id=level_id)
        .order_by(db.func.rand())
        .limit(10)
        .all()
    )
    if len(questions) < 10:
        return jsonify({'error': 'Not enough questions in this level (need at least 10)'}), 404
    return jsonify({
        'questions': [q.to_dict(include_answer=False) for q in questions],
        'count':     len(questions)
    })


@questions_bp.route('/', methods=['POST'])
@token_required
def add_question(current_user):
    """POST /api/questions/  — add a single question"""
    data     = request.get_json()
    required = ['level_id','question_text','option_a','option_b','option_c','option_d','correct_option']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    Level.query.get_or_404(data['level_id'])
    q = Question(
        level_id       = data['level_id'],
        question_text  = data['question_text'],
        option_a       = data['option_a'],
        option_b       = data['option_b'],
        option_c       = data['option_c'],
        option_d       = data['option_d'],
        correct_option = int(data['correct_option'])
    )
    db.session.add(q)
    db.session.commit()
    return jsonify({'message': 'Question added', 'question': q.to_dict(include_answer=True)}), 201


@questions_bp.route('/bulk', methods=['POST'])
@token_required
def bulk_add(current_user):
    """POST /api/questions/bulk  — add many questions at once"""
    items = request.get_json().get('questions', [])
    if not items:
        return jsonify({'error': 'questions array is empty'}), 400
    for item in items:
        db.session.add(Question(
            level_id       = item['level_id'],
            question_text  = item['question_text'],
            option_a       = item['option_a'],
            option_b       = item['option_b'],
            option_c       = item['option_c'],
            option_d       = item['option_d'],
            correct_option = int(item['correct_option'])
        ))
    db.session.commit()
    return jsonify({'message': f'{len(items)} questions added'}), 201


@questions_bp.route('/<int:qid>', methods=['PUT'])
@token_required
def update_question(current_user, qid):
    """PUT /api/questions/<id>  — update a question"""
    q    = Question.query.get_or_404(qid)
    data = request.get_json()
    for field in ['question_text','option_a','option_b','option_c','option_d','correct_option']:
        if field in data:
            setattr(q, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Question updated', 'question': q.to_dict(include_answer=True)})


@questions_bp.route('/<int:qid>', methods=['DELETE'])
@token_required
def delete_question(current_user, qid):
    """DELETE /api/questions/<id>"""
    q = Question.query.get_or_404(qid)
    db.session.delete(q)
    db.session.commit()
    return jsonify({'message': 'Question deleted'})
