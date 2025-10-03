# 파일: test_api.py
# FastAPI로 만든 도서관 API 서버의 기능이 정상적으로 동작하는지 테스트하는 스크립트입니다.
# requests 라이브러리를 사용하여 실제 HTTP 요청을 보내고 응답을 확인합니다.

# --- 필요한 라이브러리 임포트 ---
import requests # HTTP 요청을 보내기 위한 라이브러리
import json     # JSON 데이터를 다루기 위한 라이브러리 (여기서는 예쁘게 출력하기 위해 사용)

# --- 기본 설정 ---
# 테스트할 API 서버의 기본 URL을 지정합니다.
base_url = "http://localhost:8000"

def pretty_print(response):
    """
    API 서버로부터 받은 응답(Response) 객체를 보기 좋게 출력하는 함수입니다.
    - HTTP 상태 코드를 먼저 출력합니다.
    - 응답 본문(body)이 JSON 형식일 경우, 들여쓰기를 적용하여 예쁘게 출력합니다.
    - JSON 형식이 아닐 경우, 텍스트 그대로 출력합니다.
    """
    print(f"Status Code: {response.status_code}")
    try:
        # 응답을 JSON으로 변환하고, indent(들여쓰기)와 ensure_ascii=False(한글 깨짐 방지) 옵션을 적용하여 출력
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    except json.JSONDecodeError:
        # JSON으로 변환 실패 시, 받은 텍스트를 그대로 출력
        print(response.text)
    print("-" * 30) # 각 요청 결과를 구분하기 위한 구분선 출력

# ===============================================================
# --- API 기능 테스트 시작 ---
# ===============================================================

# --- 1. 회원가입 테스트 ---
print("1. 회원가입 요청...")
# 회원가입에 필요한 사용자 정보를 딕셔너리 형태로 준비합니다.
signup_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
}
# POST /auth/signup 엔드포인트에 준비된 사용자 정보를 JSON 형식으로 담아 요청을 보냅니다.
response = requests.post(f"{base_url}/auth/signup", json=signup_data)
pretty_print(response) # 응답 결과를 출력합니다.

# --- 2. 로그인 테스트 ---
print("2. 로그인 요청...")
# 로그인을 위한 사용자 이름과 비밀번호를 딕셔너리 형태로 준비합니다.
login_data = {"username": "john_doe", "password": "securepass123"}
# POST /auth/login 엔드포인트에 로그인 정보를 data (form 형식)로 담아 요청을 보냅니다.
# (FastAPI의 OAuth2PasswordRequestForm은 json이 아닌 form 데이터를 기대합니다)
auth_response = requests.post(f"{base_url}/auth/login", data=login_data)
pretty_print(auth_response) # 응답 결과를 출력합니다.

# 로그인 성공 시, 응답으로 받은 JSON에서 'access_token' 값을 추출합니다.
token = auth_response.json()["access_token"]
# 이후 인증이 필요한 요청에 사용하기 위해 HTTP 헤더를 구성합니다.
# "Authorization": "Bearer [토큰값]" 형식으로 만듭니다.
headers = {"Authorization": f"Bearer {token}"}

# --- 3. 새 도서 추가 테스트 (인증 필요) ---
print("3. 새 도서 추가 요청...")
# 데이터베이스에 추가할 새로운 도서 정보를 딕셔너리 형태로 준비합니다.
book_data = {
    "title": "Python Programming",
    "author": "John Smith",
    "isbn": "978-0123456789",
    "category": "Programming",
    "total_copies": 5
}
# POST /books 엔드포인트에 도서 정보를 JSON으로 담고, 인증을 위해 위에서 만든 헤더를 포함하여 요청합니다.
response = requests.post(f"{base_url}/books", json=book_data, headers=headers)
pretty_print(response) # 응답 결과를 출력합니다.

# 도서 추가 성공 시, 응답으로 받은 책 정보에서 'id' 값을 추출합니다.
# 이 ID는 이후 '도서 대출' 테스트에서 사용됩니다.
book_id = response.json()["id"]

# --- 4. 도서 검색 테스트 ---
print("4. 도서 검색 요청 (카테고리: Programming, 대출 가능)...")
# GET /books 엔드포인트에 쿼리 파라미터를 사용하여 특정 조건의 책을 검색합니다.
# URL 뒤에 ?key=value&key=value 형식으로 추가합니다.
search_response = requests.get(f"{base_url}/books?category=Programming&available=true")
pretty_print(search_response) # 응답 결과를 출력합니다.

# --- 5. 도서 대출 테스트 (인증 필요) ---
print("5. 도서 대출 요청...")
# 대출할 책의 ID를 딕셔너리에 담아 준비합니다.
borrow_data = {"book_id": book_id}
# POST /loans 엔드포인트에 대출 정보를 JSON으로 담고, 인증 헤더를 포함하여 요청합니다.
response = requests.post(f"{base_url}/loans", json=borrow_data, headers=headers)
pretty_print(response) # 응답 결과를 출력합니다.

# --- 6. 내 대출 목록 조회 테스트 (인증 필요) ---
print("6. 내 대출 목록 조회 요청...")
# GET /users/me/loans 엔드포인트에 인증 헤더를 포함하여 요청합니다.
# 서버는 헤더의 토큰을 보고 '나(me)'가 누구인지 식별하여 해당 사용자의 대출 목록을 반환합니다.
loans_response = requests.get(f"{base_url}/users/me/loans", headers=headers)
pretty_print(loans_response) # 응답 결과를 출력합니다.