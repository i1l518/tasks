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
    return crud.get_user_loans(db=db, user_id=current_user.id)# 파일: main.py
# FastAPI 애플리케이션의 메인 파일입니다.
# API 엔드포인트(라우터)를 정의하고, 서버 실행의 시작점 역할을 합니다.

# --- 필요한 라이브러리 및 모듈 임포트 ---
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # 사용자 로그인 시 'username', 'password'를 form 데이터로 받기 위한 클래스
from sqlalchemy.orm import Session # 데이터베이스 세션을 타입 힌팅하기 위해 사용
from typing import List # List 타입을 힌팅하기 위해 사용

# --- 직접 만든 모듈 임포트 ---
# library_api 폴더 내의 다른 파이썬 파일들에서 필요한 함수, 클래스, 변수 등을 가져옵니다.
from library_api import crud, models, schemas, auth
from library_api.database import engine, get_db

# --- 데이터베이스 테이블 생성 ---
# 애플리케이션이 시작될 때, models.py에 정의된 모든 SQLAlchemy 모델(테이블)들을
# 데이터베이스에 생성합니다. (이미 테이블이 존재하면 아무 작업도 하지 않음)
models.Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()


# ===============================================================
# --- 1. 인증(Authentication) 관련 엔드포인트 ---
# ===============================================================

@app.post("/auth/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    회원가입을 위한 API 엔드포인트입니다.
    - 요청 본문(body)으로 사용자 정보를 받아 데이터베이스에 새로운 사용자를 생성합니다.
    - response_model=schemas.User: 성공 시 반환될 데이터의 형태를 지정 (비밀번호 제외)
    - status_code=201: 성공적으로 리소스가 생성되었음을 의미하는 HTTP 상태 코드
    """
    # 이메일 중복 확인
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 사용자 이름 중복 확인
    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 중복이 없으면 crud의 create_user 함수를 호출하여 사용자를 생성
    return crud.create_user(db=db, user=user)


@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    사용자 로그인을 처리하고 JWT(JSON Web Token) 액세스 토큰을 발급하는 엔드포인트입니다.
    - OAuth2PasswordRequestForm: 'username'과 'password'를 form 데이터 형식으로 받습니다.
    """
    # 사용자 이름으로 데이터베이스에서 사용자 정보를 가져옴
    user = crud.get_user_by_username(db, username=form_data.username)
    
    # 사용자가 없거나 비밀번호가 일치하지 않으면 401 Unauthorized 에러 발생
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}, # 응답 헤더에 인증 방식을 명시
        )
        
    # 인증 성공 시, 사용자 정보(username)를 기반으로 액세스 토큰 생성
    access_token = auth.create_access_token(
        data={"sub": user.username} # 'sub'는 토큰의 주체(subject)를 의미하는 표준 필드
    )
    
    # 생성된 토큰을 클라이언트에게 반환
    return {"access_token": access_token, "token_type": "bearer"}


# ===============================================================
# --- 2. 도서(Book) 관리 관련 엔드포인트 ---
# ===============================================================

@app.post("/books", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    """
    새로운 도서를 등록하는 엔드포인트입니다.
    - Depends(auth.get_current_user): 이 엔드포인트에 접근하기 위해 유효한 JWT 토큰이 필요함을 의미합니다.
                                      요청 헤더의 토큰을 검증하고, 유효하면 해당 사용자 정보를 반환합니다.
                                      토큰이 없거나 유효하지 않으면 401 에러를 자동으로 발생시킵니다.
    """
    # crud의 create_book 함수를 호출하여 도서를 데이터베이스에 저장
    return crud.create_book(db=db, book=book)


@app.get("/books", response_model=List[schemas.Book])
def read_books(category: str = None, available: bool = None, db: Session = Depends(get_db)):
    """
    도서 목록을 조회하는 엔드포인트입니다. (인증 불필요)
    - 쿼리 파라미터(Query Parameter)를 통해 도서를 필터링할 수 있습니다.
    - 예시: /books?category=Programming&available=true
    """
    books = crud.get_books(db, category=category, available=available)
    return books


@app.delete("/books/{book_id}", response_model=schemas.Book)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    """
    특정 도서를 삭제하는 엔드포인트입니다. (인증 필요)
    - 경로 매개변수(Path Parameter)인 book_id를 받아 해당 ID의 책을 삭제합니다.
    """
    db_book = crud.delete_book(db, book_id=book_id)
    # 삭제하려는 책이 데이터베이스에 존재하지 않으면 404 Not Found 에러 발생
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


# ===============================================================
# --- 3. 대출(Loan) 관리 관련 엔드포인트 ---
# ===============================================================

@app.post("/loans", response_model=schemas.Loan, status_code=status.HTTP_201_CREATED)
def borrow_book(loan_data: schemas.LoanCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    """
    도서를 대출하는 엔드포인트입니다. (인증 필요)
    """
    book_id = loan_data.book_id
    # 토큰을 통해 인증된 사용자의 ID를 가져옴
    user_id = current_user.id
    
    # 대출하려는 책이 존재하는지 확인
    db_book = crud.get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    # 대출 가능한 재고가 있는지 확인
    if db_book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book is not available for loan")

    # crud의 create_loan 함수를 호출하여 대출 기록을 생성
    loan = crud.create_loan(db=db, book_id=book_id, user_id=user_id)
    return loan


@app.get("/users/me/loans", response_model=List[schemas.Loan])
def read_user_loans(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    """
    현재 로그인된 사용자의 대출 기록을 조회하는 엔드포인트입니다. (인증 필요)
    - 'me'라는 키워드를 사용하여 자기 자신의 정보를 조회함을 나타냅니다.
    """
    # crud의 get_user_loans 함수를 호출하여 현재 사용자의 대출 목록을 가져옴
    return crud.get_user_loans(db=db, user_id=current_user.id)