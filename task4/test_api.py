import requests
import json

base_url = "http://localhost:8000"

def pretty_print(response):
    """JSON 응답을 예쁘게 출력하는 함수"""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    except json.JSONDecodeError:
        print(response.text)
    print("-" * 30)

# 1. 회원가입
print("1. 회원가입 요청...")
signup_data = {
    "username": "john_doe",
    "email": "john@example.com", # 이메일 형식 수정
    "password": "securepass123",
    "full_name": "John Doe"
}
response = requests.post(f"{base_url}/auth/signup", json=signup_data)
pretty_print(response)

# 2. 로그인
print("2. 로그인 요청...")
login_data = {"username": "john_doe", "password": "securepass123"} # 'usename' 오타 수정
auth_response = requests.post(f"{base_url}/auth/login", data=login_data) # json=이 아닌 data=로 전송 (OAuth2PasswordRequestForm)
pretty_print(auth_response)
token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 3. 새 도서 추가
print("3. 새 도서 추가 요청...")
book_data = {
    "title": "Python Programming",
    "author": "John Smith",
    "isbn": "978-0123456789",
    "category": "Programming",
    "total_copies": 5
}
# admin_headers 대신 일반 로그인 헤더 사용
response = requests.post(f"{base_url}/books", json=book_data, headers=headers)
pretty_print(response)
book_id = response.json()["id"]

# 4. 도서 검색
print("4. 도서 검색 요청 (카테고리: Programming, 대출 가능)...")
search_response = requests.get(f"{base_url}/books?category=Programming&available=true")
pretty_print(search_response)

# 5. 도서 대출
print("5. 도서 대출 요청...")
# 실제 대출 시에는 user_id를 body에 담지 않고, 토큰을 통해 서버가 식별합니다.
borrow_data = {"book_id": book_id}
response = requests.post(f"{base_url}/loans", json=borrow_data, headers=headers)
pretty_print(response)

# 6. 내 대출 목록 조회
print("6. 내 대출 목록 조회 요청...")
loans_response = requests.get(f"{base_url}/users/me/loans", headers=headers)
pretty_print(loans_response)