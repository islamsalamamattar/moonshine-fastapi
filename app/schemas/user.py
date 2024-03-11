from pydantic import BaseModel, EmailStr, validator, UUID4
from typing import Any, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    firstName: str
    lastName: str
    imageUrl: Optional[str]

class User(UserBase):
    id: UUID4
    created_at: datetime
    is_disabled: bool
    is_onboarded: bool

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    imageUrl: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    password: Optional[str] = None

class UserPatch(UserUpdate):
    pass


class UserRegister(UserBase):
    password: str
    confirm_password: str

    @validator("confirm_password")
    def verify_password_match(cls, v, values, **kwargs):
        password = values.get("password")

        if v != password:
            raise ValueError("The two passwords did not match.")

        return v


class UserLogin(BaseModel):
    username: str
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    password: str
    confirm_password: str

    @validator("confirm_password")
    def verify_password_match(cls, v, values, **kwargs):
        password = values.get("password")

        if v != password:
            raise ValueError("The two passwords did not match.")

        return v


class PasswordUpdateSchema(PasswordResetSchema):
    old_password: str


class OldPasswordErrorSchema(BaseModel):
    old_password: bool

    @validator("old_password")
    def check_old_password_status(cls, v, values, **kwargs):
        if not v:
            raise ValueError("Old password is not corret")


