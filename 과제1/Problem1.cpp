#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <chrono>
#include <iomanip>
#include <stdexcept>

class LogFileManager {
public:
    LogFileManager() = default;
    ~LogFileManager() = default;

    // 복사 생성자 삭제
    LogFileManager(const LogFileManager&) = delete;
    // 복사 대입 연산자 삭제
    LogFileManager& operator=(const LogFileManager&) = delete;

    // 이동 생성자
    LogFileManager(LogFileManager&& other) noexcept = default;
    // 이동 대입 연산자
    LogFileManager& operator=(LogFileManager&& other) noexcept = default;

    // 로그 파일을 엽니다.
    void openLogFile(const std::string& filename) {
        auto logFile = std::make_unique<std::ofstream>(filename, std::ios_base::app);
        if (!logFile->is_open()) {
            throw std::runtime_error("Failed to open file: " + filename);
        }
        logFiles[filename] = std::move(logFile);
    }

    // 로그 파일에 메시지를 기록합니다.
    void writeLog(const std::string& filename, const std::string& message) {
        auto it = logFiles.find(filename);
        if (it != logFiles.end() && it->second && it->second->is_open()) {
            auto now = std::chrono::system_clock::now();
            auto in_time_t = std::chrono::system_clock::to_time_t(now);
            
            // 타임스탬프 형식 지정
            std::stringstream ss;
            ss << std::put_time(std::localtime(&in_time_t), "[%Y-%m-%d %X]");
            
            *(it->second) << ss.str() << " " << message << std::endl;
        } else {
            throw std::runtime_error("File not open or not found: " + filename);
        }
    }

    // 로그 파일의 내용을 읽어 반환합니다.
    std::vector<std::string> readLogs(const std::string& filename) {
        // 쓰기용으로 열려있는 파일을 닫고 읽기용으로 다시 엽니다.
        closeLogFile(filename);

        std::vector<std::string> logs;
        std::ifstream logFile(filename);
        if (!logFile.is_open()) {
            // 파일을 다시 쓰기 모드로 엽니다.
            openLogFile(filename);
            throw std::runtime_error("Failed to open file for reading: " + filename);
        }

        std::string line;
        while (std::getline(logFile, line)) {
            logs.push_back(line);
        }
        logFile.close();

        // 파일을 다시 쓰기 모드로 엽니다.
        openLogFile(filename);

        return logs;
    }

    // 로그 파일을 닫습니다.
    void closeLogFile(const std::string& filename) {
        auto it = logFiles.find(filename);
        if (it != logFiles.end()) {
            logFiles.erase(it);
        }
    }

private:
    std::map<std::string, std::unique_ptr<std::ofstream>> logFiles;
};

int main() {
    try {
        LogFileManager manager;
        manager.openLogFile("error.log");
        manager.openLogFile("debug.log");
        manager.openLogFile("info.log");

        manager.writeLog("error.log", "Database connection failed");
        manager.writeLog("debug.log", "User login attempt");
        manager.writeLog("info.log", "Server started successfully");

        std::vector<std::string> errorLogs = manager.readLogs("error.log");

        for (const auto& log : errorLogs) {
            std::cout << log << std::endl;
        }

        manager.closeLogFile("error.log");
        manager.closeLogFile("debug.log");
        manager.closeLogFile("info.log");

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}