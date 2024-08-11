from app import db
from datetime import datetime

class UploadedTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    account_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reference_no = db.Column(db.String(100), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    include = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    category = db.relationship('Category', backref='uploaded_transactions')
    user = db.relationship('User', backref='uploaded_transactions')

class AcceptedTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False, default='UNKNOWN')
    account_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reference_no = db.Column(db.String(100), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    category = db.relationship('Category', backref='accepted_transactions')
    user = db.relationship('User', backref='accepted_transactions')
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
