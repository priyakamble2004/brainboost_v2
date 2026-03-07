from flask import Blueprint, request, jsonify, current_app
from models import User
from database import db
from functools import wraps
import jwt, datetime

auth_bp = Blueprint('auth', __name__)


# ── Token helpers ─────────────────────────────────────────────
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp':     datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def token_required(f):
    """Decorator: validates Bearer JWT and injects current_user as first arg."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth  = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1]
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data         = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired — please log in again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# ── Routes ────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    """POST /api/auth/register  →  { token, user }"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'username and password required'}), 400
    if len(data['username']) < 2:
        return jsonify({'error': 'Username must be at least 2 characters'}), 400
    if len(data['password']) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 409

    user = User(username=data['username'], email=data.get('email') or None)
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Registered successfully',
        'token':   generate_token(user.id),
        'user':    user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /api/auth/login  →  { token, user }"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'Invalid username or password'}), 401
    return jsonify({
        'message': f'Welcome back, {user.username}!',
        'token':   generate_token(user.id),
        'user':    user.to_dict()
    })


@auth_bp.route('/me', methods=['GET'])
@token_required
def me(current_user):
    """GET /api/auth/me  →  { user }"""
    return jsonify({'user': current_user.to_dict()})


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """POST /api/auth/logout  (client discards the token)"""
    return jsonify({'message': 'Logged out successfully'})
