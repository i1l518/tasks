// --- 필요한 도구들을 불러오는 부분 ---
#include <iostream>     
#include <fstream>      
#include <string>       
#include <vector>       
#include <map>          
#include <memory>       
#include <chrono>       
#include <iomanip>      
#include <stdexcept>    

// --- 로그 파일 관리자(LogFileManager) 클래스 설계도 ls---
class LogFileManager {
public: // 'public'은 외부에서 사용할 수 있는 공개 기능들을 의미합니다.

    // 기본 생성자: LogFileManager 객체가 생성될 때 호출됩니다.
    // '= default'는 컴파일러가 알아서 가장 기본적인 형태로 만들어달라는 의미입니다.
    LogFileManager() = default;
    
    // 기본 소멸자: LogFileManager 객체가 사라질 때 호출됩니다.
    ~LogFileManager() = default;

    // --- 복사와 이동에 관한 규칙 (Rule of Five) ---
    // unique_ptr는 '유일한 소유권'을 가지므로 복사가 불가능합니다.
    // 따라서 이 객체 자체를 복사하려는 시도를 원천적으로 차단합니다.
    LogFileManager(const LogFileManager&) = delete;            // 복사 생성자 삭제
    LogFileManager& operator=(const LogFileManager&) = delete; // 복사 대입 연산자 삭제

    // 복사 대신 '소유권 이전(이동)'은 가능하도록 허용합니다.
    LogFileManager(LogFileManager&& other) noexcept = default; // 이동 생성자 기본 구현
    LogFileManager& operator=(LogFileManager&& other) noexcept = default; // 이동 대입 연산자 기본 구현

    /**
     * @brief 로그 파일을 엽니다. 파일은 쓰기 및 내용 추가 모드로 열립니다.
     * @param filename 열고자 하는 파일의 이름 (예: "error.log")
     */
    void openLogFile(const std::string& filename) {
        // make_unique를 사용해 ofstream(파일 쓰기 스트림) 객체를 만들고, unique_ptr에게 소유권을 맡깁니다.
        // std::ios_base::app 옵션은 파일 끝에 내용을 계속 추가하도록 만듭니다.
        auto logFile = std::make_unique<std::ofstream>(filename, std::ios_base::app);
        
        // 파일이 제대로 열렸는지 확인합니다.
        if (!logFile->is_open()) {
            // 열리지 않았다면, 예외(error)를 발생시켜 문제를 알립니다.
            throw std::runtime_error("Failed to open file: " + filename);
        }
        
        // 'logFiles' 맵에 파일 이름을 키(key)로, 파일 관리자(unique_ptr)를 값(value)으로 저장합니다.
        // std::move는 logFile이 가진 소유권을 맵으로 이전시킵니다.
        logFiles[filename] = std::move(logFile);
    }

    /**
     * @brief 지정된 로그 파일에 타임스탬프와 함께 메시지를 기록합니다.
     * @param filename 로그를 기록할 파일의 이름
     * @param message 기록할 내용
     */
    void writeLog(const std::string& filename, const std::string& message) {
        // 맵에서 해당 파일 이름을 가진 파일 관리자를 찾습니다.
        auto it = logFiles.find(filename);
        
        // 파일 관리자를 찾았고, 실제로 파일이 열려있는 상태인지 확인합니다.
        if (it != logFiles.end() && it->second && it->second->is_open()) {
            // 현재 시스템 시간을 가져옵니다.
            auto now = std::chrono::system_clock::now();
            auto in_time_t = std::chrono::system_clock::to_time_t(now);
            
            // stringstream을 이용해 타임스탬프 문자열을 만듭니다.
            std::stringstream ss;
            // "[년-월-일 시:분:초]" 형식으로 시간 포맷을 지정합니다.
            ss << std::put_time(std::localtime(&in_time_t), "[%Y-%m-%d %X]");
            
            // 파일에 "[타임스탬프] 메시지" 형식으로 내용을 씁니다.
            // *(it->second)는 unique_ptr가 가리키는 실제 ofstream 객체를 의미합니다.
            *(it->second) << ss.str() << " " << message << std::endl;
        } else {
            // 파일이 열려있지 않다면 예외를 발생시킵니다.
            throw std::runtime_error("File not open or not found: " + filename);
        }
    }

