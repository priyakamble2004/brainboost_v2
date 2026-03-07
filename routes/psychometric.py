from flask import Blueprint, request, jsonify
from models import PsychometricResult
from database import db
from routes.auth import token_required

psycho_bp = Blueprint('psychometric', __name__)

CAREER_PROFILES = {
    'analytical': {
        'badge':       '🔬',
        'title':       'THE ANALYTICAL MIND',
        'type':        'Logical · Systematic · Data-Driven',
        'desc':        ('You have a sharp, logical mind that thrives on data, patterns, and problem-solving. '
                        'You are naturally drawn to understanding how complex systems work, and you have the '
                        'patience to work through problems methodically. You excel in environments that demand '
                        'precision and structured thinking.'),
        'paths':       ['Software Engineer','Data Scientist','AI/ML Engineer','Financial Analyst',
                        'Civil/Mechanical Engineer','Cybersecurity Expert','Research Scientist',
                        'Mathematician','Economist','Chartered Accountant'],
        'strengths':   ['Critical Thinking','Problem Solving','Attention to Detail',
                        'Pattern Recognition','Technical Proficiency'],
        'recommended': ['Computer','IKS','Sociopolitical']
    },
    'creative': {
        'badge':       '🎨',
        'title':       'THE CREATIVE VISIONARY',
        'type':        'Imaginative · Expressive · Innovative',
        'desc':        ('You see the world through a lens of beauty, meaning, and possibility. Your imagination '
                        'is your greatest asset — you are constantly generating new ideas, finding unique angles, '
                        'and expressing complex emotions in original ways. You thrive when given freedom to create.'),
        'paths':       ['Graphic Designer','UX/UI Designer','Filmmaker','Journalist & Writer',
                        'Architect','Fashion Designer','Game Developer','Content Creator',
                        'Advertising Professional','Literary Author'],
        'strengths':   ['Creativity & Innovation','Visual Thinking','Storytelling',
                        'Emotional Intelligence','Aesthetic Sense'],
        'recommended': ['English','Indian Culture','IKS']
    },
    'social': {
        'badge':       '🌍',
        'title':       'THE SOCIAL CHANGEMAKER',
        'type':        'Empathetic · Communicative · Leadership',
        'desc':        ('You are powered by a deep sense of purpose — you want to make a meaningful difference '
                        "in people's lives and society. Your empathy, communication skills, and natural leadership "
                        'make you incredibly effective in roles that require collaboration and human connection.'),
        'paths':       ['Doctor / Healthcare Professional','Lawyer & Legal Expert','Teacher & Educator',
                        'Social Worker & NGO Leader','Politician & Policy Maker','Psychologist & Counsellor',
                        'HR & Organizational Developer','Diplomat & Civil Servant',
                        'Journalist & Activist','Public Health Specialist'],
        'strengths':   ['Empathy','Leadership','Communication','Conflict Resolution','Motivating Others'],
        'recommended': ['Sociopolitical','Environment','English']
    },
    'physical': {
        'badge':       '⚡',
        'title':       'THE ACTION-ORIENTED ACHIEVER',
        'type':        'Resilient · Competitive · Courageous',
        'desc':        ('You are driven by action, challenge, and achievement. You possess extraordinary '
                        'determination and a competitive spirit that pushes you beyond ordinary limits. '
                        'You thrive in high-pressure, dynamic environments where you can test yourself.'),
        'paths':       ['Professional Athlete','Military & Defence Officer','Sports Coach & Trainer',
                        'Environmental Scientist','Wildlife Conservationist','Adventure Tourism Professional',
                        'Physiotherapist','Police & Law Enforcement','Pilot & Aviation Professional',
                        'Physical Education Teacher'],
        'strengths':   ['Physical Endurance','Competitive Drive','Quick Decision Making',
                        'Courage & Resilience','Team Leadership'],
        'recommended': ['Sports','Environment','Indian Culture']
    }
}


@psycho_bp.route('/submit', methods=['POST'])
@token_required
def submit_psychometric(current_user):
    """
    POST /api/psychometric/submit
    Body: { analytical: int, creative: int, social: int, physical: int }
    Returns: { result_id, dominant, scores, profile, taken_at }
    """
    data   = request.get_json()
    scores = {
        'analytical': int(data.get('analytical', 0)),
        'creative':   int(data.get('creative',   0)),
        'social':     int(data.get('social',     0)),
        'physical':   int(data.get('physical',   0)),
    }
    dominant = max(scores, key=scores.get)
    profile  = CAREER_PROFILES[dominant]

    result = PsychometricResult(
        user_id          = current_user.id,
        dominant_trait   = dominant,
        analytical_score = scores['analytical'],
        creative_score   = scores['creative'],
        social_score     = scores['social'],
        physical_score   = scores['physical'],
        career_title     = profile['title']
    )
    db.session.add(result)
    db.session.commit()

    return jsonify({
        'result_id': result.id,
        'dominant':  dominant,
        'scores':    scores,
        'profile':   profile,
        'taken_at':  result.taken_at.isoformat()
    })


@psycho_bp.route('/history', methods=['GET'])
@token_required
def get_history(current_user):
    """GET /api/psychometric/history  →  last 5 results"""
    results = (
        PsychometricResult.query
        .filter_by(user_id=current_user.id)
        .order_by(PsychometricResult.taken_at.desc())
        .limit(5).all()
    )
    return jsonify({'results': [r.to_dict() for r in results]})


@psycho_bp.route('/latest', methods=['GET'])
@token_required
def get_latest(current_user):
    """GET /api/psychometric/latest  →  most recent result + profile"""
    r = (
        PsychometricResult.query
        .filter_by(user_id=current_user.id)
        .order_by(PsychometricResult.taken_at.desc())
        .first()
    )
    if not r:
        return jsonify({'result': None, 'profile': None})
    return jsonify({
        'result':  r.to_dict(),
        'profile': CAREER_PROFILES.get(r.dominant_trait, {})
    })
