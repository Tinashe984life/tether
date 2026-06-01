from datetime import datetime
from ..extensions import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship('Note', backref='owner', lazy='dynamic')

    def check_password(self, bcrypt, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_password(self, bcrypt, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
