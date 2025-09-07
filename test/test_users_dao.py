import pytest
import sqlite3
import tempfile
import os
from datetime import datetime
from unittest.mock import patch
import shutil

from src.database.dao.users import UsersDAO
from src.crypto.utils import encrypt_password


class TestUsersDAO:
    """Test suite for UsersDAO class."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        # Create a temporary directory for the database
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'test.db')
        
        # Create the database schema
        conn = sqlite3.connect(temp_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS "users" (
                "id" INTEGER NOT NULL UNIQUE,
                "login" VARCHAR UNIQUE,
                "password_hash" TEXT,
                "created_at" DATETIME,
                "last_login" DATETIME,
                PRIMARY KEY("id")
            )
        ''')
        conn.commit()
        conn.close()
        
        yield temp_path
        
        # Clean up
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def dao_with_db(self, temp_db):
        """Create a UsersDAO instance with a temporary database."""
        with patch('src.database.connection.DATABASE_PATH', temp_db):
            yield UsersDAO()

    def test_dao_context_manager(self, dao_with_db):
        """Test that UsersDAO can be used as a context manager."""
        with dao_with_db as dao:
            assert dao.conn is not None
            assert dao.cur is not None
            assert isinstance(dao.conn, sqlite3.Connection)
            assert isinstance(dao.cur, sqlite3.Cursor)

    def test_dao_context_manager_cleanup(self, dao_with_db):
        """Test that context manager properly cleans up resources."""
        dao = dao_with_db
        with dao:
            pass
        
        # Connection should be closed after context exit
        # Use try-except to check if connection is closed
        try:
            dao.conn.cursor()
            pytest.fail("Connection should be closed")
        except sqlite3.ProgrammingError:
            pass  # Expected - connection is closed
        
        # Cursor should be closed after context exit
        try:
            dao.cur.execute("SELECT 1")
            pytest.fail("Cursor should be closed")
        except (sqlite3.ProgrammingError, AttributeError):
            pass  # Expected - cursor is closed

    def test_create_new_user(self, dao_with_db):
        """Test creating a new user."""
        login = "testuser"
        password_hash = encrypt_password("test_password_123")
        
        with dao_with_db as dao:
            user_id = dao.create_new_user(login, password_hash)
            
            # Verify user ID is returned
            assert isinstance(user_id, int)
            assert user_id > 0
            
            # Verify user was actually created
            user = dao.get_user_by_id(user_id)
            assert user is not None
            assert user['login'] == login
            assert user['password_hash'] == password_hash
            assert 'created_at' in user
            assert user['created_at'] is not None
            
            # Verify the password hash is in bcrypt format
            assert user['password_hash'].startswith('$2b$')
            assert len(user['password_hash']) == 60

    def test_create_new_user_with_special_chars(self, dao_with_db):
        """Test creating a user with special characters in login."""
        login = "test.user@example.com"
        password_hash = encrypt_password("special_password_456")
        
        with dao_with_db as dao:
            user_id = dao.create_new_user(login, password_hash)
            
            assert isinstance(user_id, int)
            user = dao.get_user_by_id(user_id)
            assert user['login'] == login
            assert user['password_hash'].startswith('$2b$')

    def test_create_new_user_empty_login(self, dao_with_db):
        """Test creating a user with empty login."""
        login = ""
        password_hash = encrypt_password("empty_login_password_789")
        
        with dao_with_db as dao:
            user_id = dao.create_new_user(login, password_hash)
            
            assert isinstance(user_id, int)
            user = dao.get_user_by_id(user_id)
            assert user['login'] == login
            assert user['password_hash'].startswith('$2b$')

    def test_create_new_user_duplicate_login(self, dao_with_db):
        """Test creating a user with duplicate login (should fail)."""
        login = "duplicate_user"
        password_hash = encrypt_password("duplicate_password_000")
        
        with dao_with_db as dao:
            # Create first user
            dao.create_new_user(login, password_hash)
            
            # Try to create user with same login - should raise exception
            with pytest.raises(Exception):
                dao.create_new_user(login, password_hash)

    def test_get_user_by_id(self, dao_with_db):
        """Test getting a user by ID."""
        login = "get_by_id_user"
        password_hash = encrypt_password("get_by_id_password")
        
        with dao_with_db as dao:
            # Create user first
            user_id = dao.create_new_user(login, password_hash)
            
            # Get user by ID
            user = dao.get_user_by_id(user_id)
            
            assert user is not None
            assert user['id'] == user_id
            assert user['login'] == login
            assert user['password_hash'] == password_hash
            assert user['password_hash'].startswith('$2b$')

    def test_get_user_by_id_nonexistent(self, dao_with_db):
        """Test getting a non-existent user by ID."""
        with dao_with_db as dao:
            user = dao.get_user_by_id(99999)  # Non-existent ID
            
            assert user is None

    def test_get_user_by_login(self, dao_with_db):
        """Test getting a user by login."""
        login = "get_by_login_user"
        password_hash = encrypt_password("get_by_login_password")
        
        with dao_with_db as dao:
            # Create user first
            dao.create_new_user(login, password_hash)
            
            # Get user by login
            user = dao.get_user_by_login(login)
            
            assert user is not None
            assert user['login'] == login
            assert user['password_hash'] == password_hash
            assert user['password_hash'].startswith('$2b$')

    def test_get_user_by_login_nonexistent(self, dao_with_db):
        """Test getting a non-existent user by login."""
        with dao_with_db as dao:
            user = dao.get_user_by_login("nonexistent_user")
            
            assert user is None

    def test_get_all_users(self, dao_with_db):
        """Test getting all users."""
        users_data = [
            ("user1", encrypt_password("password1")),
            ("user2", encrypt_password("password2")),
            ("user3", encrypt_password("password3")),
        ]
        
        with dao_with_db as dao:
            # Create multiple users
            created_ids = []
            for login, password_hash in users_data:
                user_id = dao.create_new_user(login, password_hash)
                created_ids.append(user_id)
            
            # Get all users
            all_users = dao.get_all_users()
            
            assert len(all_users) == 3
            
            # Verify all created users are present
            for i, user in enumerate(all_users):
                assert user['login'] == users_data[i][0]
                assert user['password_hash'] == users_data[i][1]
                assert user['id'] in created_ids

    def test_get_all_users_empty(self, dao_with_db):
        """Test getting all users when no users exist."""
        with dao_with_db as dao:
            all_users = dao.get_all_users()
            
            assert all_users == []

    def test_update_user_login_only(self, dao_with_db):
        """Test updating only user login."""
        old_login = "old_login_user"
        new_login = "new_login_user"
        password_hash = encrypt_password("update_password")
        
        with dao_with_db as dao:
            # Create user
            user_id = dao.create_new_user(old_login, password_hash)
            
            # Update login only
            result = dao.update_user(user_id, login=new_login)
            
            assert result is True
            
            # Verify update
            user = dao.get_user_by_id(user_id)
            assert user['login'] == new_login
            assert user['password_hash'] == password_hash  # Unchanged
            assert user['password_hash'].startswith('$2b$')

    def test_update_user_password_only(self, dao_with_db):
        """Test updating only user password."""
        login = "password_update_user"
        old_password = encrypt_password("old_password")
        new_password = encrypt_password("new_password")
        
        with dao_with_db as dao:
            # Create user
            user_id = dao.create_new_user(login, old_password)
            
            # Update password only
            result = dao.update_user(user_id, password_hash=new_password)
            
            assert result is True
            
            # Verify update
            user = dao.get_user_by_id(user_id)
            assert user['login'] == login  # Unchanged
            assert user['password_hash'] == new_password
            assert user['password_hash'].startswith('$2b$')

    def test_update_user_last_login_only(self, dao_with_db):
        """Test updating only user last login."""
        login = "last_login_user"
        password_hash = "hashed_password_last_login"
        last_login = datetime.now()
        
        with dao_with_db as dao:
            # Create user
            user_id = dao.create_new_user(login, password_hash)
            
            # Update last login only
            result = dao.update_user(user_id, last_login=last_login)
            
            assert result is True
            
            # Verify update
            user = dao.get_user_by_id(user_id)
            assert user['login'] == login  # Unchanged
            assert user['password_hash'] == password_hash  # Unchanged
            # Convert datetime string back to datetime object for comparison
            stored_time = datetime.strptime(user['last_login'], '%Y-%m-%d %H:%M:%S.%f')
            assert stored_time == last_login

    def test_update_user_multiple_fields(self, dao_with_db):
        """Test updating multiple user fields."""
        old_login = "multi_update_old"
        new_login = "multi_update_new"
        old_password = encrypt_password("old_multi_password")
        new_password = encrypt_password("new_multi_password")
        last_login = datetime.now()
        
        with dao_with_db as dao:
            # Create user
            user_id = dao.create_new_user(old_login, old_password)
            
            # Update multiple fields
            result = dao.update_user(
                user_id,
                login=new_login,
                password_hash=new_password,
                last_login=last_login
            )
            
            assert result is True
            
            # Verify update
            user = dao.get_user_by_id(user_id)
            assert user['login'] == new_login
            assert user['password_hash'] == new_password
            assert user['password_hash'].startswith('$2b$')
            # Convert datetime string back to datetime object for comparison
            stored_time = datetime.strptime(user['last_login'], '%Y-%m-%d %H:%M:%S.%f')
            assert stored_time == last_login

    def test_update_user_no_changes(self, dao_with_db):
        """Test updating user with no changes."""
        login = "no_changes_user"
        password_hash = "hashed_no_changes"
        
        with dao_with_db as dao:
            # Create user
            user_id = dao.create_new_user(login, password_hash)
            
            # Try to update with no changes
            result = dao.update_user(user_id)
            
            assert result is False

    def test_update_user_nonexistent(self, dao_with_db):
        """Test updating a non-existent user."""
        with dao_with_db as dao:
            result = dao.update_user(99999, login="new_login")
            
            assert result is False

    def test_delete_user(self, dao_with_db):
        """Test deleting a user."""
        login = "delete_user"
        password_hash = encrypt_password("delete_user_password")
        
        with dao_with_db as dao:
            # Create user
            user_id = dao.create_new_user(login, password_hash)
            
            # Delete user
            result = dao.delete_user(user_id)
            
            assert result is True
            
            # Verify user is deleted
            user = dao.get_user_by_id(user_id)
            assert user is None
            
            # Verify not in all users
            all_users = dao.get_all_users()
            assert not any(u['id'] == user_id for u in all_users)

    def test_delete_user_nonexistent(self, dao_with_db):
        """Test deleting a non-existent user."""
        with dao_with_db as dao:
            result = dao.delete_user(99999)
            
            assert result is False

    def test_fetch_all_as_dicts(self, dao_with_db):
        """Test the internal _fetch_all_as_dicts method."""
        login = "fetch_dicts_user"
        password_hash = encrypt_password("fetch_dicts_password")
        
        with dao_with_db as dao:
            # Create user
            dao.create_new_user(login, password_hash)
            
            # Execute query and fetch as dicts
            dao.cur.execute("SELECT * FROM users")  # type: ignore
            result = dao._fetch_all_as_dicts()
            
            assert len(result) == 1
            assert isinstance(result[0], dict)
            assert result[0]['login'] == login
            assert result[0]['password_hash'] == password_hash
            assert result[0]['password_hash'].startswith('$2b$')

    def test_execute_query_with_params(self, dao_with_db):
        """Test the internal _execute_query method with parameters."""
        login = "execute_query_user"
        password_hash = encrypt_password("execute_query_password")
        
        with dao_with_db as dao:
            # Test execute with params
            dao._execute_query(
                "INSERT INTO users(login, password_hash, created_at) VALUES (?, ?, datetime('now'))",
                (login, password_hash)
            )
            
            # Verify insertion
            user = dao.get_user_by_login(login)
            assert user is not None
            assert user['login'] == login
            assert user['password_hash'].startswith('$2b$')

    def test_execute_query_without_params(self, dao_with_db):
        """Test the internal _execute_query method without parameters."""
        with dao_with_db as dao:
            # Test execute without params
            dao._execute_query("SELECT COUNT(*) as count FROM users")
            
            # Verify query executed
            result = dao.cur.fetchone()  # type: ignore
            # Check if result has the 'count' column by accessing by index
            assert len(result) == 1  # Should have one column
            assert result[0] is not None  # Should have a value

    def test_error_handling_in_dao(self, dao_with_db):
        """Test error handling in DAO methods."""
        with dao_with_db as dao:
            # Test with invalid SQL (should raise exception)
            with pytest.raises(Exception):
                dao._execute_query("INVALID SQL STATEMENT")

    def test_dao_with_real_database_operations(self, dao_with_db):
        """Test complex operations with real database interactions."""
        users = [
            ("user1", encrypt_password("password1")),
            ("user2", encrypt_password("password2")),
            ("user3", encrypt_password("password3")),
        ]
        
        with dao_with_db as dao:
            # Create users
            user_ids = []
            for login, password_hash in users:
                user_id = dao.create_new_user(login, password_hash)
                user_ids.append(user_id)
            
            # Update one user
            dao.update_user(user_ids[0], login="updated_user1")
            
            # Delete one user
            dao.delete_user(user_ids[1])
            
            # Get remaining users
            remaining_users = dao.get_all_users()
            
            assert len(remaining_users) == 2
            
            # Verify updates and deletions
            logins = [u['login'] for u in remaining_users]
            assert "updated_user1" in logins
            assert users[1][0] not in logins  # Deleted user
            assert users[2][0] in logins  # Unchanged user
            
            # Verify all password hashes are in bcrypt format
            for user in remaining_users:
                assert user['password_hash'].startswith('$2b$')