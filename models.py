from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Exam(db.Model):
    __tablename__ = 'exam'

    id = db.Column(db.Integer, primary_key=True)
    exam_date = db.Column(db.Date, nullable=False)
    daily_hours = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Topic(db.Model):
    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class StudySession(db.Model):
    __tablename__ = 'study_session'

    id = db.Column(db.Integer, primary_key=True)
    actual_hours = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
