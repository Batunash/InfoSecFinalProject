"""
DevSecOps Sample Application
A simple Flask application demonstrating security best practices
"""

import os
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from auth import hash_password, verify_password, validate_input
from utils import sanitize_output, log_security_event

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Initialize JWT
jwt = JWTManager(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory user storage (for demo purposes - use a real database in production)
users_db = {}

# HTML template for the home page
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DevSecOps Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .success { color: #27ae60; }
        .error { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DevSecOps Sample Application</h1>
            <p>Information Security - SENG 473 Final Project</p>
        </div>
        <div class="section">
            <h2>Available Endpoints</h2>
            <ul>
                <li>POST /api/register - Register a new user</li>
                <li>POST /api/login - Login and get JWT token</li>
                <li>GET /api/protected - Protected endpoint (requires JWT)</li>
                <li>GET /api/user/info - Get user information (requires JWT)</li>
                <li>POST /api/user/update - Update user information (requires JWT)</li>
                <li>GET /health - Health check endpoint</li>
            </ul>
        </div>
        <div class="section">
            <h2>Security Features</h2>
            <ul>
                <li>JWT-based authentication</li>
                <li>Password hashing with bcrypt</li>
                <li>Input validation and sanitization</li>
                <li>Output encoding</li>
                <li>Security event logging</li>
                <li>Rate limiting (recommended)</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def home():
    """Home page with API documentation"""
    return render_template_string(HOME_TEMPLATE)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'devsecops-app',
        'version': '1.0.0'
    }), 200


@app.route('/api/register', methods=['POST'])
def register():
    """
    Register a new user
    Expected JSON: { "username": "string", "password": "string", "email": "string" }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        # Validate input
        if not all([username, password, email]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate username
        if not validate_input(username, 'username'):
            return jsonify({'error': 'Invalid username format'}), 400

        # Validate email
        if not validate_input(email, 'email'):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if user already exists
        if username in users_db:
            return jsonify({'error': 'User already exists'}), 409

        # Hash password
        hashed_password = hash_password(password)

        # Store user
        users_db[username] = {
            'password': hashed_password,
            'email': email,
            'created_at': str(os.times())
        }

        log_security_event('USER_REGISTERED', {'username': username})

        return jsonify({
            'message': 'User registered successfully',
            'username': username
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """
    Login and get JWT token
    Expected JSON: { "username": "string", "password": "string" }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return jsonify({'error': 'Missing credentials'}), 400

        # Check if user exists
        if username not in users_db:
            log_security_event('LOGIN_FAILED', {'username': username, 'reason': 'User not found'})
            return jsonify({'error': 'Invalid credentials'}), 401

        # Verify password
        if not verify_password(password, users_db[username]['password']):
            log_security_event('LOGIN_FAILED', {'username': username, 'reason': 'Invalid password'})
            return jsonify({'error': 'Invalid credentials'}), 401

        # Create access token
        access_token = create_access_token(identity=username)

        log_security_event('LOGIN_SUCCESS', {'username': username})

        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'username': username
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    """Protected endpoint that requires JWT authentication"""
    try:
        current_user = get_jwt_identity()
        return jsonify({
            'message': f'Hello {current_user}! You have accessed a protected endpoint.',
            'user': current_user
        }), 200
    except Exception as e:
        logger.error(f"Protected endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/user/info', methods=['GET'])
@jwt_required()
def get_user_info():
    """Get current user information"""
    try:
        current_user = get_jwt_identity()

        if current_user not in users_db:
            return jsonify({'error': 'User not found'}), 404

        user_data = users_db[current_user].copy()
        # Remove sensitive data
        user_data.pop('password', None)

        return jsonify({
            'username': current_user,
            'email': user_data.get('email'),
            'created_at': user_data.get('created_at')
        }), 200

    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/user/update', methods=['POST'])
@jwt_required()
def update_user():
    """
    Update user information
    Expected JSON: { "email": "string" }
    """
    try:
        current_user = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        if current_user not in users_db:
            return jsonify({'error': 'User not found'}), 404

        # Update email if provided
        if 'email' in data:
            email = data['email']
            if not validate_input(email, 'email'):
                return jsonify({'error': 'Invalid email format'}), 400
            users_db[current_user]['email'] = email

        log_security_event('USER_UPDATED', {'username': current_user})

        return jsonify({
            'message': 'User updated successfully',
            'username': current_user
        }), 200

    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Note: In production, use a WSGI server like Gunicorn or uWSGI
    # and set debug=False
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
