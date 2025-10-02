# 파일: main.py

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from library_api import crud, models, schemas, auth
from library_api.database import engine, get_db

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- 인증 엔드포인트 ---
@app.post("/auth/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- 도서 관리 엔드포인트 ---
@app.post("/books", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    # (과제 요구사항에 따라 관리자만 추가하도록 로직을 추가할 수도 있습니다)
    return crud.create_book(db=db, book=book)

@app.get("/books", response_model=List[schemas.Book])
def read_books(category: str = None, available: bool = None, db: Session = Depends(get_db)):
    books = crud.get_books(db, category=category, available=available)
    return books

@app.delete("/books/{book_id}", response_model=schemas.Book)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_book = crud.delete_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

# --- 대출/반납 엔드포인트 ---
@app.post("/loans", response_model=schemas.Loan, status_code=status.HTTP_201_CREATED)
def borrow_book(loan_data: schemas.LoanCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    book_id = loan_data.book_id
    user_id = current_user.id
    
    db_book = crud.get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    if db_book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book is not available for loan")

    loan = crud.create_loan(db=db, book_id=book_id, user_id=user_id)
    return loan

@app.get("/users/me/loans", response_model=List[schemas.Loan])
def read_user_loans(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.get_user_loans(db=db, user_id=current_user.id)