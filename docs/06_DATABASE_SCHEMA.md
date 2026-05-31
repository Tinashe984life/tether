# MNEMO — Database Schema
## Document: 06_DATABASE_SCHEMA.md

---

## SQLAlchemy Models

### User

```python
# app/models/user.py
from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email         = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name  = db.Column(db.String(100))
    bio           = db.Column(db.Text)
    avatar_url    = db.Column(db.String(500))
    theme_pref    = db.Column(db.String(20), default='canvas')  # 'space'|'canvas'|'calendar'
    default_visibility = db.Column(db.String(20), default='private')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at    = db.Column(db.DateTime, nullable=True)

    # Relationships
    notes         = db.relationship('Note', backref='author', lazy='dynamic')
    notifications = db.relationship('Notification', backref='recipient', lazy='dynamic')

    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat(),
            'follower_count': self.followers.count(),
            'following_count': self.following.count(),
            'note_count': self.notes.filter_by(deleted_at=None, visibility='public').count(),
        }
        if include_private:
            data['email'] = self.email
            data['theme_pref'] = self.theme_pref
            data['default_visibility'] = self.default_visibility
        return data
```

---

### Note

```python
# app/models/note.py
from app.extensions import db
from app.utils.encryption import encrypt, decrypt
from app.utils.slugify import generate_slug
from datetime import datetime

class Note(db.Model):
    __tablename__ = 'notes'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title           = db.Column(db.String(500), default='')
    slug            = db.Column(db.String(600), unique=True, index=True)

    # Encrypted storage
    body_encrypted  = db.Column(db.Text)   # base64 ciphertext
    body_nonce      = db.Column(db.String(50))  # base64 nonce (16 chars)

    # Plaintext search index (separate column — see architecture note)
    body_plaintext  = db.Column(db.Text)   # WARNING: plaintext for FTS only

    visibility      = db.Column(db.String(20), default='private', index=True)
    # Values: 'private' | 'unlisted' | 'public'

    word_count      = db.Column(db.Integer, default=0)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at      = db.Column(db.DateTime, nullable=True)

    # Relationships
    tags            = db.relationship('Tag', secondary='note_tags', back_populates='notes')
    versions        = db.relationship('NoteVersion', backref='note', lazy='dynamic',
                                       order_by='NoteVersion.created_at.desc()')
    reactions       = db.relationship('Reaction', backref='note', lazy='dynamic')
    comments        = db.relationship('Comment', backref='note', lazy='dynamic')

    def set_body(self, plaintext: str):
        """Encrypt and store body. Also updates plaintext index."""
        result = encrypt(plaintext)
        self.body_encrypted = result['ciphertext']
        self.body_nonce = result['nonce']
        self.body_plaintext = plaintext  # For FTS
        self.word_count = len(plaintext.split())

    def get_body(self) -> str:
        """Decrypt and return body."""
        if not self.body_encrypted:
            return ''
        return decrypt(self.body_nonce, self.body_encrypted)

    def generate_slug(self):
        from app.utils.slugify import generate_unique_slug
        self.slug = generate_unique_slug(self.title or 'note', self.user_id)

    def to_dict(self, include_body=False):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'visibility': self.visibility,
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': [t.name for t in self.tags],
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'avatar_url': self.author.avatar_url,
            },
            'reaction_counts': self._get_reaction_counts(),
            'comment_count': self.comments.filter_by(deleted_at=None).count(),
        }
        if include_body:
            data['body'] = self.get_body()
        return data

    def _get_reaction_counts(self):
        from sqlalchemy import func
        from app.models.reaction import Reaction
        results = db.session.query(
            Reaction.emoji, func.count(Reaction.id)
        ).filter_by(note_id=self.id).group_by(Reaction.emoji).all()
        return {emoji: count for emoji, count in results}
```

---

### NoteVersion

```python
# app/models/note_version.py
from app.extensions import db
from app.utils.encryption import encrypt, decrypt
from datetime import datetime

class NoteVersion(db.Model):
    __tablename__ = 'note_versions'

    id             = db.Column(db.Integer, primary_key=True)
    note_id        = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False, index=True)
    title          = db.Column(db.String(500))
    body_encrypted = db.Column(db.Text)
    body_nonce     = db.Column(db.String(50))
    version_number = db.Column(db.Integer, nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def get_body(self) -> str:
        if not self.body_encrypted:
            return ''
        return decrypt(self.body_nonce, self.body_encrypted)

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'title': self.title,
            'version_number': self.version_number,
            'created_at': self.created_at.isoformat(),
        }
```

