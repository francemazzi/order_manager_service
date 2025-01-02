from flask import Blueprint, request, jsonify
from models.company import Company, CompanyTag
from extensions import db
from http import HTTPStatus

company_bp = Blueprint('company', __name__)

@company_bp.route('/companies', methods=['POST'])
def create_company():
    data = request.get_json()
    
    required_fields = ['name', 'vat_number', 'email', 'tag']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo {field} obbligatorio'}), HTTPStatus.BAD_REQUEST
    
    try:
        company = Company(
            name=data['name'],
            vat_number=data['vat_number'],
            email=data['email'],
            address=data.get('address'),
            phone=data.get('phone'),
            tag=CompanyTag(data['tag'])
        )
        
        db.session.add(company)
        db.session.commit()
        return jsonify(company.to_dict()), HTTPStatus.CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

@company_bp.route('/companies', methods=['GET'])
def get_companies():
    companies = Company.query.all()
    return jsonify([company.to_dict() for company in companies])

@company_bp.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    company = Company.query.get_or_404(company_id)
    return jsonify(company.to_dict())

@company_bp.route('/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    company = Company.query.get_or_404(company_id)
    data = request.get_json()
    
    try:
        for key, value in data.items():
            if hasattr(company, key):
                setattr(company, key, value)
        
        db.session.commit()
        return jsonify(company.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

@company_bp.route('/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    try:
        db.session.delete(company)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST 