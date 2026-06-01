from flask import request, jsonify
from flask import current_app as app
from flask import Blueprint
from ..extensions import db, bcrypt, jwt
from ..models.user import User
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

auth_bp = Blueprint('auth', __name__)
revoked_tokens = set()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload.get('jti') in revoked_tokens


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    if not email or not password:
        return jsonify({'msg': 'email and password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'user exists'}), 400
    user = User(email=email)
    user.set_password(bcrypt, password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'email': user.email}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    if not email or not password:
        return jsonify({'msg': 'email and password required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(bcrypt, password):
        return jsonify({'msg': 'invalid credentials'}), 401
    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))
    return jsonify({'access_token': access, 'refresh_token': refresh}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access = create_access_token(identity=str(user_id))
    return jsonify({'access_token': access}), 200


@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required(refresh=True)
def logout():
    jwt_data = get_jwt()
    revoked_tokens.add(jwt_data['jti'])
    return jsonify({'msg': 'refresh token revoked'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'msg': 'invalid token identity'}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'user not found'}), 404
    return jsonify({'id': user.id, 'email': user.email}), 200
