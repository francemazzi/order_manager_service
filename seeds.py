from datetime import datetime, timedelta, UTC
from extensions import db
from models.user import User, UserRole
from models.company import Company, CompanyTag
from models.item import Item
from models.purchase import Purchase, PurchaseItem
from models.sale import Sale, SaleItem

def seed_database():
    """Aggiunge dati di test al database"""
    
    companies = []
    
    tech_company = Company.query.filter_by(vat_number='IT12345678901').first()
    if not tech_company:
        tech_company = Company(
            name='Tech Solutions srl',
            vat_number='IT12345678901',
            email='info@techsolutions.it',
            address='Via Roma 1, Milano',
            phone='+39 02 1234567',
            tag=CompanyTag.SUPPLIER
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
            phone='+39 06 7654321',
            tag=CompanyTag.SUPPLIER
        )
        db.session.add(office_company)
        companies.append(office_company)

    retail_company = Company.query.filter_by(vat_number='IT45678901234').first()
    if not retail_company:
        retail_company = Company(
            name='Retail Store srl',
            vat_number='IT45678901234',
            email='info@retailstore.it',
            address='Via Torino 15, Torino',
            phone='+39 011 9876543',
            tag=CompanyTag.BUYER
        )
        db.session.add(retail_company)
        companies.append(retail_company)

    customer_company = Company.query.filter_by(vat_number='IT78901234567').first()
    if not customer_company:
        customer_company = Company(
            name='Customer Corp spa',
            vat_number='IT78901234567',
            email='info@customercorp.it',
            address='Via Palermo 30, Palermo',
            phone='+39 091 3456789',
            tag=CompanyTag.CUSTOMER
        )
        db.session.add(customer_company)
        companies.append(customer_company)
    
    db.session.commit()
    
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

    if not User.query.filter_by(email='manager@techsolutions.it').first():
        manager = User(
            email='manager@techsolutions.it',
            first_name='Mario',
            last_name='Rossi',
            role=UserRole.MANAGER,
            is_active=True,
            company_id=tech_company.id
        )
        manager.set_password('manager123')
        db.session.add(manager)

    if not User.query.filter_by(email='supplier@officesupplies.it').first():
        supplier = User(
            email='supplier@officesupplies.it',
            first_name='Giuseppe',
            last_name='Verdi',
            role=UserRole.SUPPLIER,
            is_active=True,
            company_id=office_company.id
        )
        supplier.set_password('supplier123')
        db.session.add(supplier)

    if not User.query.filter_by(email='user@techsolutions.it').first():
        basic_user = User(
            email='user@techsolutions.it',
            first_name='Luigi',
            last_name='Bianchi',
            role=UserRole.BASIC,
            is_active=True,
            company_id=tech_company.id
        )
        basic_user.set_password('user123')
        db.session.add(basic_user)

    if not User.query.filter_by(email='manager@retailstore.it').first():
        retail_manager = User(
            email='manager@retailstore.it',
            first_name='Anna',
            last_name='Ferrari',
            role=UserRole.MANAGER,
            is_active=True,
            company_id=retail_company.id
        )
        retail_manager.set_password('manager123')
        db.session.add(retail_manager)

    if not User.query.filter_by(email='user@customercorp.it').first():
        customer_user = User(
            email='user@customercorp.it',
            first_name='Paolo',
            last_name='Neri',
            role=UserRole.BASIC,
            is_active=True,
            company_id=customer_company.id
        )
        customer_user.set_password('user123')
        db.session.add(customer_user)

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

    if not Item.query.filter_by(sku='KEY-WL-001').first():
        keyboard = Item(
            name='Tastiera Wireless',
            description='Tastiera wireless professionale',
            price=89.99,
            price_unit='EUR',
            sku='KEY-WL-001',
            stock=100,
            stock_unit='PZ',
            company_id=tech_company.id
        )
        db.session.add(keyboard)
        items.append(keyboard)

    if not Item.query.filter_by(sku='MOU-WL-001').first():
        mouse = Item(
            name='Mouse Wireless',
            description='Mouse wireless ergonomico',
            price=49.99,
            price_unit='EUR',
            sku='MOU-WL-001',
            stock=150,
            stock_unit='PZ',
            company_id=tech_company.id
        )
        db.session.add(mouse)
        items.append(mouse)
    
    db.session.commit()
    
    if items:
        purchase1 = Purchase(
            company_id=tech_company.id,
            date=datetime.now(UTC) - timedelta(days=7),
            status='delivered',
            total_amount=6999.95,
            notes='Ordine Q1 2024'
        )
        db.session.add(purchase1)
        db.session.commit()
        
        purchase_items1 = [
            PurchaseItem(
                purchase_id=purchase1.id,
                item_id=items[0].id,
                quantity=5,
                unit_price=1000.00,
                total_price=5000.00
            ),
            PurchaseItem(
                purchase_id=purchase1.id,
                item_id=items[1].id,
                quantity=5,
                unit_price=399.99,
                total_price=1999.95
            )
        ]
        for item in purchase_items1:
            db.session.add(item)

        purchase2 = Purchase(
            company_id=office_company.id,
            date=datetime.now(UTC) - timedelta(days=14),
            status='delivered',
            total_amount=2599.00,
            notes='Rifornimento materiale ufficio'
        )
        db.session.add(purchase2)
        db.session.commit()

        purchase_items2 = [
            PurchaseItem(
                purchase_id=purchase2.id,
                item_id=items[2].id,
                quantity=200,
                unit_price=5.99,
                total_price=1198.00
            ),
            PurchaseItem(
                purchase_id=purchase2.id,
                item_id=items[3].id,
                quantity=100,
                unit_price=14.01,
                total_price=1401.00
            )
        ]
        for item in purchase_items2:
            db.session.add(item)
        
        sale1 = Sale(
            customer_name='Mario Rossi',
            customer_email='mario.rossi@email.it',
            customer_address='Via Vittorio Veneto 10, Roma',
            customer_phone='+39 333 1234567',
            date=datetime.now(UTC) - timedelta(days=3),
            status='delivered',
            total_amount=1799.98,
            notes='Consegna presso ufficio'
        )
        db.session.add(sale1)
        db.session.commit()
        
        sale_items1 = [
            SaleItem(
                sale_id=sale1.id,
                item_id=items[0].id,
                quantity=1,
                unit_price=1299.99,
                total_price=1299.99
            ),
            SaleItem(
                sale_id=sale1.id,
                item_id=items[1].id,
                quantity=1,
                unit_price=499.99,
                total_price=499.99
            )
        ]
        for item in sale_items1:
            db.session.add(item)

        sale2 = Sale(
            customer_name='Giuseppe Verdi',
            customer_email='giuseppe.verdi@email.it',
            customer_address='Via Garibaldi 25, Milano',
            customer_phone='+39 333 9876543',
            date=datetime.now(UTC) - timedelta(days=1),
            status='processing',
            total_amount=139.98,
            notes='Spedizione standard'
        )
        db.session.add(sale2)
        db.session.commit()

        sale_items2 = [
            SaleItem(
                sale_id=sale2.id,
                item_id=items[4].id,
                quantity=1,
                unit_price=89.99,
                total_price=89.99
            ),
            SaleItem(
                sale_id=sale2.id,
                item_id=items[5].id,
                quantity=1,
                unit_price=49.99,
                total_price=49.99
            )
        ]
        for item in sale_items2:
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