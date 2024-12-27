from flask import Blueprint, request, jsonify
from models.purchase import Purchase, PurchaseItem, PurchaseStatus
from models.company import Company
from models.item import Item
from extensions import db
from http import HTTPStatus

purchase_bp = Blueprint('purchase', __name__)

@purchase_bp.route('/purchases', methods=['POST'])
def create_purchase():
    data = request.get_json()
    
    required_fields = ['company_id', 'items']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo {field} obbligatorio'}), HTTPStatus.BAD_REQUEST
    
    company = Company.query.get(data['company_id'])
    if not company:
        return jsonify({'error': 'Azienda non trovata'}), HTTPStatus.NOT_FOUND
    
    total_amount = 0
    purchase_items = []
    
    for item_data in data['items']:
        if not all(k in item_data for k in ('item_id', 'quantity', 'unit_price')):
            return jsonify({'error': 'Dati item incompleti'}), HTTPStatus.BAD_REQUEST
        
        item = Item.query.get(item_data['item_id'])
        if not item:
            return jsonify({'error': f'Item {item_data["item_id"]} non trovato'}), HTTPStatus.NOT_FOUND
        
        if item.company_id != company.id:
            return jsonify({'error': f'Item {item_data["item_id"]} non appartiene all\'azienda selezionata'}), HTTPStatus.BAD_REQUEST
        
        total_price = item_data['quantity'] * item_data['unit_price']
        purchase_items.append({
            'item': item,
            'quantity': item_data['quantity'],
            'unit_price': item_data['unit_price'],
            'total_price': total_price
        })
        total_amount += total_price
    
    try:
        purchase = Purchase(
            company_id=company.id,
            total_amount=total_amount,
            notes=data.get('notes'),
            status=data.get('status', PurchaseStatus.PENDING)
        )
        
        for item_data in purchase_items:
            purchase_item = PurchaseItem(
                item=item_data['item'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            purchase.items.append(purchase_item)
        
        db.session.add(purchase)
        db.session.commit()
        
        return jsonify(purchase.to_dict()), HTTPStatus.CREATED
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

@purchase_bp.route('/purchases', methods=['GET'])
def get_purchases():
    company_id = request.args.get('company_id', type=int)
    status = request.args.get('status')
    
    query = Purchase.query
    
    if company_id:
        query = query.filter_by(company_id=company_id)
    if status:
        query = query.filter_by(status=status)
    
    purchases = query.order_by(Purchase.date.desc()).all()
    return jsonify([purchase.to_dict() for purchase in purchases])

@purchase_bp.route('/purchases/<int:purchase_id>', methods=['GET'])
def get_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    return jsonify(purchase.to_dict())

@purchase_bp.route('/purchases/<int:purchase_id>', methods=['PUT'])
def update_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    data = request.get_json()
    
    if 'status' in data:
        if data['status'] not in vars(PurchaseStatus).values():
            return jsonify({'error': 'Stato non valido'}), HTTPStatus.BAD_REQUEST
        purchase.status = data['status']
    
    if 'notes' in data:
        purchase.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify(purchase.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

@purchase_bp.route('/purchases/<int:purchase_id>', methods=['DELETE'])
def delete_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    
    if purchase.status != PurchaseStatus.PENDING:
        return jsonify({'error': 'Solo gli acquisti in stato pending possono essere eliminati'}), HTTPStatus.BAD_REQUEST
    
    try:
        db.session.delete(purchase)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST 