from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ─────────────────────────────────────────────────
#  USER
# ─────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username   = db.Column(db.String(50),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=True)
    password   = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attempts        = db.relationship('QuizAttempt',       backref='user', lazy=True)
    progress        = db.relationship('LevelProgress',     backref='user', lazy=True)
    psycho_results  = db.relationship('PsychometricResult',backref='user', lazy=True)

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)

    def to_dict(self):
        return {
            'id': self.id, 'username': self.username,
            'email': self.email, 'created_at': self.created_at.isoformat()
        }


# ─────────────────────────────────────────────────
#  SECTION
# ─────────────────────────────────────────────────
class Section(db.Model):
    __tablename__ = 'sections'
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name        = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    icon        = db.Column(db.String(10))
    image_path  = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    levels = db.relationship('Level', backref='section', lazy=True,
                             cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'description': self.description,
            'icon':        self.icon,
            'image_url':   f'/api/sections/{self.id}/image' if self.image_path else None,
            'levels':      [lv.to_dict() for lv in sorted(self.levels, key=lambda x: x.level_number)]
        }


# ─────────────────────────────────────────────────
#  LEVEL
# ─────────────────────────────────────────────────
class Level(db.Model):
    __tablename__ = 'levels'
    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_id   = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    level_number = db.Column(db.Integer, nullable=False)
    name         = db.Column(db.String(50))

    questions = db.relationship('Question', backref='level', lazy=True,
                                cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('section_id', 'level_number', name='uq_section_level'),
    )

    def to_dict(self):
        return {
            'id':             self.id,
            'section_id':     self.section_id,
            'level_number':   self.level_number,
            'name':           self.name,
            'question_count': len(self.questions)
        }


# ─────────────────────────────────────────────────
#  QUESTION
# ─────────────────────────────────────────────────
class Question(db.Model):
    __tablename__ = 'questions'
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_id       = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    question_text  = db.Column(db.Text, nullable=False)
    option_a       = db.Column(db.String(255), nullable=False)
    option_b       = db.Column(db.String(255), nullable=False)
    option_c       = db.Column(db.String(255), nullable=False)
    option_d       = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)   # 0=A, 1=B, 2=C, 3=D
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, include_answer=False):
        d = {
            'id':            self.id,
            'level_id':      self.level_id,
            'question_text': self.question_text,
            'options':       [self.option_a, self.option_b, self.option_c, self.option_d]
        }
        if include_answer:
            d['correct_option'] = self.correct_option
        return d


# ─────────────────────────────────────────────────
#  QUIZ ATTEMPT
# ─────────────────────────────────────────────────
class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    level_id     = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    score        = db.Column(db.Integer, nullable=False)    # 0–10
    stars        = db.Column(db.Integer, nullable=False)    # 1–5
    is_perfect   = db.Column(db.Boolean, default=False)     # True when score == 10
    time_taken   = db.Column(db.Integer)                    # seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('AttemptAnswer', backref='attempt', lazy=True,
                              cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':           self.id,
            'user_id':      self.user_id,
            'level_id':     self.level_id,
            'score':        self.score,
            'stars':        self.stars,
            'is_perfect':   self.is_perfect,
            'time_taken':   self.time_taken,
            'completed_at': self.completed_at.isoformat()
        }


# ─────────────────────────────────────────────────
#  ATTEMPT ANSWER  (one row per question per attempt)
# ─────────────────────────────────────────────────
class AttemptAnswer(db.Model):
    __tablename__ = 'attempt_answers'
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attempt_id      = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id     = db.Column(db.Integer, db.ForeignKey('questions.id'),    nullable=False)
    selected_option = db.Column(db.Integer)          # NULL = timed out
    is_correct      = db.Column(db.Boolean, nullable=False)
    time_taken      = db.Column(db.Integer)

    def to_dict(self):
        return {
            'question_id':     self.question_id,
            'selected_option': self.selected_option,
            'is_correct':      self.is_correct,
            'time_taken':      self.time_taken
        }


# ─────────────────────────────────────────────────
#  LEVEL PROGRESS  (best score, stars, perfect flag)
# ─────────────────────────────────────────────────
class LevelProgress(db.Model):
    __tablename__ = 'level_progress'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    level_id   = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    best_score = db.Column(db.Integer, default=0)
    best_stars = db.Column(db.Integer, default=0)
    is_perfect = db.Column(db.Boolean, default=False)    # True = 10/10 achieved
    attempts   = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'level_id', name='uq_user_level'),
    )

    def to_dict(self):
        return {
            'level_id':   self.level_id,
            'best_score': self.best_score,
            'best_stars': self.best_stars,
            'is_perfect': self.is_perfect,
            'attempts':   self.attempts,
            'updated_at': self.updated_at.isoformat()
        }


# ─────────────────────────────────────────────────
#  PSYCHOMETRIC RESULT
# ─────────────────────────────────────────────────
class PsychometricResult(db.Model):
    __tablename__ = 'psychometric_results'
    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dominant_trait   = db.Column(db.String(20), nullable=False)
    analytical_score = db.Column(db.Integer, default=0)
    creative_score   = db.Column(db.Integer, default=0)
    social_score     = db.Column(db.Integer, default=0)
    physical_score   = db.Column(db.Integer, default=0)
    career_title     = db.Column(db.String(100))
    taken_at         = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'user_id':        self.user_id,
            'dominant_trait': self.dominant_trait,
            'scores': {
                'analytical': self.analytical_score,
                'creative':   self.creative_score,
                'social':     self.social_score,
                'physical':   self.physical_score
            },
            'career_title': self.career_title,
            'taken_at':     self.taken_at.isoformat()
        }
