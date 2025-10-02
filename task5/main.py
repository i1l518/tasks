# 필요한 라이브러리들을 가져옵니다.
import os  # .env 파일에서 환경 변수를 읽어오기 위해 필요합니다.
from datetime import datetime, timedelta  # 토큰 만료 시간을 다루기 위해 필요합니다.
from typing import Dict, List, Optional  # 타입 힌팅을 위해 필요합니다.

import jwt  # JWT(JSON Web Token)를 생성하고 검증하기 위해 필요합니다.
from dotenv import load_dotenv  # .env 파일의 내용을 환경 변수로 로드하기 위해 필요합니다.
from fastapi import Depends, FastAPI, HTTPException, status  # FastAPI 핵심 기능들입니다.
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # 사용자 인증을 위해 필요합니다.
from passlib.context import CryptContext  # 비밀번호를 안전하게 해싱하기 위해 필요합니다.
from pydantic import BaseModel, Field  # 데이터 유효성 검사 및 모델 정의를 위해 필요합니다.

# .env 파일에 정의된 환경 변수를 스크립트로 로드합니다.
load_dotenv()

# FastAPI 애플리케이션 인스턴스를 생성합니다. API 문서의 제목을 "Library API"로 설정합니다.
app = FastAPI(title="Library API")


# --- 보안 및 인증 관련 설정 ---
# JWT를 암호화할 때 사용할 비밀 키를 .env 파일에서 가져옵니다.
SECRET_KEY = os.getenv("SECRET_KEY")
# 사용할 암호화 알고리즘을 지정합니다.
ALGORITHM = os.getenv("ALGORITHM")
# 액세스 토큰의 유효 기간(분 단위)을 .env 파일에서 가져와 정수로 변환합니다.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# 비밀번호 해싱을 위한 설정입니다. "bcrypt" 알고리즘을 사용합니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 인증 스키마를 설정합니다. 토큰을 받을 URL은 "/auth/login"입니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# --- 인메모리(In-memory) "데이터베이스" ---
# 실제 프로덕션 환경에서는 PostgreSQL, MongoDB 같은 실제 데이터베이스를 사용해야 합니다.
# 여기서는 간단한 시연을 위해 파이썬 딕셔너리와 리스트를 데이터베이스처럼 사용합니다.
users_db: Dict[str, Dict] = {}  # 사용자 정보를 저장할 딕셔너리
books_db: Dict[int, Dict] = {}   # 도서 정보를 저장할 딕셔너리
loans_db: List[Dict] = []       # 대출 정보를 저장할 리스트
next_user_id = 1                # 다음 사용자에게 할당할 ID
next_book_id = 1                # 다음 도서에 할당할 ID
next_loan_id = 1                # 다음 대출에 할당할 ID

def setup_initial_admin_user():
    """서버가 시작될 때 'admin' 사용자가 없으면 기본 관리자 계정을 생성하는 함수입니다."""
    global next_user_id
    if "admin" not in users_db:
        admin_user = {
            "id": next_user_id,
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": pwd_context.hash("adminpass"), # 비밀번호를 해싱하여 저장
            "full_name": "Admin User",
            "is_admin": True  # 관리자 권한 부여
        }
        users_db["admin"] = admin_user
        next_user_id += 1


# --- Pydantic 모델 (데이터 유효성 검사 및 형태 정의) ---
# Pydantic 모델을 사용하면 API가 요청/응답하는 데이터의 형식을 강제하고 자동으로 유효성을 검사할 수 있습니다.

