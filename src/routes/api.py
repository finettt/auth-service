import datetime
from fastapi import APIRouter

from ..crypto.utils import encrypt_password, verify_password
from ..database.dao.users import UsersDAO
from ..dto.api import AuthRequestDTO
from fastapi.responses import JSONResponse


router = APIRouter()


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
            return JSONResponse(status_code=401, content={"message": "Invalid credentials"})
        dao.update_user(user_id=user["id"],last_login=datetime.datetime.now())
        return JSONResponse(status_code=200, content={"message": "Login successful"})


@router.post("/delete")
def delete_account(request: AuthRequestDTO):
    with UsersDAO() as dao:
        user = dao.get_user_by_login(request.login)
        if not user or not verify_password(request.password, user["password_hash"]):
            return JSONResponse(status_code=401, content={"message": "Invalid credentials"})
        dao.delete_user(user["id"])
        return JSONResponse(status_code=200, content={"message": "User deleted successfully"})
