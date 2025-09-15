import unittest.mock
import pytest
from datetime import datetime
from src.database.dao.users import UsersDAO


def test_users_dao_init():
    """Test UsersDAO initialization."""
    dao = UsersDAO()
    assert dao.conn is None
    assert dao.cur is None


def test_users_dao_context_manager():
    """Test UsersDAO context manager functionality."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            assert dao.conn == mock_conn
            assert dao.cur == mock_cur
        
        # Verify that close was called
        mock_cur.close.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


def test_users_dao_context_manager_with_exception():
    """Test UsersDAO context manager with exception."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        try:
            with UsersDAO() as dao:
                assert dao.conn == mock_conn
                assert dao.cur == mock_cur
                raise Exception("Test exception")
        except Exception:
            pass
        
        # Verify that rollback was called instead of commit
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()


def test_execute_query_with_params():
    """Test _execute_query with parameters."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            query = "SELECT * FROM users WHERE id = %s"
            params = (1,)
            
            dao._execute_query(query, params)
            
            mock_cur.execute.assert_called_once_with(query, params)


def test_execute_query_without_params():
    """Test _execute_query without parameters."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            query = "SELECT * FROM users"
            
            dao._execute_query(query)
            
            mock_cur.execute.assert_called_once_with(query)


def test_execute_query_with_exception():
    """Test _execute_query with exception."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.execute.side_effect = Exception("Database error")
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            with pytest.raises(Exception, match="Database error"):
                dao._execute_query("SELECT * FROM users")


def test_fetch_all_as_dicts():
    """Test _fetch_all_as_dicts method."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.description = [("id",), ("login",), ("password_hash",)]
        mock_cur.fetchall.return_value = [(1, "testuser", "hash123")]
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao._fetch_all_as_dicts()
            
            expected = [{"id": 1, "login": "testuser", "password_hash": "hash123"}]
            assert result == expected


def test_get_all_users():
    """Test get_all_users method."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.description = [("id",), ("login",), ("password_hash",)]
        mock_cur.fetchall.return_value = [(1, "testuser", "hash123")]
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.get_all_users()
            
            expected = [{"id": 1, "login": "testuser", "password_hash": "hash123"}]
            assert result == expected
            mock_cur.execute.assert_called_once_with("SELECT * FROM users")


def test_create_new_user():
    """Test create_new_user method."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = [1]
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.create_new_user("testuser", "hashed_password")
            
            assert result == 1
            mock_cur.execute.assert_called_once()
            mock_cur.fetchone.assert_called_once()


def test_create_new_user_failure():
    """Test create_new_user method when fetchone returns None."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            with pytest.raises(Exception, match="Failed to get last row ID"):
                dao.create_new_user("testuser", "hashed_password")


def test_get_user_by_id():
    """Test get_user_by_id method."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.description = [("id",), ("login",), ("password_hash",)]
        mock_cur.fetchall.return_value = [(1, "testuser", "hash123")]
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.get_user_by_id(1)
            
            expected = {"id": 1, "login": "testuser", "password_hash": "hash123"}
            assert result == expected
            mock_cur.execute.assert_called_once_with("SELECT * FROM users WHERE id = %s", (1,))


def test_get_user_by_id_not_found():
    """Test get_user_by_id method when user is not found."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchall.return_value = []
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.get_user_by_id(999)
            
            assert result is None


def test_get_user_by_login():
    """Test get_user_by_login method."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.description = [("id",), ("login",), ("password_hash",)]
        mock_cur.fetchall.return_value = [(1, "testuser", "hash123")]
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.get_user_by_login("testuser")
            
            expected = {"id": 1, "login": "testuser", "password_hash": "hash123"}
            assert result == expected
            mock_cur.execute.assert_called_once_with("SELECT * FROM users WHERE login = %s", ("testuser",))


def test_get_user_by_login_not_found():
    """Test get_user_by_login method when user is not found."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchall.return_value = []
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.get_user_by_login("nonexistent")
            
            assert result is None


def test_update_user_no_changes():
    """Test update_user method with no changes."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.update_user(1)
            
            assert result is False
            mock_cur.execute.assert_not_called()


def test_update_user_login_only():
    """Test update_user method with login only."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_cur.rowcount = 1
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.update_user(1, login="newlogin")
            
            assert result is True
            mock_cur.execute.assert_called_once()


def test_update_user_password_only():
    """Test update_user method with password only."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_cur.rowcount = 1
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.update_user(1, password_hash="newhash")
            
            assert result is True
            mock_cur.execute.assert_called_once()


def test_update_user_last_login_only():
    """Test update_user method with last_login only."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_cur.rowcount = 1
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            now = datetime.now()
            result = dao.update_user(1, last_login=now)
            
            assert result is True
            mock_cur.execute.assert_called_once()


def test_update_user_all_fields():
    """Test update_user method with all fields."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_cur.rowcount = 1
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            now = datetime.now()
            result = dao.update_user(1, login="newlogin", password_hash="newhash", last_login=now)
            
            assert result is True
            mock_cur.execute.assert_called_once()


def test_delete_user():
    """Test delete_user method."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_cur.rowcount = 1
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.delete_user(1)
            
            assert result is True
            mock_cur.execute.assert_called_once_with("DELETE FROM users WHERE id = %s", (1,))


def test_delete_user_not_found():
    """Test delete_user method when user is not found."""
    with unittest.mock.patch("src.database.dao.users.get_db_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_cur = unittest.mock.MagicMock()
        mock_cur.rowcount = 0
        mock_conn.cursor.return_value = mock_cur
        mock_get_conn.return_value = mock_conn
        
        with UsersDAO() as dao:
            result = dao.delete_user(999)
            
            assert result is False