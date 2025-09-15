import datetime
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..crypto.utils import encrypt_password, verify_password
from ..database.dao.users import UsersDAO
from ..database.dao.tokens import TokensDAO
from ..dto.api import AuthRequestDTO
from ..database.settings import settings
from fastapi.responses import JSONResponse

security = HTTPBearer()

router = APIRouter()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token and validate it against Redis."""
    token = credentials.credentials
    try:
        # Verify JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        login = payload.get("sub")

        if not user_id or not login:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        # Validate token exists in Redis
        with TokensDAO() as token_dao:
            if not token_dao.is_token_valid(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token not found or expired",
                )

        return {"user_id": user_id, "login": login}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@router.post("/register")
def register_account(request: AuthRequestDTO):
    with UsersDAO() as dao:
        user_id = dao.create_new_user(request.login, encrypt_password(request.password))
    return JSONResponse(status_code=201, content={"id": user_id})


@router.post("/login")
def login_account(request: AuthRequestDTO):
    with UsersDAO() as dao:
        user = dao.get_user_by_login(request.login)
        if not user or not verify_password(request.password, user["password_hash"]):
            return JSONResponse(
                status_code=401, content={"message": "Invalid credentials"}
            )

        dao.update_user(user_id=user["id"], last_login=datetime.datetime.now())

        # Generate JWT token
        token_data = {
            "sub": user["login"],
            "user_id": user["id"],
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=24),
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")

        # Store token in Redis
        with TokensDAO() as token_dao:
            token_dao.store_token(user["id"], token)

        return JSONResponse(
            status_code=200, content={"access_token": token, "token_type": "bearer"}
        )


@router.post("/logout")
def logout_account(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user by removing their token from Redis."""
    token = credentials.credentials

    # Remove token from Redis
    with TokensDAO() as token_dao:
        if token_dao.delete_token(token):
            return JSONResponse(
                status_code=200, content={"message": "Successfully logged out"}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to logout token"
            )


@router.post("/delete")
def delete_account(request: AuthRequestDTO):
    with UsersDAO() as dao:
        user = dao.get_user_by_login(request.login)
        if not user or not verify_password(request.password, user["password_hash"]):
            return JSONResponse(
                status_code=401, content={"message": "Invalid credentials"}
            )

        # Revoke all user tokens before deleting account
        with TokensDAO() as token_dao:
            token_dao.revoke_user_tokens(user["id"])

        dao.delete_user(user["id"])
        return JSONResponse(
            status_code=200, content={"message": "User deleted successfully"}
        )


@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    with UsersDAO() as dao:
        user = dao.get_user_by_id(current_user["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Remove sensitive data
        user.pop("password_hash", None)
        return user
