from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
from ...database.connection import get_db_connection


logger = logging.getLogger(__name__)


class UsersDAO:
    def __init__(self) -> None:
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.conn = get_db_connection()
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()

    def _execute_query(self, query: str, params: Optional[Tuple] = None) -> None:
        """Helper method to execute a query with error handling."""
        try:
            if params:
                self.cur.execute(query, params) # type: ignore
            else:
                self.cur.execute(query) # type: ignore
        except Exception as e:
            logger.error(f"Database query failed: {query} with error: {str(e)}")
            raise

    def _fetch_all_as_dicts(self) -> List[Dict[str, Any]]:
        columns = [description[0] for description in self.cur.description] # type: ignore
        return [dict(zip(columns, row)) for row in self.cur.fetchall()] # type: ignore

    def get_all_users(self):
        try:
            self._execute_query("SELECT * FROM users")
            return self._fetch_all_as_dicts()
        except Exception as e:
            logger.error(f"Failed to get all users: {str(e)}")
            raise

    def create_new_user(self, login: str, password_hash: str) -> int:
        """Create a new user and return the user ID."""
        try:
            self._execute_query(
                "INSERT INTO users(login, password_hash, created_at) VALUES (?, ?, datetime('now'))",
                (login, password_hash),
            )
            if self.cur and self.cur.lastrowid:
                return self.cur.lastrowid
            raise Exception("Failed to get last row ID")
        except Exception as e:
            logger.error(f"Failed to create new user: {str(e)}")
            raise

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by their ID."""
        try:
            self._execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
            result = self._fetch_all_as_dicts()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            raise
    def get_user_by_login(self, login: str) -> Optional[Dict[str, Any]]:
        try:
            self._execute_query("SELECT * FROM users WHERE login = ?", (login,))
            result = self._fetch_all_as_dicts()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get user by login: {str(e)}")
            raise

    def update_user(
        self,
        user_id: int,
        login: Optional[str] = None,
        password_hash: Optional[str] = None,
        last_login: Optional[datetime] = None,
    ) -> bool:
        """Update a user's information."""
        try:
            if login is None and password_hash is None and last_login is None:
                return False
            query_parts = ["UPDATE users SET"]
            params = []
            if login is not None and password_hash is not None:
                query_parts.append("login = ?, password_hash = ?")
                params.extend([login, password_hash])
                if last_login is not None:
                    query_parts.append(", last_login = ?")
                    params.append(last_login)
            elif login is not None:
                query_parts.append("login = ?")
                params.append(login)
                if last_login is not None:
                    query_parts.append(", last_login = ?")
                    params.append(last_login)
            elif password_hash is not None:
                query_parts.append("password_hash = ?")
                params.append(password_hash)
                if last_login is not None:
                    query_parts.append(", last_login = ?")
                    params.append(last_login)
            elif last_login is not None:
                query_parts.append("last_login = ?")
                params.append(last_login)
            query_parts.append("WHERE id = ?")
            params.append(user_id)
            query = " ".join(query_parts)
            
            self._execute_query(query, tuple(params))

            return bool(self.cur and self.cur.rowcount > 0)
        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            raise

    def delete_user(self, user_id: int) -> bool:
        """Delete a user by their ID."""
        try:
            self._execute_query("DELETE FROM users WHERE id = ?", (user_id,))
            return bool(self.cur and self.cur.rowcount > 0)
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            raise
