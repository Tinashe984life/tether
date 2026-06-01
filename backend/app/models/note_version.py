from datetime import datetime
from ..extensions import db


class NoteVersion(db.Model):
    __tablename__ = 'note_versions'
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    body_encrypted = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    note = db.relationship('Note', backref=db.backref('versions', lazy='dynamic'))