---

### Tag & Note-Tag Association

```python
# app/models/tag.py
from app.extensions import db

note_tags = db.Table('note_tags',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Tag(db.Model):
    __tablename__ = 'tags'

    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    # Tags are per-user (same tag name across users = different tag records)

    notes   = db.relationship('Note', secondary='note_tags', back_populates='tags')

    __table_args__ = (
        db.UniqueConstraint('name', 'user_id', name='uq_tag_name_user'),
    )
```

---

### Follow (Social Graph)

```python
# app/models/follow.py
from app.extensions import db
from datetime import datetime

class Follow(db.Model):
    __tablename__ = 'follows'

    follower_id  = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

# Add to User model:
# followers = db.relationship('User', secondary='follows',
#     primaryjoin='User.id == Follow.following_id',
#     secondaryjoin='User.id == Follow.follower_id',
#     backref=db.backref('following', lazy='dynamic'), lazy='dynamic')
```

---

### Reaction

```python
# app/models/reaction.py
from app.extensions import db
from datetime import datetime

VALID_EMOJIS = ['👍', '❤️', '🔥', '💡']

class Reaction(db.Model):
    __tablename__ = 'reactions'

    id         = db.Column(db.Integer, primary_key=True)
    note_id    = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False, index=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    emoji      = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('note_id', 'user_id', 'emoji', name='uq_reaction'),
    )
```

---

### Comment

```python
# app/models/comment.py
from app.extensions import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'

    id         = db.Column(db.Integer, primary_key=True)
    note_id    = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False, index=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id  = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    body       = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    author     = db.relationship('User', foreign_keys=[user_id])
    replies    = db.relationship('Comment', foreign_keys=[parent_id])

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'parent_id': self.parent_id,
            'body': self.body if not self.deleted_at else '[deleted]',
            'created_at': self.created_at.isoformat(),
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'avatar_url': self.author.avatar_url,
            },
            'replies': [r.to_dict() for r in self.replies if not r.deleted_at],
        }
```

---

### Notification

```python
# app/models/notification.py
from app.extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type        = db.Column(db.String(50), nullable=False)
    # Types: 'new_follower' | 'reaction' | 'comment' | 'reply'
    actor_id    = db.Column(db.Integer, db.ForeignKey('users.id'))
    note_id     = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=True)
    is_read     = db.Column(db.Boolean, default=False, index=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    actor       = db.relationship('User', foreign_keys=[actor_id])
```

---

## FTS5 Virtual Table (SQLite)

Run this migration manually or add to a `flask db upgrade` custom script:

```sql
-- Run after base schema is created
CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
    title,
    body_plaintext,
    content='notes',
    content_rowid='id',
    tokenize='porter ascii'
);

-- Sync triggers
CREATE TRIGGER notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, title, body_plaintext)
    VALUES (new.id, new.title, new.body_plaintext);
END;

CREATE TRIGGER notes_au AFTER UPDATE ON notes BEGIN
    DELETE FROM notes_fts WHERE rowid = old.id;
    INSERT INTO notes_fts(rowid, title, body_plaintext)
    VALUES (new.id, new.title, new.body_plaintext);
END;

CREATE TRIGGER notes_ad AFTER DELETE ON notes BEGIN
    DELETE FROM notes_fts WHERE rowid = old.id;
END;
```

---

## Migration Commands

```bash
# Initialize (run once)
flask db init

# Create migration after model changes
flask db migrate -m "description of change"

# Apply migrations
flask db upgrade

# Rollback one migration
flask db downgrade

# See current state
flask db current
```

---

## ER Diagram (Text)

```
users ──────────< notes >──────────< note_tags >────── tags
  |                 |
  |                 ├──────────< note_versions
  |                 ├──────────< reactions
  |                 └──────────< comments >──── comments (self-ref, replies)
  |
  ├──────────< follows (follower_id / following_id)
  └──────────< notifications
```
