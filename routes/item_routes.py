from flask import Blueprint, request, jsonify
from models.item import Item
from models.company import Company
from extensions import db
from http import HTTPStatus

item_bp = Blueprint('item', __name__)

@item_bp.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    
    required_fields = ['name', 'price', 'sku', 'company_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo {field} obbligatorio'}), HTTPStatus.BAD_REQUEST
    
    company = Company.query.get(data['company_id'])
    if not company:
        return jsonify({'error': 'Azienda non trovata'}), HTTPStatus.NOT_FOUND
    
    item = Item(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        sku=data['sku'],
        stock=data.get('stock', 0),
        company_id=data['company_id']
    )
    
    try:
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), HTTPStatus.CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

@item_bp.route('/items', methods=['GET'])
def get_items():
    company_id = request.args.get('company_id', type=int)
    query = Item.query
    
    if company_id:
        query = query.filter_by(company_id=company_id)
    
    items = query.all()
    return jsonify([item.to_dict() for item in items])

@item_bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@item_bp.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json()
    
    if 'company_id' in data:
        company = Company.query.get(data['company_id'])
        if not company:
            return jsonify({'error': 'Azienda non trovata'}), HTTPStatus.NOT_FOUND
    
    try:
        for key, value in data.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        db.session.commit()
        return jsonify(item.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

@item_bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST 