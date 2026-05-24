"""
Unit tests for the main application
"""

import pytest
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers(client):
    """Create authenticated headers for testing"""
    # Register a test user
    client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpassword123',
        'email': 'test@example.com'
    })

    # Login to get token
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpassword123'
    })

    data = json.loads(response.data)
    token = data.get('access_token')

    return {'Authorization': f'Bearer {token}'}


class TestHealthEndpoint:
    """Test the health check endpoint"""

    def test_health_check(self, client):
        """Test that health endpoint returns 200 and correct data"""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'service' in data
        assert 'version' in data


class TestHomeEndpoint:
    """Test the home page endpoint"""

    def test_home_page(self, client):
        """Test that home page returns HTML"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'DevSecOps' in response.data


class TestRegistration:
    """Test user registration"""

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/register', json={
            'username': 'newuser',
            'password': 'password123',
            'email': 'newuser@example.com'
        })

        assert response.status_code == 201

        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert data['username'] == 'newuser'

    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/api/register', json={
            'username': 'newuser'
        })

        assert response.status_code == 400

    def test_register_invalid_username(self, client):
        """Test registration with invalid username"""
        response = client.post('/api/register', json={
            'username': 'invalid username!',
            'password': 'password123',
            'email': 'test@example.com'
        })

        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/api/register', json={
            'username': 'newuser',
            'password': 'password123',
            'email': 'invalid-email'
        })

        assert response.status_code == 400

    def test_register_duplicate_user(self, client):
        """Test registration with duplicate username"""
        # First registration
        client.post('/api/register', json={
            'username': 'duplicate',
            'password': 'password123',
            'email': 'duplicate@example.com'
        })

        # Second registration with same username
        response = client.post('/api/register', json={
            'username': 'duplicate',
            'password': 'password456',
            'email': 'duplicate2@example.com'
        })

        assert response.status_code == 409


class TestLogin:
    """Test user login"""

    def test_login_success(self, client):
        """Test successful login"""
        # Register first
        client.post('/api/register', json={
            'username': 'loginuser',
            'password': 'password123',
            'email': 'login@example.com'
        })

        # Login
        response = client.post('/api/login', json={
            'username': 'loginuser',
            'password': 'password123'
        })

        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['token_type'] == 'Bearer'
        assert data['username'] == 'loginuser'

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/login', json={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post('/api/login', json={
            'username': 'testuser'
        })

        assert response.status_code == 400


class TestProtectedEndpoints:
    """Test protected endpoints that require authentication"""

    def test_protected_without_auth(self, client):
        """Test accessing protected endpoint without authentication"""
        response = client.get('/api/protected')
        assert response.status_code == 401

    def test_protected_with_auth(self, client, auth_headers):
        """Test accessing protected endpoint with valid authentication"""
        response = client.get('/api/protected', headers=auth_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'message' in data
        assert 'user' in data

    def test_user_info_without_auth(self, client):
        """Test getting user info without authentication"""
        response = client.get('/api/user/info')
        assert response.status_code == 401

    def test_user_info_with_auth(self, client, auth_headers):
        """Test getting user info with valid authentication"""
        response = client.get('/api/user/info', headers=auth_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['username'] == 'testuser'
        assert 'email' in data
        assert 'password' not in data  # Password should not be returned

    def test_update_user_without_auth(self, client):
        """Test updating user without authentication"""
        response = client.post('/api/user/update', json={
            'email': 'newemail@example.com'
        })
        assert response.status_code == 401

    def test_update_user_with_auth(self, client, auth_headers):
        """Test updating user with valid authentication"""
        response = client.post('/api/user/update',
                               json={'email': 'newemail@example.com'},
                               headers=auth_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['message'] == 'User updated successfully'


class TestErrorHandling:
    """Test error handling"""

    def test_404_error(self, client):
        """Test 404 error for non-existent endpoint"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data

    def test_405_error(self, client):
        """Test 405 error for wrong HTTP method"""
        response = client.get('/api/register')
        assert response.status_code == 405

        data = json.loads(response.data)
        assert 'error' in data


class TestSecurityFeatures:
    """Test security features"""

    def test_max_content_length(self, client):
        """Test that large uploads are rejected"""
        large_data = 'x' * (17 * 1024 * 1024)  # 17MB

        response = client.post('/api/register',
                               json={'username': large_data,
                                     'password': 'password123',
                                     'email': 'test@example.com'},
                               content_type='application/json')

        # Should be rejected due to size limit
        assert response.status_code in [400, 413]

    def test_json_content_type_required(self, client):
        """Test that JSON content type is required"""
        response = client.post('/api/register',
                               data='username=test&password=pass',
                               content_type='application/x-www-form-urlencoded')

        # Should handle gracefully
        assert response.status_code in [400, 415]
