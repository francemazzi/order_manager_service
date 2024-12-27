from datetime import datetime, timedelta, UTC
from werkzeug.security import generate_password_hash
from extensions import db
from models.user import User
from models.company import Company
from models.item import Item
from models.purchase import Purchase, PurchaseItem
from models.sale import Sale, SaleItem

def seed_database():
    """Aggiunge dati di test al database"""
    
    if not User.query.filter_by(email='test@example.com').first():
        admin = User(
            email='test@example.com',
            password=generate_password_hash('test'),
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        db.session.add(admin)
    
    companies = []
    tech_company = Company.query.filter_by(vat_number='IT12345678901').first()
    if not tech_company:
        tech_company = Company(
            name='Tech Solutions srl',
            vat_number='IT12345678901',
            email='info@techsolutions.it',
            address='Via Roma 1, Milano',
            phone='+39 02 1234567'
        )
        db.session.add(tech_company)
        companies.append(tech_company)
    
    office_company = Company.query.filter_by(vat_number='IT98765432109').first()
    if not office_company:
        office_company = Company(
            name='Office Supplies spa',
            vat_number='IT98765432109',
            email='info@officesupplies.it',
            address='Via Napoli 42, Roma',
            phone='+39 06 7654321'
        )
        db.session.add(office_company)
        companies.append(office_company)
    
    db.session.commit()
    
    items = []
    if not Item.query.filter_by(sku='LAP-X1-001').first():
        laptop = Item(
            name='Laptop Pro X1',
            description='Laptop professionale 15"',
            price=1299.99,
            price_unit='EUR',
            sku='LAP-X1-001',
            stock=50,
            stock_unit='PZ',
            company_id=tech_company.id
        )
        db.session.add(laptop)
        items.append(laptop)
    
    if not Item.query.filter_by(sku='MON-4K-002').first():
        monitor = Item(
            name='Monitor 27" 4K',
            description='Monitor Ultra HD',
            price=499.99,
            price_unit='EUR',
            sku='MON-4K-002',
            stock=30,
            stock_unit='PZ',
            company_id=tech_company.id
        )
        db.session.add(monitor)
        items.append(monitor)
    
    if not Item.query.filter_by(sku='PAP-A4-001').first():
        paper = Item(
            name='Carta A4',
            description='Risma carta 500 fogli',
            price=5.99,
            price_unit='EUR',
            sku='PAP-A4-001',
            stock=1000,
            stock_unit='PZ',
            company_id=office_company.id
        )
        db.session.add(paper)
        items.append(paper)
    
    if not Item.query.filter_by(sku='PEN-BL-002').first():
        pens = Item(
            name='Penne Blu',
            description='Confezione 50 penne',
            price=15.99,
            price_unit='EUR',
            sku='PEN-BL-002',
            stock=200,
            stock_unit='PZ',
            company_id=office_company.id
        )
        db.session.add(pens)
        items.append(pens)
    
    db.session.commit()
    
    if items:
        purchase = Purchase(
            company_id=tech_company.id,
            date=datetime.now(UTC) - timedelta(days=7),
            status='delivered',
            total_amount=6999.95,
            notes='Ordine Q1 2024'
        )
        db.session.add(purchase)
        db.session.commit()
        
        purchase_items = [
            PurchaseItem(
                purchase_id=purchase.id,
                item_id=items[0].id,
                quantity=5,
                unit_price=1000.00,
                total_price=5000.00
            ),
            PurchaseItem(
                purchase_id=purchase.id,
                item_id=items[1].id,
                quantity=5,
                unit_price=399.99,
                total_price=1999.95
            )
        ]
        for item in purchase_items:
            db.session.add(item)
        
        sale = Sale(
            customer_name='Mario Rossi',
            customer_email='mario.rossi@email.it',
            customer_address='Via Vittorio Veneto 10, Roma',
            customer_phone='+39 333 1234567',
            date=datetime.now(UTC) - timedelta(days=3),
            status='delivered',
            total_amount=1799.98,
            notes='Consegna presso ufficio'
        )
        db.session.add(sale)
        db.session.commit()
        
        sale_items = [
            SaleItem(
                sale_id=sale.id,
                item_id=items[0].id,
                quantity=1,
                unit_price=1299.99,
                total_price=1299.99
            ),
            SaleItem(
                sale_id=sale.id,
                item_id=items[1].id,
                quantity=1,
                unit_price=499.99,
                total_price=499.99
            )
        ]
        for item in sale_items:
            db.session.add(item)
        
        db.session.commit()
        print("Nuovi dati aggiunti con successo!")
    else:
        print("I dati di test sono già presenti nel database!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database() 