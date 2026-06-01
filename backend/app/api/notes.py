from flask import request, jsonify
from flask import current_app as app
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.note import Note
from ..models.tag import Tag

notes_bp = Blueprint('notes', __name__)


def serialize_note(note, key):
    return {
        'id': note.id,
        'title': note.title,
        'body': note.get_body(key),
        'tags': [t.name for t in note.tags],
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat() if note.updated_at else None,
    }


def get_or_create_tags(tag_names):
    tags = []
    for name in set((tag_name or '').strip() for tag_name in (tag_names or [])):
        if not name:
            continue
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.flush()
        tags.append(tag)
    return tags


@notes_bp.route('/', methods=['GET'])
@jwt_required()
def list_notes():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify([]), 401
    page = max(int(request.args.get('page', 1)), 1)
    per_page = min(max(int(request.args.get('per_page', 20)), 1), 100)
    query = Note.query.filter_by(user_id=user_id, deleted_at=None).order_by(Note.updated_at.desc())
    notes = query.paginate(page=page, per_page=per_page, error_out=False).items
    key = app.config.get('ENCRYPTION_KEY')
    return jsonify([serialize_note(n, key) for n in notes])


@notes_bp.route('/', methods=['POST'])
@jwt_required()
def create_note():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    title = data.get('title')
    body = data.get('body', '')
    tags = get_or_create_tags(data.get('tags', []))
    key = app.config.get('ENCRYPTION_KEY')
    note = Note(user_id=user_id, title=title)
    note.set_body(body, key)
    note.tags.extend(tags)
    db.session.add(note)
    db.session.commit()
    return jsonify({'id': note.id}), 201


@notes_bp.route('/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'msg': 'invalid token identity'}), 401
    note = Note.query.filter_by(id=note_id, user_id=user_id, deleted_at=None).first_or_404()
    key = app.config.get('ENCRYPTION_KEY')
    return jsonify(serialize_note(note, key))


@notes_bp.route('/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'msg': 'invalid token identity'}), 401
    note = Note.query.filter_by(id=note_id, user_id=user_id, deleted_at=None).first_or_404()
    data = request.get_json() or {}
    note.title = data.get('title', note.title)
    body = data.get('body')
    tags = data.get('tags')
    key = app.config.get('ENCRYPTION_KEY')
    if tags is not None:
        note.tags = get_or_create_tags(tags)
    if body is not None:
        from ..models.note_version import NoteVersion
        ver = NoteVersion(note_id=note.id, body_encrypted=note.body_encrypted)
        db.session.add(ver)
        note.set_body(body, key)
    db.session.commit()
    return jsonify({'id': note.id}), 200


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'msg': 'invalid token identity'}), 401
    note = Note.query.filter_by(id=note_id, user_id=user_id, deleted_at=None).first_or_404()
    note.deleted_at = note.updated_at
    db.session.commit()
    return jsonify({'id': note.id}), 200


@notes_bp.route('/<int:note_id>/versions', methods=['GET'])
@jwt_required()
def list_note_versions(note_id):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'msg': 'invalid token identity'}), 401
    note = Note.query.filter_by(id=note_id, user_id=user_id).first_or_404()
    versions = [
        {
            'id': version.id,
            'created_at': version.created_at.isoformat(),
        }
        for version in note.versions.order_by('created_at').all()
    ]
    return jsonify(versions)


@notes_bp.route('/<int:note_id>/restore/<int:version_id>', methods=['POST'])
@jwt_required()
def restore_note_version(note_id, version_id):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'msg': 'invalid token identity'}), 401
    note = Note.query.filter_by(id=note_id, user_id=user_id, deleted_at=None).first_or_404()
    version = note.versions.filter_by(id=version_id).first_or_404()
    key = app.config.get('ENCRYPTION_KEY')
    current_version = note.body_encrypted
    if current_version is not None:
        from ..models.note_version import NoteVersion
        db.session.add(NoteVersion(note_id=note.id, body_encrypted=current_version))
    note.body_encrypted = version.body_encrypted
    db.session.commit()
    return jsonify({'id': note.id}), 200
