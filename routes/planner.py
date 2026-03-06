from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from models import Exam, Topic,db

planner_bp = Blueprint('planner', __name__)


@planner_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_plan():
    user_id = get_jwt_identity()

    exam = Exam.query.filter_by(user_id=user_id).first()
    topics = Topic.query.all()

    days_left = (exam.exam_date - date.today()).days

    plan = []
    for topic in topics:
        plan.append({
            'topic': topic.name,
            'hours': round(exam.daily_hours / len(topics), 2)
        })

    return jsonify({
        'days_left': days_left,
        'daily_plan': plan
    })


@planner_bp.route('/exam', methods=['POST'])
@jwt_required()
def add_exam():
    user_id = get_jwt_identity()
    data = request.json

    exam_date = date.fromisoformat(data['exam_date'])
    daily_hours = data['daily_hours']

    exam = Exam(
        exam_date=exam_date,
        daily_hours=daily_hours,
        user_id=user_id
    )

    db.session.add(exam)
    db.session.commit()

    return jsonify({
        'msg': 'Exam added successfully',
        'exam_date': str(exam_date),
        'daily_hours': daily_hours
    }), 201


@planner_bp.route('/topic', methods=['POST'])
@jwt_required()
def add_topic():
    user_id = int(get_jwt_identity())
    data = request.json

    if 'name' not in data:
        return jsonify({'msg': 'Topic name required'}), 400

    topic = Topic(
        name=data['name'],
        user_id=user_id
    )

    db.session.add(topic)
    db.session.commit()

    return jsonify({
        'msg': 'Topic added successfully',
        'topic': data['name']
    }), 201


@planner_bp.route('/plan', methods=['GET'])
@jwt_required()
def get_daily_plan():
    user_id = get_jwt_identity()

    exam = Exam.query.filter_by(user_id=user_id).first()
    if not exam:
        return jsonify({'msg': 'No exam found'}), 404

    topics = Topic.query.filter_by(user_id=user_id).all()
    if not topics:
        return jsonify({'msg': 'No topics found'}), 404

    days_left = (exam.exam_date - date.today()).days
    if days_left <= 0:
        return jsonify({'msg': 'Exam date already passed'}), 400

    hours_per_topic = round(exam.daily_hours / len(topics), 2)

    daily_plan = []
    for topic in topics:
        daily_plan.append({
            'topic': topic.name,
            'hours_per_day': hours_per_topic
        })

    return jsonify({
        'days_left': days_left,
        'daily_plan': daily_plan
    })