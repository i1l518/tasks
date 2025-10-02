from fastapi import FastAPI
from app import models  # app 폴더 안의 models를 불러옴
from app.database import engine
from app.routers import users, books

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 라우터 포함
app.include_router(users.router)
app.include_router(books.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Online Library API"}