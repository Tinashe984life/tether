import pytest
import os
from app import create_app, db
from app.models import User
from app.extensions import bcrypt

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Use test configuration
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'test-secret-key-32-bytes-minimum!!!'
    os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-32-bytes-minimum!!'
    os.environ['ENCRYPTION_KEY'] = '00' * 32  # 64 hex chars = 32 bytes for AES-256
    
    app = create_app()
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password(bcrypt, 'password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    # Reload from database in fresh context
    with app.app_context():
        user = db.session.get(User, user_id)
        yield user

@pytest.fixture
def auth_headers(client, app):
    """Get authorization headers with valid JWT token."""
    with app.app_context():
        # Register or login a test user
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        if response.status_code != 200:
            # User doesn't exist, register first
            reg_resp = client.post('/api/auth/register', json={
                'email': 'test@example.com',
                'password': 'password123'
            })
            response = client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        data = response.get_json()
        if 'access_token' in data:
            return {'Authorization': f'Bearer {data["access_token"]}'}
        else:
            # Fallback - register and try again
            client.post('/api/auth/register', json={
                'email': 'testuser123@example.com',
                'password': 'password123'
            })
            resp = client.post('/api/auth/login', json={
                'email': 'testuser123@example.com',
                'password': 'password123'
            })
            data = resp.get_json()
            return {'Authorization': f'Bearer {data["access_token"]}'}

@pytest.fixture
def auth_headers_invalid():
    """Get authorization headers with invalid token."""
    return {'Authorization': 'Bearer invalid.token.here'}
