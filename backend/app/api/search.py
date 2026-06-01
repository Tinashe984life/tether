from datetime import datetime
from flask import request, jsonify
from flask import current_app as app
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.note import Note
from ..models.tag import Tag

search_bp = Blueprint('search', __name__)


@search_bp.route('/', methods=['GET'])
@jwt_required()
def search_notes():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify([]), 401
    query_string = (request.args.get('q') or '').strip().lower()
    tag_names = [name.strip() for name in (request.args.get('tags') or '').split(',') if name.strip()]
    from_date = request.args.get('from')
    to_date = request.args.get('to')

    query = Note.query.filter_by(user_id=user_id, deleted_at=None)
    if tag_names:
        query = query.join(Note.tags).filter(Tag.name.in_(tag_names)).distinct()

    notes = query.order_by(Note.updated_at.desc()).all()
    key = app.config.get('ENCRYPTION_KEY')
    results = []
    for note in notes:
        body = note.get_body(key)
        title = (note.title or '')
        created_at = note.created_at
        if from_date:
            try:
                if created_at < datetime.fromisoformat(from_date):
                    continue
            except ValueError:
                pass
        if to_date:
            try:
                if created_at > datetime.fromisoformat(to_date):
                    continue
            except ValueError:
                pass

        if query_string:
            if query_string not in title.lower() and query_string not in body.lower():
                continue

        results.append({
            'id': note.id,
            'title': title,
            'excerpt': body[:120],
            'tags': [t.name for t in note.tags],
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat() if note.updated_at else None,
        })

    return jsonify(results)
