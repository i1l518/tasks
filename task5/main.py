import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, Field

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

app = FastAPI(title="Library API")

# --- Security & Authentication ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- In-memory "Database" ---
users_db: Dict[str, Dict] = {}
books_db: Dict[int, Dict] = {}
loans_db: List[Dict] = []
next_user_id = 1
next_book_id = 1
next_loan_id = 1

def setup_initial_admin_user():
    global next_user_id
    if "admin" not in users_db:
        admin_user = {
            "id": next_user_id,
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": pwd_context.hash("adminpass"),
            "full_name": "Admin User",
            "is_admin": True
        }
        users_db["admin"] = admin_user
        next_user_id += 1

# --- Pydantic Models (Data Validation) ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int = Field(..., gt=0)

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    category: str
    available_copies: int

class LoanCreate(BaseModel):
    book_id: int

class LoanOut(BaseModel):
    id: int
    book_id: int
    user_id: int
    loan_date: datetime
    return_date: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Utility & Dependency Functions ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

async def get_admin_user(current_user: Dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin privileges"
        )
    return current_user

# --- API Endpoints ---
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 관리자 계정을 미리 생성합니다."""
    setup_initial_admin_user()

@app.post("/auth/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
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
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, admin: Dict = Depends(get_admin_user)):
    global next_book_id
    new_book = book.model_dump()
    new_book["id"] = next_book_id
    new_book["available_copies"] = book.total_copies
    books_db[next_book_id] = new_book
    next_book_id += 1
    return new_book

@app.get("/books", response_model=List[BookOut])
async def search_books(category: Optional[str] = None, available: Optional[bool] = None):
    results = list(books_db.values())
    if category:
        results = [b for b in results if b["category"].lower() == category.lower()]
    if available is not None and available:
        results = [b for b in results if b["available_copies"] > 0]
    return results

@app.post("/loans", response_model=LoanOut, status_code=status.HTTP_201_CREATED)
async def borrow_book(loan_data: LoanCreate, current_user: Dict = Depends(get_current_user)):
    global next_loan_id
    book = books_db.get(loan_data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book["available_copies"] <= 0:
        raise HTTPException(status_code=400, detail="No available copies of this book")

    book["available_copies"] -= 1
    new_loan = {
        "id": next_loan_id,
        "book_id": book["id"],
        "user_id": current_user["id"],
        "loan_date": datetime.utcnow(),
        "return_date": None
    }
    loans_db.append(new_loan)
    next_loan_id += 1
    return new_loan

@app.get("/users/me/loans", response_model=List[LoanOut])
async def get_my_loans(current_user: Dict = Depends(get_current_user)):
    return [loan for loan in loans_db if loan["user_id"] == current_user["id"]]