    /**
     * @brief 지정된 로그 파일의 모든 내용을 읽어와 문자열 목록(vector)으로 반환합니다.
     * @param filename 읽을 파일의 이름
     * @return 파일의 각 줄이 담긴 std::vector<std::string>
     */
    std::vector<std::string> readLogs(const std::string& filename) {
        // 읽기 작업을 하기 전에, 혹시 쓰기용으로 열려있을지 모르는 파일 스트림을 먼저 닫습니다.
        closeLogFile(filename);

        std::vector<std::string> logs; // 파일 내용을 담을 바구니(vector)를 준비합니다.
        std::ifstream logFile(filename); // 이번엔 파일을 읽기 전용(ifstream)으로 엽니다.
        
        // 파일이 읽기용으로 열리지 않았다면,
        if (!logFile.is_open()) {
            // 원래 상태로 되돌리기 위해 다시 쓰기용으로 파일을 열어두고,
            openLogFile(filename);
            // 예외를 발생시킵니다.
            throw std::runtime_error("Failed to open file for reading: " + filename);
        }

        std::string line; // 파일에서 한 줄씩 읽어올 임시 변수
        // 파일의 끝에 도달할 때까지 한 줄씩 읽어오는 것을 반복합니다.
        while (std::getline(logFile, line)) {
            logs.push_back(line); // 읽어온 한 줄을 바구니에 추가합니다.
        }
        logFile.close(); // 읽기 작업이 끝났으므로 파일을 닫습니다.

        // 나중에 다시 로그를 쓸 수 있도록, 파일을 다시 쓰기 모드로 열어둡니다.
        openLogFile(filename);

        return logs; // 내용이 담긴 바구니를 반환합니다.
    }

    /**
     * @brief 지정된 로그 파일을 닫습니다.
     * @param filename 닫을 파일의 이름
     */
    void closeLogFile(const std::string& filename) {
        // 맵에서 해당 파일 이름을 가진 파일 관리자를 찾습니다.
        auto it = logFiles.find(filename);
        if (it != logFiles.end()) {
            // 맵에서 해당 항목을 삭제합니다.
            // 이때 unique_ptr가 소멸되면서 자신이 관리하던 파일 스트림을 자동으로 닫아줍니다.
            logFiles.erase(it);
        }
    }

private: // 'private'은 클래스 내부에서만 사용하는 비공개 변수나 함수를 의미합니다.
    // 파일 이름(string)을 키로, 해당 파일을 제어하는 unique_ptr를 값으로 가지는 맵(서랍)입니다.
    std::map<std::string, std::unique_ptr<std::ofstream>> logFiles;
};

// --- 프로그램의 시작점, main 함수 ---
int main() {
    // try-catch 블록: 코드 실행 중 예외(에러)가 발생하면 프로그램을 안전하게 처리하기 위함입니다.
    try {
        LogFileManager manager; // LogFileManager 객체(관리자 로봇)를 생성합니다.
        
        // 관리할 로그 파일들을 엽니다.
        manager.openLogFile("error.log");
        manager.openLogFile("debug.log");
        manager.openLogFile("info.log");

        // 각 파일에 로그를 기록합니다.
        manager.writeLog("error.log", "Database connection failed");
        manager.writeLog("debug.log", "User login attempt");
        manager.writeLog("info.log", "Server started successfully");

        // "error.log" 파일의 내용을 모두 읽어와 errorLogs 변수에 저장합니다.
        std::vector<std::string> errorLogs = manager.readLogs("error.log");

        // 읽어온 로그들을 한 줄씩 화면에 출력합니다.
        for (const auto& log : errorLogs) {
            std::cout << log << std::endl;
        }

        // 작업이 끝난 파일들을 닫습니다.
        manager.closeLogFile("error.log");
        manager.closeLogFile("debug.log");
        manager.closeLogFile("info.log");

    } catch (const std::exception& e) {
        // try 블록 안에서 예외가 발생하면 이곳으로 이동합니다.
        // 발생한 에러 메시지를 화면에 출력합니다.
        std::cerr << "Error: " << e.what() << std::endl;
    }

    // 프로그램을 정상적으로 종료합니다.
    return 0;
}