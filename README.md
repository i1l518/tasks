# RGT 로봇 응용 SW 개발자 직무 면접 전 과제

이 문서는 ㈜알지티의 로봇 응용 SW 개발자 직무 면접 전 과제에 대한 안내서입니다. 각 과제의 개발 환경, 사전 준비 사항, 그리고 상세한 빌드 및 실행 방법을 포함하고 있습니다.

## 📝 목차 (Table of Contents)

*   [**환경설정**](#환경설정)
    *   [C++ (Task 1, 2, 3)](#c-task-1-2-3)
    *   [Python (Task 4)](#python-task-4)
    *   [Python (Task 5)](#python-task-5)
*   [**빌드 및 실행 방법**](#빌드-및-실행-방법)
    *   [Task 1](#task-1)
    *   [Task 2](#task-2)
    *   [Task 3](#task-3)
    *   [Task 4](#task-4)
    *   [Task 5](#task-5)

---

## 💻 환경설정

이 섹션에서는 각 과제를 수행하기 위해 필요한 개발 환경 및 사전 준비 사항을 안내합니다.

### C++ 과제 (Task 1, 2, 3)

1.  **Visual Studio Code:** 코드 편집 및 터미널 실행을 위해 필요합니다.
2.  **MinGW-w64 (g++ 컴파일러):** C++ 코드를 컴파일하기 위해 필요합니다.
    *   **중요:** 설치 후, 컴파일러의 `bin` 폴더 (예: `C:\msys64\mingw64\bin`)가 시스템 환경 변수 `Path`에 추가되어 있어야 터미널에서 `g++` 명령어를 인식할 수 있습니다.

### Python 과제 (Task 4)

1.  **Python:** [공식 웹사이트](https://www.python.org/downloads/)에서 Python 3.9 이상 버전을 설치합니다.
2.  **가상 환경 설정 (권장):** 프로젝트의 독립성을 위해 가상 환경을 설정합니다.
    ```bash
    # `task4` 폴더로 이동
    cd task4
    # venv 라는 이름의 가상 환경 생성
    python -m venv venv
    # 가상 환경 활성화
    .\venv\Scripts\activate
    ```
3.  **패키지 설치:** `requirements.txt` 파일을 사용하여 API 서버와 클라이언트에 필요한 모든 패키지를 한 번에 설치합니다.
    ```bash
    # `task4` 폴더에 requirements.txt 파일이 있는지 확인 후 아래 명령어 실행
    pip install -r requirements.txt
    ```

### Python 과제 (Task 5)

1.  **Python:** [공식 웹사이트](https://www.python.org/downloads/)에서 Python 3.9 이상 버전을 설치합니다.
2.  **가상 환경 설정:** 프로젝트의 의존성 충돌을 방지하기 위해 가상 환경을 사용합니다.
    ```bash
    # `task5` 폴더로 이동
    cd task5
    # venv 라는 이름의 가상 환경 생성
    python -m venv venv
    # 가상 환경 활성화 (Windows 기준)
    .\venv\Scripts\activate
    ```
3.  **패키지 설치:** `requirements.txt` 파일을 사용하여 API 서버와 클라이언트에 필요한 모든 패키지를 한 번에 설치합니다.
    ```bash
    # `task5` 폴더에 requirements.txt 파일이 있는지 확인 후 아래 명령어 실행
    pip install -r requirements.txt
    ```

---

## 🚀 빌드 및 실행 방법

이 섹션에서는 각 과제를 컴파일하고 실행하는 상세한 방법을 안내합니다.

### Task 1

*   **문제:** 스마트 포인터를 활용한 리소스 관리
*   **소스 파일:** `task1/Problem1.cpp`

#### 방법: 터미널을 이용한 직접 실행
1.  VS Code 터미널에서 `task1` 폴더로 이동합니다: `cd task1`
2.  컴파일 명령어: `g++ -o Problem1.exe Problem1.cpp`
3.  실행 명령어: `./Problem1.exe`

### Task 2

*   **문제:** 템플릿과 STL을 활용한 컨테이너 설계
*   **소스 파일:** `task2/Problem2.cpp` (예시 파일명)

#### 방법: 터미널을 이용한 직접 실행
1.  VS Code 터미널에서 `task2` 폴더로 이동합니다: `cd task2`
2.  컴파일 명령어: `g++ -o Problem2.exe Problem2.cpp`
3.  실행 명령어: `./Problem2.exe`

### Task 3

*   **문제:** 멀티스레딩과 함수형 프로그래밍을 활용한 병렬 처리
*   **소스 파일:** `task3/Problem3.cpp` (예시 파일명)

#### 방법: 터미널을 이용한 직접 실행
1.  VS Code 터미널에서 `task3` 폴더로 이동합니다: `cd task3`
2.  컴파일 명령어: `g++ -o Problem3.exe Problem3.cpp -pthreads`
3.  실행 명령어: `./Problem3.exe`

### Task 4

*   **문제:** Python RESTful API 서버 구현
*   **소스 파일:** `task4/main.py` (예시 파일명)

1.  VS Code 터미널에서 `task4` 폴더로 이동합니다: `cd task4`
2.  **(최초 1회)** 위 `환경설정`에 따라 Python 가상 환경을 설정하고 패키지를 설치합니다.
3.  가상 환경을 활성화합니다: `.\venv\Scripts\activate`
4.  FastAPI 개발 서버를 실행합니다: `uvicorn main:app --reload`
5.  서버가 `http://12.7.0.0.1:8000` 에서 실행되면, 웹 브라우저나 별도의 테스트 스크립트로 API를 호출할 수 있습니다.

### Task 5

*   **문제:** JWT 인증을 포함한 Python RESTful API 서버 및 클라이언트 구현
*   **소스 파일:** `task5/main.py`, `task5/client.py`
*   **실행 순서:** 반드시 API 서버(`main.py`)를 먼저 실행한 후, 클라이언트(`client.py`)를 실행해야 합니다.

#### 1. API 서버 실행
1.  VS Code에서 **첫 번째 터미널**을 엽니다.
2.  `task5` 폴더로 이동합니다: `cd task5`
3.  **(최초 1회)** 위 `환경설정`에 따라 가상 환경 설정 및 패키지 설치를 진행합니다.
4.  가상 환경을 활성화합니다: `.\venv\Scripts\activate`
5.  FastAPI 개발 서버를 실행합니다: `uvicorn main:app --reload`
6.  서버가 `http://127.0.0.1:8000` 에서 실행되면 **이 터미널은 그대로 둡니다.**

#### 2. 클라이언트 실행 (서버가 켜진 상태에서 진행)
1.  VS Code에서 **새로운 두 번째 터미널**을 엽니다. (기존 터미널 옆 `+` 아이콘 클릭)
2.  두 번째 터미널에서 `task5` 폴더로 이동합니다: `cd task5`
3.  두 번째 터미널에서도 가상 환경을 활성화합니다: `.\venv\Scripts\activate`
4.  테스트 클라이언트 스크립트를 실행합니다: `python client.py`
5.  클라이언트 터미널에 회원가입, 로그인, 도서 추가 등의 API 테스트 결과가 순차적으로 출력됩니다. 서버 터미널에는 클라이언트로부터 들어온 요청 로그가 출력됩니다.