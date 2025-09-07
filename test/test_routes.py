import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from fastapi.testclient import TestClient

from src.app import app
from src.crypto.utils import encrypt_password


class TestRoutes:
    """Test suite for routes package."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
        self.test_login = "testuser"
        self.test_password = "TestPassword123"
        self.test_password_hash = encrypt_password(self.test_password)
        self.test_user_id = 1

    @patch('src.routes.api.UsersDAO')
    def test_register_account_success(self, mock_users_dao_class):
        """Test successful user registration."""
        # Mock the UsersDAO context manager
        mock_dao = Mock()
        mock_users_dao_class.return_value.__enter__.return_value = mock_dao
        mock_users_dao_class.return_value.__exit__.return_value = None
        mock_dao.create_new_user.return_value = self.test_user_id

        # Create request data
        request_data = {
            "login": self.test_login,
            "password": self.test_password
        }

        # Make request
        response = self.client.post("/register", json=request_data)

        # Assertions
        assert response.status_code == 201
        assert response.json() == {"id": self.test_user_id}
        
        # Verify DAO methods were called correctly
        # The password should be hashed with bcrypt, so we can't predict the exact hash
        # Instead, verify it was called with the correct login and a hash
        call_args = mock_dao.create_new_user.call_args
        assert call_args[0][0] == self.test_login  # login
        assert isinstance(call_args[0][1], str)  # password hash
        assert call_args[0][1].startswith('$2b$')  # bcrypt format
        assert len(call_args[0][1]) == 60  # bcrypt hash length
        mock_users_dao_class.assert_called_once()

    @patch('src.routes.api.UsersDAO')
    def test_register_account_database_error(self, mock_users_dao_class):
        """Test user registration with database error."""
        # Mock the UsersDAO context manager
        mock_dao = Mock()
        mock_users_dao_class.return_value.__enter__.return_value = mock_dao
        mock_users_dao_class.return_value.__exit__.return_value = None
        mock_dao.create_new_user.side_effect = Exception("Database error")

        # Create request data
        request_data = {
            "login": self.test_login,
            "password": self.test_password
        }

        # Make request
        with pytest.raises(Exception) as exc_info:
            self.client.post("/register", json=request_data)
        
        # Assertions
        assert "Database error" in str(exc_info.value)

    @patch('src.routes.api.UsersDAO')
    def test_login_account_success(self, mock_users_dao_class):
        """Test successful user login."""
        # Mock the UsersDAO context manager
        mock_dao = Mock()
        mock_users_dao_class.return_value.__enter__.return_value = mock_dao
        mock_users_dao_class.return_value.__exit__.return_value = None
        
        # Mock user data
        mock_user = {
            "id": self.test_user_id,
            "login": self.test_login,
            "password_hash": self.test_password_hash,
            "created_at": datetime.now().isoformat()
        }
        mock_dao.get_user_by_login.return_value = mock_user
        mock_dao.update_user.return_value = True

        # Create request data
        request_data = {
            "login": self.test_login,
            "password": self.test_password
        }

        # Make request
        response = self.client.post("/login", json=request_data)

        # Assertions
        assert response.status_code == 201
        assert response.json() == {"message": "Login successful"}
        
        # Verify DAO methods were called correctly
        mock_dao.get_user_by_login.assert_called_once_with(self.test_login)
        mock_dao.update_user.assert_called_once()
        # Check that update_user was called with correct parameters
        call_args = mock_dao.update_user.call_args
        assert call_args[1]['user_id'] == self.test_user_id
        assert call_args[1]['last_login'] is not None

    @patch('src.routes.api.UsersDAO')
    def test_login_account_user_not_found(self, mock_users_dao_class):
        """Test login with non-existent user."""
        # Mock the UsersDAO context manager
        mock_dao = Mock()
        mock_users_dao_class.return_value.__enter__.return_value = mock_dao
        mock_users_dao_class.return_value.__exit__.return_value = None
        mock_dao.get_user_by_login.return_value = None

        # Create request data
        request_data = {
            "login": "nonexistent",
            "password": self.test_password
        }

        # Make request
        response = self.client.post("/login", json=request_data)

        # Assertions
        assert response.status_code == 401
        assert response.json() == {"message": "Invalid credentials"}
        
        # Verify DAO methods were called correctly
        mock_dao.get_user_by_login.assert_called_once_with("nonexistent")
        mock_dao.update_user.assert_not_called()

    @patch('src.routes.api.UsersDAO')
    def test_login_account_incorrect_password(self, mock_users_dao_class):
        """Test login with incorrect password."""
        # Mock the UsersDAO context manager
        mock_dao = Mock()
        mock_users_dao_class.return_value.__enter__.return_value = mock_dao
        mock_users_dao_class.return_value.__exit__.return_value = None
        
        # Mock user data with different password hash
        mock_user = {
            "id": self.test_user_id,
            "login": self.test_login,
            "password_hash": encrypt_password("DifferentPassword123"),
            "created_at": datetime.now().isoformat()
        }
        mock_dao.get_user_by_login.return_value = mock_user

        # Create request data
        request_data = {
            "login": self.test_login,
            "password": self.test_password
        }

        # Make request
        response = self.client.post("/login", json=request_data)

        # Assertions
        assert response.status_code == 401
        assert response.json() == {"message": "Invalid credentials"}
        
        # Verify DAO methods were called correctly
        mock_dao.get_user_by_login.assert_called_once_with(self.test_login)
        mock_dao.update_user.assert_not_called()

    @patch('src.routes.api.UsersDAO')
    def test_delete_account_success(self, mock_users_dao_class):
        """Test successful user deletion."""
        # Mock the UsersDAO context manager
        mock_dao = Mock()
        mock_users_dao_class.return_value.__enter__.return_value = mock_dao
        mock_users_dao_class.return_value.__exit__.return_value = None
        
        # Mock user data
        mock_user = {
            "id": self.test_user_id,
            "login": self.test_login,
            "password_hash": self.test_password_hash,
            "created_at": datetime.now().isoformat()
        }
        mock_dao.get_user_by_login.return_value = mock_user
        mock_dao.delete_user.return_value = True

        # Create request data
        request_data = {
            "login": self.test_login,
            "password": self.test_password
        }

        # Make request
        response = self.client.post("/delete", json=request_data)

        # Assertions
        assert response.status_code == 200
        assert response.json() == {"message": "User deleted successfully"}
        
        # Verify DAO methods were called correctly
        mock_dao.get_user_by_login.assert_called_once_with(self.test_login)
        mock_dao.delete_user.assert_called_once_with(self.test_user_id)

    @patch('src.routes.api.UsersDAO')
    def test_delete_account_user_not_found(self, mock_users_dao_class):
        """Test deletion of non-existent user."""
        # Mock the UsersDAO context manager
        mock_dao = Mock()
        mock_users_dao_class.return_value.__enter__.return_value = mock_dao
        mock_users_dao_class.return_value.__exit__.return_value = None
        mock_dao.get_user_by_login.return_value = None

        # Create request data
        request_data = {
            "login": "nonexistent",
            "password": self.test_password
        }

        # Make request
        response = self.client.post("/delete", json=request_data)

        # Assertions
        assert response.status_code == 401
        assert response.json() == {"message": "Invalid credentials"}
        
        # Verify DAO methods were called correctly
        mock_dao.get_user_by_login.assert_called_once_with("nonexistent")
        mock_dao.delete_user.assert_not_called()

    @patch('src.routes.api.UsersDAO')
    def test_delete_account_incorrect_password(self, mock_users_dao_class):
        """Test deletion with incorrect password."""
        # Mock the UsersDAO context manager
        mock_dao = Mock()
        mock_users_dao_class.return_value.__enter__.return_value = mock_dao
        mock_users_dao_class.return_value.__exit__.return_value = None
        
        # Mock user data with different password hash
        mock_user = {
            "id": self.test_user_id,
            "login": self.test_login,
            "password_hash": encrypt_password("DifferentPassword123"),
            "created_at": datetime.now().isoformat()
        }
        mock_dao.get_user_by_login.return_value = mock_user

        # Create request data
        request_data = {
            "login": self.test_login,
            "password": self.test_password
        }

        # Make request
        response = self.client.post("/delete", json=request_data)

        # Assertions
        assert response.status_code == 401
        assert response.json() == {"message": "Invalid credentials"}
        
        # Verify DAO methods were called correctly
        mock_dao.get_user_by_login.assert_called_once_with(self.test_login)
        mock_dao.delete_user.assert_not_called()

    @patch('src.routes.api.UsersDAO')
    def test_delete_account_database_error(self, mock_users_dao_class):
        """Test user deletion with database error."""
        # Mock the UsersDAO context manager
        mock_dao = Mock()
        mock_users_dao_class.return_value.__enter__.return_value = mock_dao
        mock_users_dao_class.return_value.__exit__.return_value = None
        
        # Mock user data
        mock_user = {
            "id": self.test_user_id,
            "login": self.test_login,
            "password_hash": self.test_password_hash,
            "created_at": datetime.now().isoformat()
        }
        mock_dao.get_user_by_login.return_value = mock_user
        mock_dao.delete_user.side_effect = Exception("Database error")

        # Create request data
        request_data = {
            "login": self.test_login,
            "password": self.test_password
        }

        # Make request
        with pytest.raises(Exception) as exc_info:
            self.client.post("/delete", json=request_data)
        
        # Assertions
        assert "Database error" in str(exc_info.value)

    def test_register_account_invalid_data(self):
        """Test registration with invalid DTO data."""
        # Test with empty login
        request_data = {
            "login": "",
            "password": self.test_password
        }
        response = self.client.post("/register", json=request_data)
        assert response.status_code == 422

        # Test with short login
        request_data = {
            "login": "ab",
            "password": self.test_password
        }
        response = self.client.post("/register", json=request_data)
        assert response.status_code == 422

        # Test with empty password
        request_data = {
            "login": self.test_login,
            "password": ""
        }
        response = self.client.post("/register", json=request_data)
        assert response.status_code == 422

        # Test with short password
        request_data = {
            "login": self.test_login,
            "password": "short"
        }
        response = self.client.post("/register", json=request_data)
        assert response.status_code == 422

    def test_login_account_invalid_data(self):
        """Test login with invalid DTO data."""
        # Test with empty login
        request_data = {
            "login": "",
            "password": self.test_password
        }
        response = self.client.post("/login", json=request_data)
        assert response.status_code == 422

        # Test with invalid password (no uppercase)
        request_data = {
            "login": self.test_login,
            "password": "lowercase123"
        }
        response = self.client.post("/login", json=request_data)
        assert response.status_code == 422

    def test_delete_account_invalid_data(self):
        """Test deletion with invalid DTO data."""
        # Test with empty login
        request_data = {
            "login": "",
            "password": self.test_password
        }
        response = self.client.post("/delete", json=request_data)
        assert response.status_code == 422

        # Test with invalid password (no digit)
        request_data = {
            "login": self.test_login,
            "password": "NoDigitsHere"
        }
        response = self.client.post("/delete", json=request_data)
        assert response.status_code == 422

    @patch('src.routes.api.verify_password')
    def test_password_verification_integration(self, mock_verify_password):
        """Test that passwords are properly verified in all endpoints."""
        mock_verify_password.return_value = True
        
        # Mock UsersDAO
        with patch('src.routes.api.UsersDAO') as mock_users_dao_class:
            mock_dao = Mock()
            mock_users_dao_class.return_value.__enter__.return_value = mock_dao
            mock_users_dao_class.return_value.__exit__.return_value = None
            
            # Setup mock responses
            mock_dao.create_new_user.return_value = self.test_user_id
            mock_user = {
                "id": self.test_user_id,
                "login": self.test_login,
                "password_hash": "hashed_password",
                "created_at": datetime.now().isoformat()
            }
            mock_dao.get_user_by_login.return_value = mock_user
            mock_dao.update_user.return_value = True
            mock_dao.delete_user.return_value = True

            # Test register
            request_data = {
                "login": self.test_login,
                "password": self.test_password
            }
            
            response = self.client.post("/register", json=request_data)
            assert response.status_code == 201
            # verify_password is not called in register, only encrypt_password
            
            # Test login
            response = self.client.post("/login", json=request_data)
            assert response.status_code == 201
            mock_verify_password.assert_called_once_with(self.test_password, "hashed_password")
            
            # Test delete
            response = self.client.post("/delete", json=request_data)
            assert response.status_code == 200
            # verify_password should be called twice (login and delete)
            assert mock_verify_password.call_count == 2

    def test_information_disclosure_prevention(self):
        """Test that error messages don't reveal user existence."""
        # Test with valid DTO data but non-existent user
        request_data = {
            "login": "nonexistent_user",
            "password": "ValidPass123"  # Valid password format
        }
        
        # Test login with non-existent user
        with patch('src.routes.api.UsersDAO') as mock_users_dao_class:
            mock_dao = Mock()
            mock_users_dao_class.return_value.__enter__.return_value = mock_dao
            mock_users_dao_class.return_value.__exit__.return_value = None
            mock_dao.get_user_by_login.return_value = None
            
            response = self.client.post("/login", json=request_data)
            assert response.status_code == 401
            assert response.json() == {"message": "Invalid credentials"}
        
        # Test delete with non-existent user
        with patch('src.routes.api.UsersDAO') as mock_users_dao_class:
            mock_dao = Mock()
            mock_users_dao_class.return_value.__enter__.return_value = mock_dao
            mock_users_dao_class.return_value.__exit__.return_value = None
            mock_dao.get_user_by_login.return_value = None
            
            response = self.client.post("/delete", json=request_data)
            assert response.status_code == 401
            assert response.json() == {"message": "Invalid credentials"}
        
        # Both should return the same error message regardless of user existence