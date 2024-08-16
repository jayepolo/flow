from app import db
from datetime import datetime

class UploadedTransaction(db.Model):
    __tablename__ = 'uploaded_transaction'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    account_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reference_no = db.Column(db.String(100), nullable=True)
    category_l1 = db.Column(db.String(64), nullable=True)
    category_l2 = db.Column(db.String(64), nullable=True)
    category_l3 = db.Column(db.String(64), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    applied_rules = db.Column(db.String(255), nullable=True)
    include = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('uploaded_transactions', lazy='dynamic'))

    def __repr__(self):
        return f'<UploadedTransaction {self.id}: {self.date} - {self.amount}>'

class AcceptedTransaction(db.Model):
    __tablename__ = 'accepted_transaction'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    account_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reference_no = db.Column(db.String(100), nullable=True)
    category_l1 = db.Column(db.String(64), nullable=True)
    category_l2 = db.Column(db.String(64), nullable=True)
    category_l3 = db.Column(db.String(64), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    applied_rules = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref=db.backref('accepted_transactions', lazy='dynamic'))

    def __repr__(self):
        return f'<AcceptedTransaction {self.id}: {self.date} - {self.amount}>'

# Example usage of datetime (not part of the model, just for demonstration)
def create_uploaded_transaction(date_str, **kwargs):
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    return UploadedTransaction(date=date, **kwargs)

def create_accepted_transaction(date_str, **kwargs):
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    return AcceptedTransaction(date=date, **kwargs)