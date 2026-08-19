from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    interviews = db.relationship('Interview', backref='user', lazy=True)

class Interview(db.Model):
    __tablename__ = 'interviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    experience_levels = db.Column(db.JSON, nullable=False)  # {skill: years}
    job_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='interview', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))
    score = db.Column(db.Integer, default=0)
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)  # Max 5000 chars enforced in API
    ai_score = db.Column(db.Integer, default=0)  # Score from 0-10
    ai_feedback = db.Column(db.Text)  # Feedback from AI evaluation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ATSScan(db.Model):
    __tablename__ = 'ats_scans'
    id = db.Column(db.Integer, primary_key=True)
    resume_text = db.Column(db.Text, nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    overall_score = db.Column(db.Integer, default=0)
    keyword_score = db.Column(db.Integer, default=0)
    skills_score = db.Column(db.Integer, default=0)
    experience_score = db.Column(db.Integer, default=0)
    format_score = db.Column(db.Integer, default=0)
    matched_keywords = db.Column(db.JSON, default=list)
    missing_keywords = db.Column(db.JSON, default=list)
    suggestions = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