class UserCreate(BaseModel):
    """회원가입 시 클라이언트로부터 받을 데이터 모델입니다."""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    """회원가입 후 클라이언트에게 응답으로 보낼 데이터 모델입니다. (비밀번호 제외)"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None

class BookCreate(BaseModel):
    """새로운 도서를 생성할 때 받을 데이터 모델입니다."""
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int = Field(..., gt=0)  # 총 권수는 0보다 커야 함을 강제합니다.

class BookOut(BaseModel):
    """도서 정보를 응답으로 보낼 때 사용할 데이터 모델입니다."""
    id: int
    title: str
    author: str
    isbn: str
    category: str
    available_copies: int

class LoanCreate(BaseModel):
    """도서 대출 시 받을 데이터 모델입니다."""
    book_id: int

class LoanOut(BaseModel):
    """대출 정보를 응답으로 보낼 때 사용할 데이터 모델입니다."""
    id: int
    book_id: int
    user_id: int
    loan_date: datetime
    return_date: Optional[datetime] = None  # 반납 날짜는 처음에는 비어있을 수 있습니다.

class Token(BaseModel):
    """로그인 성공 시 보낼 JWT 토큰 데이터 모델입니다."""
    access_token: str
    token_type: str


# --- 유틸리티 및 의존성 주입(Dependency Injection) 함수 ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """사용자 정보를 받아 JWT 액세스 토큰을 생성하는 함수입니다."""
    to_encode = data.copy()
    # 토큰 만료 시간을 설정합니다.
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    # JWT를 생성합니다.
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    API 요청 헤더의 토큰을 해석하여 현재 로그인된 사용자를 찾아 반환하는 의존성 함수입니다.
    이 함수를 필요로 하는 엔드포인트는 자동으로 토큰 유효성 검사를 수행하게 됩니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 토큰을 디코딩하여 payload를 얻습니다.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # payload에서 사용자 이름을 추출합니다.
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError: # 토큰이 유효하지 않은 경우
        raise credentials_exception
    
    # 데이터베이스에서 해당 사용자 정보를 찾습니다.
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

async def get_admin_user(current_user: Dict = Depends(get_current_user)):
    """
    현재 로그인한 사용자가 관리자인지 확인하는 의존성 함수입니다.
    이 함수를 필요로 하는 엔드포인트는 관리자만 접근할 수 있습니다.
    """
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # 권한 없음
            detail="Operation requires admin privileges"
        )
    return current_user


# --- API 엔드포인트 정의 ---

@app.on_event("startup")
async def startup_event():
    """FastAPI 애플리케이션이 시작될 때 단 한 번 실행되는 이벤트입니다."""
    setup_initial_admin_user()

@app.post("/auth/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    """사용자 회원가입을 처리하는 엔드포인트입니다."""
    global next_user_id
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = {
        "id": next_user_id,
        "username": user.username,
        "email": user.email,
        "hashed_password": pwd_context.hash(user.password),
        "full_name": user.full_name,
        "is_admin": False
    }
    users_db[user.username] = new_user
    next_user_id += 1
    return new_user

@app.post("/auth/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """사용자 로그인을 처리하고 액세스 토큰을 발급하는 엔드포인트입니다."""
    user = users_db.get(form_data.username)
    # 사용자가 존재하고 비밀번호가 일치하는지 확인합니다.
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 액세스 토큰을 생성합니다.
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, admin: Dict = Depends(get_admin_user)):
    """새로운 도서를 추가하는 엔드포인트입니다. (관리자 전용)"""
    global next_book_id
    new_book = book.model_dump()
    new_book["id"] = next_book_id
    new_book["available_copies"] = book.total_copies
    books_db[next_book_id] = new_book
    next_book_id += 1
    return new_book

@app.get("/books", response_model=List[BookOut])
async def search_books(category: Optional[str] = None, available: Optional[bool] = None):
    """도서를 검색하는 엔드포인트입니다. 카테고리나 대출 가능 여부로 필터링할 수 있습니다."""
    results = list(books_db.values())
    if category:
        results = [b for b in results if b["category"].lower() == category.lower()]
    if available is not None and available:
        results = [b for b in results if b["available_copies"] > 0]
    return results

@app.post("/loans", response_model=LoanOut, status_code=status.HTTP_201_CREATED)
async def borrow_book(loan_data: LoanCreate, current_user: Dict = Depends(get_current_user)):
    """도서를 대출하는 엔드포인트입니다. (로그인 필요)"""
    global next_loan_id
    book = books_db.get(loan_data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book["available_copies"] <= 0:
        raise HTTPException(status_code=400, detail="No available copies of this book")

    # 대출 가능한 권수를 1 감소시킵니다.
    book["available_copies"] -= 1
    
    new_loan = {
        "id": next_loan_id,
        "book_id": book["id"],
        "user_id": current_user["id"], # 토큰에서 인증된 사용자의 ID를 사용
        "loan_date": datetime.utcnow(),
        "return_date": None
    }
    loans_db.append(new_loan)
    next_loan_id += 1
    return new_loan

@app.get("/users/me/loans", response_model=List[LoanOut])
async def get_my_loans(current_user: Dict = Depends(get_current_user)):
    """현재 로그인한 사용자의 대출 목록을 조회하는 엔드포인트입니다. (로그인 필요)"""
    return [loan for loan in loans_db if loan["user_id"] == current_user["id"]]