import json
import requests

# 테스트할 FastAPI 서버의 기본 주소입니다.
BASE_URL = "http://127.0.0.1:8000"

def pretty_print_response(response):
    """
    서버로부터 받은 응답(response)을 보기 좋게 출력하는 도우미 함수입니다.
    상태 코드와 JSON 형식의 본문을 출력합니다.
    """
    print(f"Status Code: {response.status_code}")
    try:
        # 응답 본문을 JSON으로 파싱하여 예쁘게 출력
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        # JSON이 아닌 경우 그냥 텍스트로 출력
        print("Response Body (not JSON):")
        print(response.text)
    print("-" * 30)  # 각 요청을 구분하기 위한 구분선


# --- 시나리오 시작 ---

# --- 1. 사용자 회원가입 ---
print(">>> 1. Signing up a new user 'john_doe'...")
# 회원가입에 필요한 데이터를 딕셔너리 형태로 정의합니다.
signup_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "full_name": "John Doe",
}
# '/auth/signup' 엔드포인트에 POST 요청을 보냅니다.
response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
# 서버의 응답을 출력합니다.
pretty_print_response(response)


# --- 2. 일반 사용자 및 관리자 로그인 ---
print(">>> 2. Logging in as 'john_doe'...")
# 로그인을 위해 사용자 이름과 비밀번호를 form-data 형식으로 준비합니다.
# OAuth2PasswordRequestForm은 json이 아닌 data(form) 형식을 기대합니다.
login_data_user = {"username": "john_doe", "password": "securepass123"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data_user)
pretty_print_response(response)
# 로그인 성공 시, 이후 요청에 사용될 토큰을 변수에 저장합니다.
user_token = response.json().get("access_token") if response.ok else None
user_headers = {"Authorization": f"Bearer {user_token}"} if user_token else {}

print(">>> 2.1. Logging in as 'admin'...")
# 서버 시작 시 자동으로 생성된 'admin' 계정으로 로그인합니다.
login_data_admin = {"username": "admin", "password": "adminpass"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data_admin)
pretty_print_response(response)
# 관리자 권한이 필요한 요청에 사용될 관리자 토큰을 저장합니다.
admin_token = response.json().get("access_token") if response.ok else None
admin_headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}


# --- 3. 도서 추가 (관리자 권한 필요) ---
# 관리자 로그인이 성공했을 경우에만 이 블록을 실행합니다.
if admin_token:
    print(">>> 3. Creating a new book (as admin)...")
    book_data = {
        "title": "Python Programming",
        "author": "John Smith",
        "isbn": "978-0123456789",
        "category": "Programming",
        "total_copies": 5,
    }
    # 요청 헤더에 관리자 토큰을 포함하여 POST 요청을 보냅니다.
    response = requests.post(f"{BASE_URL}/books", json=book_data, headers=admin_headers)
    pretty_print_response(response)
    # 나중에 대출 테스트에 사용하기 위해 생성된 책의 ID를 저장합니다.
    created_book_id = response.json().get("id") if response.ok else None
else:
    print("Admin login failed, skipping book creation.")
    created_book_id = None


# --- 4. 도서 검색 ---
print(">>> 4. Searching for available 'Programming' books...")
# URL 쿼리 파라미터로 검색 조건을 전달합니다. (예: /books?category=Programming&available=true)
params = {"category": "Programming", "available": True}
response = requests.get(f"{BASE_URL}/books", params=params)
pretty_print_response(response)


# --- 5. 도서 대출 (일반 사용자) ---
# 일반 사용자 로그인이 성공했고, 이전에 책이 성공적으로 생성되었을 경우에만 실행합니다.
if user_token and created_book_id:
    print(f">>> 5. Borrowing book with ID {created_book_id} (as 'john_doe')...")
    # 대출할 책의 ID를 요청 본문에 담아 보냅니다.
    borrow_data = {"book_id": created_book_id}
    # 요청 헤더에 일반 사용자('john_doe')의 토큰을 포함하여 POST 요청을 보냅니다.
    response = requests.post(f"{BASE_URL}/loans", json=borrow_data, headers=user_headers)
    pretty_print_response(response)
else:
    print("User login or book creation failed, skipping book borrowing.")


# --- 6. 내 대출 목록 조회 (일반 사용자) ---
# 일반 사용자 로그인이 성공했을 경우에만 실행합니다.
if user_token:
    print(">>> 6. Viewing 'john_doe's' loans...")
    # 헤더에 사용자 토큰을 포함하여 GET 요청을 보내 자신의 대출 목록을 요청합니다.
    response = requests.get(f"{BASE_URL}/users/me/loans", headers=user_headers)
    pretty_print_response(response)
else:
    print("User login failed, skipping loan viewing.")