import unittest.mock
import datetime
from fastapi.testclient import TestClient
from src.app import app
from src.routes.api import get_current_user

client = TestClient(app)


def test_register_account_with_encrypted_password():
    """Test register account with encrypted password."""
    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_dao_class:
        mock_dao = unittest.mock.MagicMock()
        mock_dao_class.return_value.__enter__.return_value = mock_dao
        mock_dao.create_new_user.return_value = 1
        
        with unittest.mock.patch("src.routes.api.encrypt_password") as mock_encrypt:
            mock_encrypt.return_value = "hashed_password"
            
            response = client.post("/api/register", json={"login": "testuser", "password": "TestPassword1"})
            assert response.status_code == 201
            assert response.json() == {"id": 1}
            
            # Verify that encrypt_password was called
            mock_encrypt.assert_called_once_with("TestPassword1")


def test_login_account_success_full_flow():
    """Test login account with full success flow."""
    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_dao_class:
        mock_dao = unittest.mock.MagicMock()
        mock_dao_class.return_value.__enter__.return_value = mock_dao
        mock_dao.get_user_by_login.return_value = {
            "id": 1,
            "login": "testuser",
            "password_hash": "$2b$12$EixZaYVK1e.1O6b.dY.qfe.8.G.i.O.Z.a.z.a.z.a.z.a"
        }
        mock_dao.update_user.return_value = True
        
        with unittest.mock.patch("src.routes.api.verify_password") as mock_verify_password:
            mock_verify_password.return_value = True
            
            with unittest.mock.patch("src.routes.api.TokensDAO") as mock_token_dao_class:
                mock_token_dao = unittest.mock.MagicMock()
                mock_token_dao_class.return_value.__enter__.return_value = mock_token_dao
                mock_token_dao.store_token.return_value = True
                
                with unittest.mock.patch("src.routes.api.jwt.encode") as mock_jwt_encode:
                    mock_jwt_encode.return_value = "test_token"
                    
                    with unittest.mock.patch("src.routes.api.settings") as mock_settings:
                        mock_settings.SECRET_KEY = "test_secret_key"
                        
                        response = client.post("/api/login", json={"login": "testuser", "password": "TestPassword1"})
                        assert response.status_code == 200
                        assert "access_token" in response.json()
                        assert response.json()["token_type"] == "bearer"


def test_login_account_with_update_user_failure():
    """Test login account when update_user fails."""
    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_dao_class:
        mock_dao = unittest.mock.MagicMock()
        mock_dao_class.return_value.__enter__.return_value = mock_dao
        mock_dao.get_user_by_login.return_value = {
            "id": 1,
            "login": "testuser",
            "password_hash": "$2b$12$EixZaYVK1e.1O6b.dY.qfe.8.G.i.O.Z.a.z.a.z.a.z.a"
        }
        mock_dao.update_user.return_value = False
        
        with unittest.mock.patch("src.routes.api.verify_password") as mock_verify_password:
            mock_verify_password.return_value = True
            
            with unittest.mock.patch("src.routes.api.TokensDAO") as mock_token_dao_class:
                mock_token_dao = unittest.mock.MagicMock()
                mock_token_dao_class.return_value.__enter__.return_value = mock_token_dao
                mock_token_dao.store_token.return_value = True
                
                with unittest.mock.patch("src.routes.api.jwt.encode") as mock_jwt_encode:
                    mock_jwt_encode.return_value = "test_token"
                    
                    with unittest.mock.patch("src.routes.api.settings") as mock_settings:
                        mock_settings.SECRET_KEY = "test_secret_key"
                        
                        response = client.post("/api/login", json={"login": "testuser", "password": "TestPassword1"})
                        assert response.status_code == 200
                        assert "access_token" in response.json()


def test_delete_account_with_revoke_tokens_failure():
    """Test delete account when revoking tokens fails."""
    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_user_dao_class:
        mock_user_dao = unittest.mock.MagicMock()
        mock_user_dao_class.return_value.__enter__.return_value = mock_user_dao
        mock_user_dao.get_user_by_login.return_value = {
            "id": 1,
            "login": "testuser",
            "password_hash": "$2b$12$EixZaYVK1e.1O6b.dY.qfe.8.G.i.O.Z.a.z.a.z.a.z.a"
        }
        mock_user_dao.delete_user.return_value = True
        
        with unittest.mock.patch("src.routes.api.verify_password") as mock_verify_password:
            mock_verify_password.return_value = True
            
            with unittest.mock.patch("src.routes.api.TokensDAO") as mock_token_dao_class:
                mock_token_dao = unittest.mock.MagicMock()
                mock_token_dao_class.return_value.__enter__.return_value = mock_token_dao
                mock_token_dao.revoke_user_tokens.return_value = None  # Even if it fails, we continue
                
                response = client.post("/api/delete", json={"login": "testuser", "password": "TestPassword1"})
                assert response.status_code == 200
                assert response.json() == {"message": "User deleted successfully"}


def test_get_profile_with_password_hash_removal():
    """Test get profile ensures password_hash is removed from response."""
    def mock_get_current_user():
        return {"user_id": 1, "login": "testuser"}

    app.dependency_overrides[get_current_user] = mock_get_current_user

    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_user_dao:
        mock_user_dao.return_value.__enter__.return_value.get_user_by_id.return_value = {
            "id": 1,
            "login": "testuser",
            "password_hash": "$2b$12$EixZaYVK1e.1O6b.dY.qfe.8.G.i.O.Z.a.z.a.z.a.z.a",
            "last_login": "2023-01-01T00:00:00"
        }
        response = client.get("/api/profile", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200
        assert "password_hash" not in response.json()
        assert response.json() == {"id": 1, "login": "testuser", "last_login": "2023-01-01T00:00:00"}

    app.dependency_overrides = {}