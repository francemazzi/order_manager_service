from flask import Blueprint, request, jsonify
from models.user import User, UserRole
from models.company import Company
from extensions import db
from http import HTTPStatus

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Email e password sono obbligatori'}), HTTPStatus.BAD_REQUEST
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email già registrata'}), HTTPStatus.CONFLICT
    
    role = data.get('role', 'basic').lower()
    if role not in [r.value for r in UserRole]:
        return jsonify({'error': f'Ruolo non valido. I ruoli disponibili sono: {", ".join([r.value for r in UserRole])}'}), HTTPStatus.BAD_REQUEST
    
    if 'company_id' in data:
        company = Company.query.get(data['company_id'])
        if not company:
            return jsonify({'error': 'Azienda non trovata'}), HTTPStatus.NOT_FOUND
    
    user = User(
        email=data['email'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role=UserRole(role),
        is_active=data.get('is_active', True),
        company_id=data.get('company_id')
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), HTTPStatus.CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        if 'email' in data:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email già registrata'}), HTTPStatus.CONFLICT
            user.email = data['email']
        
        if 'role' in data:
            role = data['role'].lower()
            if role not in [r.value for r in UserRole]:
                return jsonify({'error': f'Ruolo non valido. I ruoli disponibili sono: {", ".join([r.value for r in UserRole])}'}), HTTPStatus.BAD_REQUEST
            user.role = UserRole(role)
            
        if 'password' in data:
            user.set_password(data['password'])
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]) 