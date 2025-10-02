"""
CRUD(Create, Read, Update, Delete) 작업을 수행하는 함수들을 모아놓은 파일입니다.
API 엔드포인트의 로직과 데이터베이스 상호작용 로직을 분리하여 코드를 더 깔끔하게 유지합니다.
"""
from sqlalchemy.orm import Session
from . import models, schemas

# --- 사용자(User) 관련 CRUD 함수 ---

# ID로 특정 사용자를 조회
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# 사용자 이름(username)으로 특정 사용자를 조회
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# 새 사용자를 데이터베이스에 생성
# 라우터에서 해싱된 비밀번호를 직접 받아서 저장합니다.
def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(username=user.username, hashed_password=hashed_password, is_admin=user.is_admin)
    db.add(db_user)  # DB 세션에 새 사용자 객체 추가
    db.commit()      # 변경사항을 DB에 커밋(저장)
    db.refresh(db_user) # DB에서 방금 생성된 사용자 정보를 다시 읽어옴 (ID 등)
    return db_user

# --- 도서(Book) 관련 CRUD 함수 ---

# 모든 도서 목록을 조회 (페이지네이션을 위한 skip, limit 옵션 포함)
def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

# ID로 특정 도서를 조회
def get_book_by_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

# 새 도서를 데이터베이스에 생성
def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(title=book.title, author=book.author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# ID로 특정 도서를 삭제
def delete_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book