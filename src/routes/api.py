from fastapi import APIRouter

from ..crypto.utils import encrypt_password
from ..database.dao.users import UsersDAO
from ..dto.api import AuthRequestDTO
from fastapi.responses import JSONResponse


router = APIRouter()


@router.post("/register")
def register_account(request: AuthRequestDTO):
    with UsersDAO() as dao:
        user_id = dao.create_new_user(request.email, encrypt_password(request.password))
    return JSONResponse(status_code=201, content={"id": user_id})


@router.post("/login")
def login_account(request: AuthRequestDTO):
    with UsersDAO() as dao:
        user = dao.get_user_by_email(request.email)
        if not user:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        if user["password_hash"] == encrypt_password(request.password):
            return JSONResponse(status_code=201, content={"message": "Succes login"})
        else:
            return JSONResponse(
                status_code=401, content={"message": "Password incorrect"}
            )


@router.post("/delete")
def delete_account(request: AuthRequestDTO):
    with UsersDAO() as dao:
        user = dao.get_user_by_email(request.email)
        if not user:
            return JSONResponse(status_code=404, content={"message": "User not found"})
        if user["password_hash"] == encrypt_password(request.password):
            dao.delete_user(user["id"])
            return JSONResponse(status_code=200, content={"message": "User deleted"})
        return JSONResponse(status_code=401, content={"message": "Password incorrect"})
