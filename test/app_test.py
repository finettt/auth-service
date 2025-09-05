import unittest
import httpx
import uuid
from src.database.dao.users import UsersDAO

BASE_URL = "http://127.1:8000"


def get_payload():
    return {
        "email": "TestUser123",
        "password": "Te",
    }


class AppTest(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test."""
        self.test_users = []
    
    def tearDown(self):
        """Clean up test users after each test."""
        with UsersDAO() as dao:
            for user_id in self.test_users:
                try:
                    dao.delete_user(user_id)
                except Exception:
                    pass
        self.test_users.clear()
    
    def _create_test_user(self, email: str | None = None, password: str | None = None) -> dict:
        """Helper method to create a test user and track it for cleanup."""
        if email is None:
            email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        if password is None:
            password = "test_password"
        
        payload = {"email": email, "password": password}
        res = httpx.post(BASE_URL + "/register", json=payload)
        
        if res.status_code == 201:
            user_data = res.json()
            self.test_users.append(user_data["id"])
            return {"email": email, "password": password, "id": user_data["id"]}
        else:
            raise Exception(f"Failed to create test user: {res.status_code} - {res.json()}")
    def test_register(self):
        user = self._create_test_user()
        res = httpx.post(BASE_URL + "/login", json={"email": user["email"], "password": user["password"]})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json(), {"message": "Succes login"})

    def test_login_not_found(self):
        payload = {"email": "NotExists", "password": "123"}
        res = httpx.post(BASE_URL + "/login", json=payload)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json(), {"message": "User not found"})

    def test_login_incorrect_password(self):
        user = self._create_test_user()
        payload = {
            "email": user["email"],
            "password": "WrongPassword",
        }
        res = httpx.post(BASE_URL + "/login", json=payload)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json(), {"message": "Password incorrect"})

    def test_login_success(self):
        user = self._create_test_user()
        res = httpx.post(BASE_URL + "/login", json={"email": user["email"], "password": user["password"]})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json(), {"message": "Succes login"})

    def test_delete_account_incorrect_password(self):
        user = self._create_test_user()
        payload = {
            "email": user["email"],
            "password": "WrongPassword",
        }
        res = httpx.post(BASE_URL + "/delete", json=payload)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json(), {"message": "Password incorrect"})

    def test_delete_account_not_found(self):
        payload = {"email": "NotExists", "password": "123"}
        res = httpx.post(BASE_URL + "/delete", json=payload)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json(), {"message": "User not found"})

    def test_delete_account_success(self):
        user = self._create_test_user()
        payload = {"email": user["email"], "password": user["password"]}
        res = httpx.post(BASE_URL + "/delete", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"message": "User deleted"})
