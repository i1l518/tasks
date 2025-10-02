from sqlalchemy.orm import Session
# from . import models, schemas, auth  <- 여기서 auth 삭제
from . import models, schemas

# --- User CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str): # <- 인자로 hashed_password를 직접 받도록 변경
    # hashed_password = auth.get_password_hash(user.password)  <- 이 줄 삭제
    db_user = models.User(username=user.username, hashed_password=hashed_password, is_admin=user.is_admin) # <- user.password 대신 인자로 받은 hashed_password 사용
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Book CRUD ---
def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

def get_book_by_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(title=book.title, author=book.author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book