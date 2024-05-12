from flask import Blueprint, request, jsonify
from app.models import User, db
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    is_admin = data.get('is_admin', False)

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already in use'}), 400

    new_user = User(username=username, email=email, role=role, is_admin=is_admin)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User successfully registered'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity={'id': user.id, 'is_admin': user.is_admin})
        return jsonify({'access_token': access_token, 'is_admin': user.is_admin}), 200

    return jsonify({'message': 'Invalid credentials'}), 401
