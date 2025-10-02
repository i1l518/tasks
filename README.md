\# RGT 로봇 응용 SW 개발자 직무 면접 전 과제



이 문서는 ㈜알지티의 로봇 응용 SW 개발자 직무 면접 전 과제에 대한 안내서입니다. 각 과제의 개발 환경, 사전 준비 사항, 그리고 상세한 빌드 및 실행 방법을 포함하고 있습니다.



\## 📝 목차 (Table of Contents)



1\.  \[Task 1: 스마트 포인터를 활용한 리소스 관리](#task-1-스마트-포인터를-활용한-리소스-관리)

2\.  \[Task 2: 템플릿과 STL을 활용한 컨테이너 설계](#task-2-템플릿과-stl을-활용한-컨테이너-설계)

3\.  \[Task 3: 멀티스레딩과 함수형 프로그래밍을 활용한 병렬 처리](#task-3-멀티스레딩과-함수형-프로그래밍을-활용한-병렬-처리)

4\.  \[Task 4: Python RESTful API 서버 구현](#task-4-python-restful-api-서버-구현)



---



\## 💻 개발 환경 (Development Environment)



\*   \*\*운영체제 (OS):\*\* Windows 11

\*   \*\*코드 편집기 (IDE):\*\* Visual Studio Code

\*   \*\*C++ 컴파일러 (Compiler):\*\* g++ (MinGW-w64)

\*   \*\*Python 버전:\*\* Python 3.9+



---



\## 🛠 사전 준비 사항 (Prerequisites)



\### C++ 과제 (Task 1, 2, 3)



1\.  \*\*Visual Studio Code:\*\* 코드 편집 및 터미널 실행을 위해 필요합니다.

2\.  \*\*MinGW-w64 (g++ 컴파일러):\*\* C++ 코드를 컴파일하기 위해 필요합니다.

&nbsp;   \*   \*\*중요:\*\* 설치 후, 컴파일러의 `bin` 폴더 (예: `C:\\msys64\\mingw64\\bin`)가 시스템 환경 변수 `Path`에 추가되어 있어야 터미널에서 `g++` 명령어를 인식할 수 있습니다.



\### Python 과제 (Task 4)



1\.  \*\*Python:\*\* \[공식 웹사이트](https://www.python.org/downloads/)에서 Python 3.9 이상 버전을 설치합니다.

2\.  \*\*가상 환경 설정 (권장):\*\* 프로젝트의 독립성을 위해 가상 환경을 설정합니다.

&nbsp;   ```bash

&nbsp;   # `과제4` 폴더로 이동

&nbsp;   cd 과제4

&nbsp;   # venv 라는 이름의 가상 환경 생성

&nbsp;   python -m venv venv

&nbsp;   # 가상 환경 활성화

&nbsp;   .\\venv\\Scripts\\activate

&nbsp;   ```

3\.  \*\*패키지 설치:\*\* API 서버 구동에 필요한 패키지들을 설치합니다.

&nbsp;   ```bash

&nbsp;   pip install fastapi uvicorn

&nbsp;   ```



---



\## 🚀 빌드 및 실행 방법 (How to Build and Run)



\### Task 1: 스마트 포인터를 활용한 리소스 관리



\*   \*\*소스 파일:\*\* `과제1/Problem1.cpp`



\#### 방법 A: VS Code의 Task 기능 이용 (권장)



1\.  VS Code에서 `과제.code-workspace` 파일을 엽니다.

2\.  `과제1/Problem1.cpp` 파일을 클릭하여 편집기 창을 활성화합니다.

3\.  `F5` 키를 누르면 자동으로 컴파일 및 실행이 진행됩니다.



\#### 방법 B: 터미널을 이용한 직접 실행



1\.  VS Code 터미널을 열고 `과제1` 폴더로 이동합니다.

&nbsp;   ```bash

&nbsp;   cd 과제1

&nbsp;   ```

2\.  아래 명령어로 코드를 컴파일하여 `Problem1.exe` 실행 파일을 생성합니다.

&nbsp;   ```bash

&nbsp;   g++ -o Problem1.exe Problem1.cpp

&nbsp;   ```

3\.  아래 명령어로 프로그램을 실행합니다.

&nbsp;   ```bash

&nbsp;   ./Problem1.exe

&nbsp;   ```



---



\### Task 2: 템플릿과 STL을 활용한 컨테이너 설계



\*   \*\*소스 파일:\*\* `과제2/Problem2.cpp` (예시 파일명)



\#### 방법 A: VS Code의 Task 기능 이용 (권장)



1\.  VS Code에서 `과제.code-workspace` 파일을 엽니다.

2\.  `과제2/Problem2.cpp` 파일을 클릭하여 편집기 창을 활성화합니다.

3\.  `F5` 키를 누르면 자동으로 컴파일 및 실행이 진행됩니다.



\#### 방법 B: 터미널을 이용한 직접 실행



1\.  VS Code 터미널을 열고 `과제2` 폴더로 이동합니다.

&nbsp;   ```bash

&nbsp;   cd 과제2

&nbsp;   ```

2\.  아래 명령어로 코드를 컴파일하여 `Problem2.exe` 실행 파일을 생성합니다.

&nbsp;   ```bash

&nbsp;   g++ -o Problem2.exe Problem2.cpp

&nbsp;   ```

3\.  아래 명령어로 프로그램을 실행합니다.

&nbsp;   ```bash

&nbsp;   ./Problem2.exe

&nbsp;   ```



---



\### Task 3: 멀티스레딩과 함수형 프로그래밍을 활용한 병렬 처리



\*   \*\*소스 파일:\*\* `과제3/Problem3.cpp` (예시 파일명)



\#### 방법 A: VS Code의 Task 기능 이용 (권장)



1\.  VS Code에서 `과제.code-workspace` 파일을 엽니다.

2\.  `과제3/Problem3.cpp` 파일을 클릭하여 편집기 창을 활성화합니다.

3\.  `F5` 키를 누르면 자동으로 컴파일 및 실행이 진행됩니다.



\#### 방법 B: 터미널을 이용한 직접 실행



1\.  VS Code 터미널을 열고 `과제3` 폴더로 이동합니다.

&nbsp;   ```bash

&nbsp;   cd 과제3

&nbsp;   ```

2\.  아래 명령어로 코드를 컴파일하여 `Problem3.exe` 실행 파일을 생성합니다. (멀티스레딩 코드는 `-pthreads` 옵션 추가가 필요할 수 있습니다)

&nbsp;   ```bash

&nbsp;   g++ -o Problem3.exe Problem3.cpp -pthreads

&nbsp;   ```

3\.  아래 명령어로 프로그램을 실행합니다.

&nbsp;   ```bash

&nbsp;   ./Problem3.exe

&nbsp;   ```



---



\### Task 4: Python RESTful API 서버 구현



\*   \*\*소스 파일:\*\* `과제4/main.py` (예시 파일명)



1\.  VS Code 터미널을 열고 `과제4` 폴더로 이동합니다.

&nbsp;   ```bash

&nbsp;   cd 과제4

&nbsp;   ```

2\.  \*\*(최초 1회)\*\* 위 `사전 준비 사항`에 따라 Python 가상 환경을 설정하고 패키지를 설치합니다. 이미 했다면 건너뜁니다.

3\.  가상 환경을 활성화합니다.

&nbsp;   ```bash

&nbsp;   .\\venv\\Scripts\\activate

&nbsp;   ```

4\.  아래 명령어를 입력하여 FastAPI 개발 서버를 실행합니다.

&nbsp;   ```bash

&nbsp;   uvicorn main:app --reload

&nbsp;   ```

5\.  서버가 `http://127.0.0.1:8000` 에서 실행됩니다. 과제 설명에 나온 `입력 파이선 파일`을 실행하거나 웹 브라우저, Postman 등으로 API를 테스트할 수 있습니다.

