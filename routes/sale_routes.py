from flask import Blueprint, request, jsonify
from models.sale import Sale, SaleItem, SaleStatus
from models.item import Item
from models.company import Company
from extensions import db
from http import HTTPStatus

sale_bp = Blueprint('sale', __name__)

@sale_bp.route('/sales', methods=['POST'])
def create_sale():
    data = request.get_json()
    
    required_fields = ['customer_name', 'items', 'company_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo {field} obbligatorio'}), HTTPStatus.BAD_REQUEST
    
    # Verifica che l'azienda esista
    company = Company.query.get(data['company_id'])
    if not company:
        return jsonify({'error': f'Azienda {data["company_id"]} non trovata'}), HTTPStatus.NOT_FOUND
    
    total_amount = 0
    sale_items = []
    
    for item_data in data['items']:
        if not all(k in item_data for k in ('item_id', 'quantity', 'unit_price')):
            return jsonify({'error': 'Dati item incompleti'}), HTTPStatus.BAD_REQUEST
        
        item = Item.query.get(item_data['item_id'])
        if not item:
            return jsonify({'error': f'Item {item_data["item_id"]} non trovato'}), HTTPStatus.NOT_FOUND
        
        if item.stock < item_data['quantity']:
            return jsonify({'error': f'Quantità non disponibile per item {item.name}'}), HTTPStatus.BAD_REQUEST
        
        total_price = item_data['quantity'] * item_data['unit_price']
        sale_items.append({
            'item': item,
            'quantity': item_data['quantity'],
            'unit_price': item_data['unit_price'],
            'total_price': total_price
        })
        total_amount += total_price
    
    try:
        sale = Sale(
            customer_name=data['customer_name'],
            customer_email=data.get('customer_email'),
            customer_address=data.get('customer_address'),
            customer_phone=data.get('customer_phone'),
            total_amount=total_amount,
            notes=data.get('notes'),
            status=data.get('status', SaleStatus.PENDING),
            company_id=company.id
        )
        
        for item_data in sale_items:
            sale_item = SaleItem(
                item=item_data['item'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            sale.items.append(sale_item)
            
            if sale.status == SaleStatus.CONFIRMED:
                item_data['item'].stock -= item_data['quantity']
        
        db.session.add(sale)
        db.session.commit()
        
        return jsonify(sale.to_dict()), HTTPStatus.CREATED
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

@sale_bp.route('/sales', methods=['GET'])
def get_sales():
    status = request.args.get('status')
    customer_email = request.args.get('customer_email')
    
    query = Sale.query
    
    if status:
        query = query.filter_by(status=status)
    if customer_email:
        query = query.filter_by(customer_email=customer_email)
    
    sales = query.order_by(Sale.date.desc()).all()
    return jsonify([sale.to_dict() for sale in sales])

@sale_bp.route('/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    return jsonify(sale.to_dict())

@sale_bp.route('/sales/<int:sale_id>', methods=['PUT'])
def update_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    data = request.get_json()
    old_status = sale.status
    
    if 'status' in data:
        if data['status'] not in vars(SaleStatus).values():
            return jsonify({'error': 'Stato non valido'}), HTTPStatus.BAD_REQUEST
        
        if old_status != SaleStatus.CONFIRMED and data['status'] == SaleStatus.CONFIRMED:
            for sale_item in sale.items:
                if sale_item.item.stock < sale_item.quantity:
                    return jsonify({'error': f'Quantità non disponibile per item {sale_item.item.name}'}), HTTPStatus.BAD_REQUEST
                sale_item.item.stock -= sale_item.quantity
        
        elif old_status == SaleStatus.CONFIRMED and data['status'] == SaleStatus.CANCELLED:
            for sale_item in sale.items:
                sale_item.item.stock += sale_item.quantity
        
        sale.status = data['status']
    
    for field in ['customer_name', 'customer_email', 'customer_address', 'customer_phone', 'notes']:
        if field in data:
            setattr(sale, field, data[field])
    
    try:
        db.session.commit()
        return jsonify(sale.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

@sale_bp.route('/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    
    if sale.status != SaleStatus.PENDING:
        return jsonify({'error': 'Solo le vendite in stato pending possono essere eliminate'}), HTTPStatus.BAD_REQUEST
    
    try:
        db.session.delete(sale)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST 