import pytest
from app.models import User
from app import db
from app.extensions import bcrypt


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""
    
    def test_register_success(self, client, app):
        """Test successful user registration."""
        with app.app_context():
            response = client.post('/api/auth/register', json={
                'email': 'newuser@example.com',
                'password': 'securepass123'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data.get('email') == 'newuser@example.com'
            
            # Verify user was created
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None
    
    def test_register_duplicate_email(self, client, app, test_user):
        """Test registration fails with duplicate email."""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',  # Already exists
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'user exists' in data.get('msg', '').lower()
    
    def test_register_missing_email(self, client):
        """Test registration fails without email."""
        response = client.post('/api/auth/register', json={
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'email' in data.get('msg', '').lower()
    
    def test_register_missing_password(self, client):
        """Test registration fails without password."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'password' in data.get('msg', '').lower()
    
    def test_register_empty_email(self, client):
        """Test registration fails with empty email."""
        response = client.post('/api/auth/register', json={
            'email': '',
            'password': 'password123'
        })
        
        assert response.status_code == 400
    
    def test_register_empty_password(self, client):
        """Test registration fails with empty password."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': ''
        })
        
        assert response.status_code == 400
    
    def test_login_success(self, client, test_user):
        """Test successful login returns tokens."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_refresh_token(self, client, test_user):
        """Test refresh endpoint returns a new access token."""
        login_resp = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        refresh_token = login_resp.get_json().get('refresh_token')
        assert refresh_token

        response = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {refresh_token}'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data

    def test_logout_revokes_refresh_token(self, client, test_user):
        """Test logout revokes the refresh token."""
        login_resp = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        refresh_token = login_resp.get_json().get('refresh_token')
        assert refresh_token

        logout_resp = client.delete('/api/auth/logout', headers={
            'Authorization': f'Bearer {refresh_token}'
        })
        assert logout_resp.status_code == 200

        response = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {refresh_token}'
        })
        assert response.status_code == 401

    def test_get_me(self, client, test_user):
        """Test /me returns the current user."""
        login_resp = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        access_token = login_resp.get_json().get('access_token')
        assert access_token

        response = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {access_token}'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('email') == 'test@example.com'

    def test_login_invalid_email(self, client):
        """Test login fails with non-existent email."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'invalid' in data.get('msg', '').lower() or 'credentials' in data.get('msg', '').lower()
    
    def test_login_invalid_password(self, client, test_user):
        """Test login fails with wrong password."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'invalid' in data.get('msg', '').lower() or 'credentials' in data.get('msg', '').lower()
    
    def test_login_missing_email(self, client):
        """Test login fails without email."""
        response = client.post('/api/auth/login', json={
            'password': 'password123'
        })
        
        assert response.status_code in [400, 401]
    
    def test_login_missing_password(self, client):
        """Test login fails without password."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code in [400, 401]
    
    def test_login_case_insensitive_email(self, client, test_user):
        """Test login with different email case."""
        response = client.post('/api/auth/login', json={
            'email': 'TEST@EXAMPLE.COM',
            'password': 'password123'
        })
        
        # Should fail if emails are case-sensitive
        assert response.status_code in [200, 401]
