import json
import requests

BASE_URL = "http://127.0.0.1:8000"

def pretty_print_response(response):
    """Helper function to print response status and JSON body."""
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("Response Body (not JSON):")
        print(response.text)
    print("-" * 30)


# --- 1. 사용자 회원가입 ---
print(">>> 1. Signing up a new user 'john_doe'...")
signup_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "full_name": "John Doe",
}
response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
pretty_print_response(response)
john_doe_id = response.json().get("id") if response.ok else None


# --- 2. 일반 사용자 및 관리자 로그인 ---
print(">>> 2. Logging in as 'john_doe'...")
login_data_user = {"username": "john_doe", "password": "securepass123"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data_user)
pretty_print_response(response)
user_token = response.json().get("access_token") if response.ok else None
user_headers = {"Authorization": f"Bearer {user_token}"} if user_token else {}

print(">>> 2.1. Logging in as 'admin'...")
login_data_admin = {"username": "admin", "password": "adminpass"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data_admin)
pretty_print_response(response)
admin_token = response.json().get("access_token") if response.ok else None
admin_headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}


# --- 3. 도서 추가 (관리자 권한 필요) ---
if admin_token:
    print(">>> 3. Creating a new book (as admin)...")
    book_data = {
        "title": "Python Programming",
        "author": "John Smith",
        "isbn": "978-0123456789",
        "category": "Programming",
        "total_copies": 5,
    }
    response = requests.post(f"{BASE_URL}/books", json=book_data, headers=admin_headers)
    pretty_print_response(response)
    created_book_id = response.json().get("id") if response.ok else None
else:
    print("Admin login failed, skipping book creation.")
    created_book_id = None


# --- 4. 도서 검색 ---
print(">>> 4. Searching for available 'Programming' books...")
params = {"category": "Programming", "available": True}
response = requests.get(f"{BASE_URL}/books", params=params)
pretty_print_response(response)


# --- 5. 도서 대출 (일반 사용자) ---
if user_token and created_book_id:
    print(f">>> 5. Borrowing book with ID {created_book_id} (as 'john_doe')...")
    borrow_data = {"book_id": created_book_id}
    response = requests.post(f"{BASE_URL}/loans", json=borrow_data, headers=user_headers)
    pretty_print_response(response)
else:
    print("User login or book creation failed, skipping book borrowing.")


# --- 6. 내 대출 목록 조회 (일반 사용자) ---
if user_token:
    print(">>> 6. Viewing 'john_doe's' loans...")
    response = requests.get(f"{BASE_URL}/users/me/loans", headers=user_headers)
    pretty_print_response(response)
else:
    print("User login failed, skipping loan viewing.")