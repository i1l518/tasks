"""
데이터베이스 연결 설정 및 세션 관리를 담당하는 파일입니다.
SQLAlchemy 엔진, 세션 생성기, 모델의 기반이 될 Base 클래스를 정의합니다.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

# .env 파일의 환경 변수를 읽어오기 위한 Pydantic Settings 클래스
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        # .env 파일을 읽어오도록 설정
        env_file = ".env"

# Settings 클래스의 인스턴스를 생성하여 환경 변수를 로드합니다.
settings = Settings()

# SQLAlchemy 엔진을 생성합니다. 데이터베이스와의 연결을 관리합니다.
# SQLite를 사용할 때는 connect_args={"check_same_thread": False} 옵션이 필요합니다.
# 이는 FastAPI의 비동기 환경에서 SQLite가 안전하게 작동하도록 보장합니다.
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# 데이터베이스 세션(연결)을 생성하는 클래스입니다.
# autocommit=False, autoflush=False는 데이터 변경사항을 명시적으로 commit해야만 DB에 반영되도록 합니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 데이터베이스 모델(테이블)이 상속받을 기본 클래스입니다.
Base = declarative_base()

# API가 호출될 때마다 독립적인 데이터베이스 세션을 생성하고,
# 요청 처리가 끝나면 세션을 자동으로 닫아주는 의존성 함수입니다.
def get_db():
    db = SessionLocal()  # 데이터베이스 세션 생성
    try:
        yield db  # API 함수에 세션을 전달
    finally:
        db.close()  # 요청 처리가 끝나면 세션을 닫음