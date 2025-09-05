import unittest
import uuid
from src.database.dao.users import UsersDAO


class UsersDAOTest(unittest.TestCase):
    
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
    
    def _create_test_user(self, email: str | None = None, password_hash: str | None = None) -> int:
        """Helper method to create a test user and track it for cleanup."""
        if email is None:
            email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        if password_hash is None:
            password_hash = "test_password_hash"
        
        with UsersDAO() as dao:
            user_id = dao.create_new_user(email, password_hash)
            self.test_users.append(user_id)
            return user_id

    def test_1_enter_exit(self):
        """Test that DAO connection and cursor are properly initialized."""
        with UsersDAO() as dao:
            self.assertIsNotNone(dao.conn)
            self.assertIsNotNone(dao.cur)

    def test_2_create_user(self):
        """Test creating a new user."""
        user_id = self._create_test_user("test_create@example.com", "password_hash")
        self.assertIsNotNone(user_id)

    def test_3_get_all_users(self):
        """Test getting all users."""
        self._create_test_user("test_get_all@example.com", "password_hash")
        
        with UsersDAO() as dao:
            users = dao.get_all_users()
            self.assertIsNotNone(users)
            self.assertIsInstance(users, list)

    def test_4_get_user_by_id(self):
        """Test getting a user by ID."""
        user_id = self._create_test_user("test_by_id@example.com", "password_hash")
        
        with UsersDAO() as dao:
            user = dao.get_user_by_id(user_id)
            self.assertIsNotNone(user)
            self.assertEqual(user["email"], "test_by_id@example.com") # type: ignore

    def test_5_get_user_by_email(self):
        """Test getting a user by email."""
        email = "test_by_email@example.com"
        user_id = self._create_test_user(email, "password_hash")
        
        with UsersDAO() as dao:
            user = dao.get_user_by_email(email)
            self.assertIsNotNone(user)
            self.assertEqual(user["id"], user_id) # type: ignore

    def test_6_update_user(self):
        """Test updating a user."""
        user_id = self._create_test_user("test_update@example.com", "old_password")
        
        with UsersDAO() as dao:
            success = dao.update_user(user_id, "updated_email@example.com", "new_password")
            self.assertTrue(success)
            
            updated_user = dao.get_user_by_id(user_id)
            self.assertIsNotNone(updated_user)
            self.assertEqual(updated_user["email"], "updated_email@example.com") # type: ignore
            self.assertEqual(updated_user["password_hash"], "new_password") # type: ignore

    def test_7_delete_user(self):
        """Test deleting a user."""
        user_id = self._create_test_user("test_delete@example.com", "password_hash")
        
        with UsersDAO() as dao:
            is_deleted = dao.delete_user(user_id)
            self.assertTrue(is_deleted)
            
            # Verify user is actually deleted
            deleted_user = dao.get_user_by_id(user_id)
            self.assertIsNone(deleted_user)

    def test_8_init_method(self):
        """Test UsersDAO initialization."""
        dao = UsersDAO()
        self.assertIsNone(dao.conn)
        self.assertIsNone(dao.cur)

    def test_9_update_user_both_none(self):
        """Test update_user when both email and password_hash are None."""
        user_id = self._create_test_user("test_both_none@example.com", "password_hash")
        
        with UsersDAO() as dao:
            result = dao.update_user(user_id, None, None)
            self.assertFalse(result)

    def test_10_update_user_only_email(self):
        """Test update_user when only email is provided."""
        user_id = self._create_test_user("test_only_email@example.com", "old_password")
        
        with UsersDAO() as dao:
            success = dao.update_user(user_id, "updated_email@example.com", None)
            self.assertTrue(success)
            
            updated_user = dao.get_user_by_id(user_id)
            self.assertIsNotNone(updated_user)
            self.assertEqual(updated_user["email"], "updated_email@example.com") # type: ignore
            self.assertEqual(updated_user["password_hash"], "old_password") # type: ignore

    def test_11_update_user_only_password(self):
        """Test update_user when only password_hash is provided."""
        user_id = self._create_test_user("test_only_password@example.com", "old_password")
        
        with UsersDAO() as dao:
            success = dao.update_user(user_id, None, "new_password_hash")
            self.assertTrue(success)
            
            updated_user = dao.get_user_by_id(user_id)
            self.assertIsNotNone(updated_user)
            self.assertEqual(updated_user["email"], "test_only_password@example.com") # type: ignore
            self.assertEqual(updated_user["password_hash"], "new_password_hash") # type: ignore

    def test_12_get_user_by_id_nonexistent(self):
        """Test get_user_by_id with non-existent user ID."""
        with UsersDAO() as dao:
            user = dao.get_user_by_id(999999)
            self.assertIsNone(user)

    def test_13_get_user_by_email_nonexistent(self):
        """Test get_user_by_email with non-existent email."""
        with UsersDAO() as dao:
            user = dao.get_user_by_email("nonexistent@example.com")
            self.assertIsNone(user)

    def test_14_delete_user_nonexistent(self):
        """Test delete_user with non-existent user ID."""
        with UsersDAO() as dao:
            result = dao.delete_user(999999)
            self.assertFalse(result)

    def test_15_get_all_users_empty(self):
        """Test get_all_users when no users exist."""
        with UsersDAO() as dao:
            users = dao.get_all_users()
            self.assertIsInstance(users, list)
            self.assertEqual(len(users), 0)
