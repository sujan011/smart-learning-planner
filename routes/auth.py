from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'msg': 'Username already exists'}), 409

    user = User(
        username=data['username'],
        password=generate_password_hash(data['password'])
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': 'User registered'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'msg': 'Invalid credentials'}), 401

    token = create_access_token(identity=str(user.id))


    return jsonify({'access_token': token})
