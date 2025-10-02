"""
사용자 인증 관련 로직(비밀번호, JWT 토큰)을 처리하는 파일입니다.
비밀번호 해싱, 토큰 생성/검증, API 엔드포인트에서 현재 사용자를 가져오는 의존성 함수 등을 포함합니다.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from . import schemas, models, crud
from .database import get_db, settings

# 비밀번호 해싱을 위한 설정
# "bcrypt" 알고리즘을 사용하도록 지정합니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 스킴을 정의합니다. FastAPI가 API 문서에서 인증 UI를 생성하고,
# 요청 헤더에서 'Bearer' 토큰을 추출하는 방법을 알게 됩니다.
# tokenUrl은 토큰을 발급받는 API 엔드포인트의 경로를 가리킵니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

# 입력된 평문 비밀번호와 해싱된 비밀번호가 일치하는지 확인하는 함수
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 평문 비밀번호를 bcrypt 해시로 변환하는 함수
def get_password_hash(password):
    return pwd_context.hash(password)

# JWT 액세스 토큰을 생성하는 함수
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # 유효 기간이 주어지지 않으면 기본 15분으로 설정
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})  # 만료 시간(exp) 필드 추가
    # 비밀 키와 알고리즘을 사용하여 JWT를 인코딩합니다.
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# API 요청 헤더의 토큰을 검증하고, 현재 로그인한 사용자 정보를 반환하는 의존성 함수
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 토큰 검증 실패 시 발생시킬 예외
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # JWT 토큰을 디코딩하여 payload(내용물)를 추출합니다.
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")  # 토큰의 'sub'(subject) 필드에서 사용자 이름을 가져옵니다.
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        # 토큰 디코딩 과정에서 에러 발생 시 (유효하지 않은 토큰, 만료된 토큰 등)
        raise credentials_exception
    
    # 데이터베이스에서 해당 사용자 이름으로 사용자 정보를 조회합니다.
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        # 토큰은 유효하지만 해당 사용자가 DB에 없는 경우
        raise credentials_exception
    return user

# 현재 로그인한 사용자가 관리자인지 확인하는 의존성 함수
def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        # 관리자가 아닐 경우 403 Forbidden 에러 발생
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user