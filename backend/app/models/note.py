from datetime import datetime
from ..extensions import db
from ..utils.encryption import encrypt_text, decrypt_text
from .tag import note_tags


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    body_encrypted = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    tags = db.relationship(
        'Tag',
        secondary=note_tags,
        backref=db.backref('notes', lazy='dynamic'),
        lazy='dynamic',
    )

    def set_body(self, plaintext: str, key_hex: str):
        self.body_encrypted = encrypt_text(plaintext or '', key_hex)

    def get_body(self, key_hex: str) -> str:
        if not self.body_encrypted:
            return ''
        return decrypt_text(self.body_encrypted, key_hex)
