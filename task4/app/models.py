"""
SQLAlchemy를 사용하여 데이터베이스 테이블 구조를 파이썬 클래스 형태로 정의하는 파일입니다.
이 클래스들은 ORM에 의해 실제 데이터베이스 테이블과 매핑됩니다.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base  # database.py에서 정의한 Base 클래스를 가져옴

# 사용자 정보를 저장하는 'users' 테이블 모델
class User(Base):
    __tablename__ = "users"  # 데이터베이스에서 사용할 실제 테이블 이름

    id = Column(Integer, primary_key=True, index=True)  # 사용자 고유 ID, 기본 키
    username = Column(String, unique=True, index=True, nullable=False)  # 사용자 이름, 중복 불가
    hashed_password = Column(String, nullable=False)  # 해싱된 비밀번호
    is_admin = Column(Boolean, default=False)  # 관리자 여부, 기본값은 False

# 도서 정보를 저장하는 'books' 테이블 모델
class Book(Base):
    __tablename__ = "books"  # 데이터베이스에서 사용할 실제 테이블 이름

    id = Column(Integer, primary_key=True, index=True)  # 도서 고유 ID, 기본 키
    title = Column(String, index=True, nullable=False)  # 도서 제목
    author = Column(String, index=True, nullable=False)  # 저자
    is_borrowed = Column(Boolean, default=False)  # 대출 여부, 기본값은 False
    borrower_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 대출한 사용자의 ID, 외래 키

    # User 모델과의 관계를 설정합니다. Book.borrower를 통해 해당 책을 빌린 User 객체에 접근할 수 있습니다.
    borrower = relationship("User")