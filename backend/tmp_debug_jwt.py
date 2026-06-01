from app import create_app
from app.models import User
from app.extensions import db, bcrypt

app = create_app()
with app.app_context():
    db.create_all()
    user = User(email='test@example.com')
    user.set_password(bcrypt, 'password123')
    db.session.add(user)
    db.session.commit()
    client = app.test_client()
    login = client.post('/api/auth/login', json={'email': 'test@example.com', 'password': 'password123'})
    print('login', login.status_code, login.get_json())
    token = login.get_json().get('refresh_token')
    r = client.post('/api/auth/refresh', headers={'Authorization': f'Bearer {token}'})
    print('refresh', r.status_code, r.get_json())
