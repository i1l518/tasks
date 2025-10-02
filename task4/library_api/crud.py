# 파일: crud.py

from sqlalchemy.orm import Session
from . import models, schemas, auth

# --- User CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Book CRUD ---
def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, category: str = None, available: bool = None):
    query = db.query(models.Book)
    if category:
        query = query.filter(models.Book.category == category)
    if available is not None and available:
        query = query.filter(models.Book.available_copies > 0)
    return query.all()

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(
        **book.dict(),
        available_copies=book.total_copies
    )
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
    return None

# --- Loan CRUD ---
def create_loan(db: Session, book_id: int, user_id: int):
    book = get_book(db, book_id)
    if not book or book.available_copies <= 0:
        return None  # 대출 불가

    book.available_copies -= 1
    db_loan = models.Loan(book_id=book_id, user_id=user_id)
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def get_user_loans(db: Session, user_id: int):
    return db.query(models.Loan).filter(models.Loan.user_id == user_id).all()