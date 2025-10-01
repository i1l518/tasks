#include "CircularBuffer.h" // 위 코드를 이 파일명으로 저장
#include <iostream>
#include <string>
#include <numeric>   // std::accumulate를 위해 필요
#include <algorithm> // std::max_element를 위해 필요
#include <vector>    // 비교용 (필요 시)
#include <iomanip>   // 소수점 출력을 위해 필요

int main() {
    // 테스트 시나리오
    CircularBuffer<double> tempBuffer(5);

    // 온도 센서 데이터 추가
    tempBuffer.push_back(23.5);
    tempBuffer.push_back(24.1);
    tempBuffer.push_back(23.8);
    tempBuffer.push_back(25.2);
    tempBuffer.push_back(24.7);
    tempBuffer.push_back(26.1); // 버퍼가 가득 참 - 가장 오래된 값(23.5) 오버라이트

    // STL 사용
    // begin()과 end()가 올바르게 구현되어 STL 알고리즘과 호환됨
    double maxTemp = 0.0;
    if (!tempBuffer.empty()) {
        maxTemp = *std::max_element(tempBuffer.begin(), tempBuffer.end());
    }
    
    double avgTemp = 0.0;
    if (!tempBuffer.empty()) {
        avgTemp = std::accumulate(tempBuffer.begin(), tempBuffer.end(), 0.0) / tempBuffer.size();
    }


    // --- 출력 (제공된 예시와 최대한 유사하게) ---
    std::cout << "begin()부터 순회 시: ";
    for (const auto& val : tempBuffer) {
        std::cout << val << " ";
    }
    std::cout << "(가장 오래된 것부터)" << std::endl;
    std::cout << std::endl;

    std::cout << "tempBuffer.size() = " << tempBuffer.size() << std::endl;
    std::cout << "tempBuffer.capacity() = " << tempBuffer.capacity() << std::endl;
    std::cout << "tempBuffer.empty() = " << (tempBuffer.empty() ? "true" : "false") << std::endl;
    std::cout << "maxTemp = " << maxTemp << std::endl;
    // std::fixed와 std::setprecision을 사용하여 소수점 2자리까지 출력
    std::cout << "avgTemp = " << std::fixed << std::setprecision(2) << avgTemp << std::endl;
    std::cout << "tempBuffer.front() = " << tempBuffer.front() << " // 가장 오래된 데이터" << std::endl;
    std::cout << "tempBuffer.back() = " << tempBuffer.back() << " // 가장 최근 데이터" << std::endl;

    return 0;
}