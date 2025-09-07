from pydantic import BaseModel, field_validator
import re


class AuthRequestDTO(BaseModel):
    login: str
    password: str

    @field_validator('login')
    @classmethod
    def validate_login(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Login must be at least 3 characters long')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

    
