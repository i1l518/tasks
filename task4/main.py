"""
FastAPI 애플리케이션의 메인 실행 파일입니다.
앱 인스턴스를 생성하고, 데이터베이스 테이블을 초기화하며, 각 기능별 라우터를 앱에 포함시킵니다.
"""
from fastapi import FastAPI
from app import models  # app 폴더의 models.py를 가져옴
from app.database import engine, SessionLocal # app 폴더의 database.py에서 engine을 가져옴
from app.routers import users, books  # app/routers 폴더에서 users.py와 books.py의 라우터를 가져옴

# 애플리케이션 시작 시, models.py에 정의된 모든 테이블을 데이터베이스에 생성합니다.
# 이미 테이블이 존재한다면 아무 동작도 하지 않습니다.
models.Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스를 생성합니다.
app = FastAPI()

# app/routers/users.py 파일에 정의된 API 엔드포인트들을 메인 앱에 포함시킵니다.
app.include_router(users.router)
# app/routers/books.py 파일에 정의된 API 엔드포인트들을 메인 앱에 포함시킵니다.
app.include_router(books.router)

# 루트 경로 ("/")로 GET 요청이 왔을 때 실행될 함수를 정의합니다.
# 서버가 정상적으로 실행 중인지 확인하는 용도로 사용할 수 있습니다.
@app.get("/")
def read_root():
    return {"message": "Welcome to the Online Library API"}