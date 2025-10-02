# 파일: schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

# --- Book Schemas ---
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    available_copies: int

    class Config:
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# --- Loan Schemas ---
class LoanBase(BaseModel):
    book_id: int
    user_id: int

class LoanCreate(BaseModel):
    book_id: int

class Loan(BaseModel):
    id: int
    book_id: int
    user_id: int
    loan_date: datetime.datetime
    return_date: Optional[datetime.datetime] = None
    book: Book # 대출 내역 조회 시 책 정보 포함

    class Config:
        from_attributes = True


# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None