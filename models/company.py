from datetime import datetime
from extensions import db
from enum import Enum

class CompanyTag(Enum):
    BUYER = 'buyer'
    SUPPLIER = 'supplier'
    CUSTOMER = 'customer'

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vat_number = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(200))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    tag = db.Column(db.Enum(CompanyTag), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('Item', backref='company', lazy=True)

    def __repr__(self):
        return f'<Company {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'vat_number': self.vat_number,
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            'tag': self.tag.value if self.tag else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 