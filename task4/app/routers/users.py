"""
사용자 관련 API 엔드포인트(라우트)를 정의하는 파일입니다 (회원가입, 로그인).
APIRouter를 사용하여 관련 엔드포인트들을 그룹화합니다.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from .. import crud, schemas, auth
from ..database import get_db, settings

# APIRouter 인스턴스를 생성합니다.
# prefix: 이 라우터에 포함된 모든 엔드포인트의 경로 앞에 "/users"가 붙습니다.
# tags: API 문서에서 "users"라는 태그로 그룹화됩니다.
router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# POST /users/ 경로로 요청이 왔을 때 실행됩니다. (회원가입)
@router.post("/", response_model=schemas.User, summary="사용자 등록")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 이미 존재하는 사용자 이름인지 확인
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 비밀번호를 해싱합니다.
    hashed_password = auth.get_password_hash(user.password)
    # CRUD 함수를 호출하여 사용자를 생성합니다.
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)

# POST /users/token 경로로 요청이 왔을 때 실행됩니다. (로그인 및 토큰 발급)
@router.post("/token", response_model=schemas.Token, summary="로그인 및 토큰 발급")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 사용자 이름으로 사용자를 조회하고, 비밀번호가 일치하는지 확인합니다.
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 액세스 토큰의 유효 기간을 설정합니다.
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # JWT 액세스 토큰을 생성합니다.
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}