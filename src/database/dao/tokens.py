import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from ...database.redis_connection import get_redis_connection

logger = logging.getLogger(__name__)


class TokensDAO:
    """Data Access Object for managing tokens in Redis."""

    def __init__(self) -> None:
        self.redis_conn = None

    def __enter__(self):
        self.redis_conn = get_redis_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.redis_conn:
            self.redis_conn.close()

    def store_token(self, user_id: int, token: str, expires_in_hours: int = 24) -> bool:
        """Store a token in Redis with expiration time."""
        try:
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            token_data = {
                "user_id": user_id,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            key = f"token:{token}"
            self.redis_conn.setex(key, expires_in_hours * 3600, json.dumps(token_data))
            return True
        except Exception as e:
            logger.error(f"Failed to store token: {str(e)}")
            return False

    def get_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token data from Redis."""
        try:
            key = f"token:{token}"
            token_data = self.redis_conn.get(key)
            if token_data:
                return json.loads(token_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get token: {str(e)}")
            return None

    def delete_token(self, token: str) -> bool:
        """Delete a token from Redis."""
        try:
            key = f"token:{token}"
            result = self.redis_conn.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete token: {str(e)}")
            return False

    def is_token_valid(self, token: str) -> bool:
        """Check if a token exists and is not expired."""
        try:
            token_data = self.get_token(token)
            if not token_data:
                return False
            
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            return datetime.now() < expires_at
        except Exception as e:
            logger.error(f"Failed to validate token: {str(e)}")
            return False

    def get_user_tokens(self, user_id: int) -> list:
        """Get all tokens for a specific user."""
        try:
            pattern = "token:*"
            keys = self.redis_conn.keys(pattern)
            user_tokens = []
            
            for key in keys:
                token_data = self.redis_conn.get(key)
                if token_data:
                    data = json.loads(token_data)
                    if data.get("user_id") == user_id:
                        user_tokens.append({
                            "token": key.replace("token:", ""),
                            "expires_at": data.get("expires_at"),
                            "created_at": data.get("created_at")
                        })
            
            return user_tokens
        except Exception as e:
            logger.error(f"Failed to get user tokens: {str(e)}")
            return []

    def revoke_user_tokens(self, user_id: int) -> int:
        """Revoke all tokens for a specific user."""
        try:
            pattern = "token:*"
            keys = self.redis_conn.keys(pattern)
            revoked_count = 0
            
            for key in keys:
                token_data = self.redis_conn.get(key)
                if token_data:
                    data = json.loads(token_data)
                    if data.get("user_id") == user_id:
                        self.redis_conn.delete(key)
                        revoked_count += 1
            
            return revoked_count
        except Exception as e:
            logger.error(f"Failed to revoke user tokens: {str(e)}")
            return 0