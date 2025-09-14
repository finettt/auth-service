import unittest.mock
from fastapi.testclient import TestClient
from src.app import app
from src.routes.api import get_current_user

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == "Healthy"


def test_register_account():
    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_dao:
        mock_dao.return_value.__enter__.return_value.create_new_user.return_value = 1
        response = client.post("/api/register", json={"login": "testuser", "password": "TestPassword1"})
        assert response.status_code == 201
        assert response.json() == {"id": 1}


def test_login_account_success():
    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_dao:
        mock_dao.return_value.__enter__.return_value.get_user_by_login.return_value = {
            "id": 1,
            "login": "testuser",
            "password_hash": "$2b$12$EixZaYVK1e.1O6b.dY.qfe.8.G.i.O.Z.a.z.a.z.a.z.a"  # pragma: allowlist secret
        }
        with unittest.mock.patch("src.routes.api.verify_password") as mock_verify_password:
            mock_verify_password.return_value = True
            with unittest.mock.patch("src.routes.api.TokensDAO") as mock_token_dao:
                mock_token_dao.return_value.__enter__.return_value.store_token.return_value = None
                response = client.post("/api/login", json={"login": "testuser", "password": "TestPassword1"})
                assert response.status_code == 200
                assert "access_token" in response.json()
                assert response.json()["token_type"] == "bearer"


def test_login_account_failure():
    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_dao:
        mock_dao.return_value.__enter__.return_value.get_user_by_login.return_value = None
        response = client.post("/api/login", json={"login": "testuser", "password": "TestPassword1"})
        assert response.status_code == 401
        assert response.json() == {"message": "Invalid credentials"}


def test_logout_account():
    with unittest.mock.patch("src.routes.api.TokensDAO") as mock_token_dao:
        mock_token_dao.return_value.__enter__.return_value.delete_token.return_value = True
        response = client.post("/api/logout", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200
        assert response.json() == {"message": "Successfully logged out"}


def test_delete_account():
    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_user_dao:
        mock_user_dao.return_value.__enter__.return_value.get_user_by_login.return_value = {
            "id": 1,
            "login": "testuser",
            "password_hash": "$2b$12$EixZaYVK1e.1O6b.dY.qfe.8.G.i.O.Z.a.z.a.z.a.z.a"  # pragma: allowlist secret
        }
        with unittest.mock.patch("src.routes.api.verify_password") as mock_verify_password:
            mock_verify_password.return_value = True
            with unittest.mock.patch("src.routes.api.TokensDAO") as mock_token_dao:
                mock_token_dao.return_value.__enter__.return_value.revoke_user_tokens.return_value = None
                mock_user_dao.return_value.__enter__.return_value.delete_user.return_value = None
                response = client.post("/api/delete", json={"login": "testuser", "password": "TestPassword1"})
                assert response.status_code == 200
                assert response.json() == {"message": "User deleted successfully"}



def test_get_profile():
    def mock_get_current_user():
        return {"user_id": 1, "login": "testuser"}

    app.dependency_overrides[get_current_user] = mock_get_current_user

    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_user_dao:
        mock_user_dao.return_value.__enter__.return_value.get_user_by_id.return_value = {
            "id": 1,
            "login": "testuser",
            "last_login": "2023-01-01T00:00:00"
        }
        response = client.get("/api/profile", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200
        assert response.json() == {"id": 1, "login": "testuser", "last_login": "2023-01-01T00:00:00"}

    app.dependency_overrides = {}
