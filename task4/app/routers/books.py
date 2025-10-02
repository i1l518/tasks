from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/books",
    tags=["books"],
)

@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED, summary="새 도서 추가 (관리자)")
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), admin_user: models.User = Depends(auth.get_current_admin_user)):
    return crud.create_book(db=db, book=book)

@router.get("/", response_model=List[schemas.Book], summary="모든 도서 목록 조회")
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = crud.get_books(db, skip=skip, limit=limit)
    return books

@router.delete("/{book_id}", response_model=schemas.Book, summary="도서 삭제 (관리자)")
def delete_book(book_id: int, db: Session = Depends(get_db), admin_user: models.User = Depends(auth.get_current_admin_user)):
    db_book = crud.delete_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.post("/{book_id}/borrow", response_model=schemas.Book, summary="도서 대출 (로그인 사용자)")
def borrow_book(book_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    book = crud.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.is_borrowed:
        raise HTTPException(status_code=400, detail="Book is already borrowed")
    
    book.is_borrowed = True
    book.borrower_id = current_user.id
    db.commit()
    db.refresh(book)
    return book

@router.post("/{book_id}/return", response_model=schemas.Book, summary="도서 반납 (로그인 사용자)")
def return_book(book_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    book = crud.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.is_borrowed:
        raise HTTPException(status_code=400, detail="Book is not currently borrowed")
    if book.borrower_id != current_user.id and not current_user.is_admin:
         raise HTTPException(status_code=403, detail="You can only return books you borrowed")

    book.is_borrowed = False
    book.borrower_id = None
    db.commit()
    db.refresh(book)
    return book