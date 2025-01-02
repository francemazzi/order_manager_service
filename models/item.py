from datetime import datetime
from extensions import db

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    price_unit = db.Column(db.String(20), nullable=False, default='EUR')  
    sku = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=0)
    stock_unit = db.Column(db.String(20), nullable=False, default='PZ')  
    gross_margin = db.Column(db.Numeric(5, 2), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('sku', 'company_id', name='unique_sku_per_company'),
    )

    def __repr__(self):
        return f'<Item {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'price_unit': self.price_unit,
            'sku': self.sku,
            'stock': self.stock,
            'stock_unit': self.stock_unit,
            'gross_margin': float(self.gross_margin) if self.gross_margin is not None else None,
            'company_id': self.company_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 