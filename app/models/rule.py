from app import db

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    rule_text = db.Column(db.Text, nullable=False)
    l1_category = db.Column(db.String(64), nullable=True)
    l2_category = db.Column(db.String(64), nullable=True)
    l3_category = db.Column(db.String(64), nullable=True)
    exclude = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Rule {self.name}>'
