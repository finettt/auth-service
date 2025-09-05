from pydantic import BaseModel


class AuthRequestDTO(BaseModel):
    email: str
    password: str
