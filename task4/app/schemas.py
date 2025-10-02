"""
Pydantic을 사용하여 API 요청/응답 데이터의 형태를 정의하고 유효성을 검사하는 파일입니다.
데이터의 타입을 강제하고, 필수 필드를 지정하여 API의 안정성을 높입니다.
"""
from pydantic import BaseModel
from typing import Optional

# --- 도서 관련 스키마 ---

# 도서의 기본 정보 (공통 필드)
class BookBase(BaseModel):
    title: str
    author: str

# 새 도서를 생성할 때 API 요청 본문으로 받을 데이터 형태
class BookCreate(BookBase):
    pass  # BookBase와 동일한 필드를 가짐

# API 응답으로 클라이언트에게 보여줄 도서 데이터 형태
class Book(BookBase):
    id: int
    is_borrowed: bool

    # SQLAlchemy 모델 객체를 Pydantic 모델로 변환할 수 있도록 설정
    class Config:
        from_attributes = True

# --- 사용자 관련 스키마 ---

# 사용자의 기본 정보
class UserBase(BaseModel):
    username: str

# 새 사용자를 생성(회원가입)할 때 API 요청 본문으로 받을 데이터 형태
class UserCreate(UserBase):
    password: str
    is_admin: bool = False

# API 응답으로 클라이언트에게 보여줄 사용자 데이터 형태 (비밀번호 제외)
class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

# --- 토큰 관련 스키마 ---

# 로그인 성공 시 응답으로 보낼 액세스 토큰의 형태
class Token(BaseModel):
    access_token: str
    token_type: str

# JWT 토큰 안에 저장될 데이터의 형태
class TokenData(BaseModel):
    username: Optional[str] = None