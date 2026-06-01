import os
from app import create_app
from app.extensions import db

os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
os.environ['ENCRYPTION_KEY'] = '00' * 32

app = create_app()
with app.app_context():
    db.create_all()
    client = app.test_client()
    resp = client.post('/api/auth/register', json={'email': 'test@example.com', 'password': 'password123'})
    print('register', resp.status_code, resp.get_json())
    login = client.post('/api/auth/login', json={'email': 'test@example.com', 'password': 'password123'})
    print('login', login.status_code, login.get_json())
    token = login.get_json().get('access_token')
    print('token', token[:20] if token else None)
    search = client.get('/api/search/?q=other', headers={'Authorization': f'Bearer {token}'})
    print('search', search.status_code, search.get_data(as_text=True))
