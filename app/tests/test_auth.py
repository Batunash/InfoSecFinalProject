"""
Unit tests for authentication utilities
"""

import pytest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth import (
    hash_password,
    verify_password,
    validate_input,
    is_strong_password,
    generate_token,
    verify_token
)


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password(self):
        """Test that password hashing works"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long

    def test_hash_password_empty(self):
        """Test that empty password raises error"""
        with pytest.raises(ValueError):
            hash_password("")

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Test password verification with empty values"""
        hashed = hash_password("testpassword")

        assert verify_password("", hashed) is False
        assert verify_password("test", "") is False
        assert verify_password("", "") is False

    def test_hash_different_passwords(self):
        """Test that different passwords produce different hashes"""
        password1 = "password123"
        password2 = "password456"

        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        assert hash1 != hash2

    def test_hash_same_password_different_salts(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "samepassword"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestInputValidation:
    """Test input validation"""

    def test_validate_username_valid(self):
        """Test valid username validation"""
        assert validate_input("testuser", "username") is True
        assert validate_input("user123", "username") is True
        assert validate_input("test_user", "username") is True
        assert validate_input("User123", "username") is True

    def test_validate_username_invalid(self):
        """Test invalid username validation"""
        assert validate_input("", "username") is False
        assert validate_input("ab", "username") is False  # Too short
        assert validate_input("user with spaces", "username") is False
        assert validate_input("user@domain", "username") is False
        assert validate_input("user!", "username") is False
        assert validate_input(None, "username") is False

    def test_validate_email_valid(self):
        """Test valid email validation"""
        assert validate_input("test@example.com", "email") is True
        assert validate_input("user.name@domain.co.uk", "email") is True
        assert validate_input("user+tag@example.org", "email") is True

    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        assert validate_input("", "email") is False
        assert validate_input("invalid", "email") is False
        assert validate_input("@example.com", "email") is False
        assert validate_input("user@", "email") is False
        assert validate_input("user@domain", "email") is False
        assert validate_input(None, "email") is False

    def test_validate_password(self):
        """Test password validation"""
        assert validate_input("password123", "password") is True
        assert validate_input("12345678", "password") is True
        assert validate_input("short", "password") is False
        assert validate_input("", "password") is False

    def test_validate_unknown_type(self):
        """Test validation with unknown type"""
        assert validate_input("test", "unknown") is False


class TestStrongPassword:
    """Test strong password checking"""

    def test_strong_password(self):
        """Test that strong password passes"""
        password = "StrongP@ssw0rd123"
        is_strong, issues = is_strong_password(password)

        assert is_strong is True
        assert len(issues) == 0

    def test_weak_password_too_short(self):
        """Test that short password fails"""
        password = "Short1!"
        is_strong, issues = is_strong_password(password)

        assert is_strong is False
        assert any("12 characters" in issue for issue in issues)

    def test_weak_password_no_uppercase(self):
        """Test that password without uppercase fails"""
        password = "lowercase123!"
        is_strong, issues = is_strong_password(password)

        assert is_strong is False
        assert any("uppercase" in issue for issue in issues)

    def test_weak_password_no_lowercase(self):
        """Test that password without lowercase fails"""
        password = "UPPERCASE123!"
        is_strong, issues = is_strong_password(password)

        assert is_strong is False
        assert any("lowercase" in issue for issue in issues)

    def test_weak_password_no_digit(self):
        """Test that password without digit fails"""
        password = "NoDigitsHere!"
        is_strong, issues = is_strong_password(password)

        assert is_strong is False
        assert any("digit" in issue for issue in issues)

    def test_weak_password_no_special(self):
        """Test that password without special character fails"""
        password = "NoSpecialChars123"
        is_strong, issues = is_strong_password(password)

        assert is_strong is False
        assert any("special" in issue for issue in issues)


class TestTokenGeneration:
    """Test token generation and verification"""

    def test_generate_token(self):
        """Test token generation"""
        user_id = "testuser"
        secret = "test-secret"
        token = generate_token(user_id, secret)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """Test token verification with valid token"""
        user_id = "testuser"
        secret = "test-secret"
        token = generate_token(user_id, secret)

        verified_id = verify_token(token, secret)

        assert verified_id == user_id

    def test_verify_token_invalid_secret(self):
        """Test token verification with wrong secret"""
        user_id = "testuser"
        secret = "test-secret"
        wrong_secret = "wrong-secret"
        token = generate_token(user_id, secret)

        verified_id = verify_token(token, wrong_secret)

        assert verified_id is None

    def test_verify_token_expired(self):
        """Test token verification with expired token"""
        user_id = "testuser"
        secret = "test-secret"
        # Generate token with 0 expiry (already expired)
        token = generate_token(user_id, secret, expiry=0)

        verified_id = verify_token(token, secret)

        assert verified_id is None

    def test_verify_token_malformed(self):
        """Test token verification with malformed token"""
        secret = "test-secret"

        assert verify_token("", secret) is None
        assert verify_token("invalid", secret) is None
        assert verify_token("a:b", secret) is None
