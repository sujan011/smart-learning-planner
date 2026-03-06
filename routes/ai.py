from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import StudySession
from ml.readiness import predict_readiness


ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/readiness', methods=['GET'])
@jwt_required()
def readiness():
    user_id = get_jwt_identity()

    sessions = StudySession.query.filter_by(user_id=user_id).all()

    total_hours = sum(s.actual_hours for s in sessions)
    completion = len(sessions) * 10
    confidence = 75

    score = predict_readiness(total_hours, completion, confidence)

    return jsonify({'readiness_score': score})
