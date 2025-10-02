#include "CircularBuffer.h" 
#include <iostream>
#include <string>
#include <numeric>   
#include <algorithm> 
#include <vector>    
#include <iomanip>   


int main() {
    // --- 1. 객체 생성 ---
    // double 타입의 데이터를 저장하고, 최대 용량(capacity)이 5인 CircularBuffer 객체를 생성합니다.
    // 변수 이름은 tempBuffer로 지정합니다.
    CircularBuffer<double> tempBuffer(5);

    // --- 2. 데이터 추가 ---
    // push_back 메서드를 사용하여 버퍼의 끝에 데이터를 순서대로 추가합니다.
    tempBuffer.push_back(23.5); // size: 1
    tempBuffer.push_back(24.1); // size: 2
    tempBuffer.push_back(23.8); // size: 3
    tempBuffer.push_back(25.2); // size: 4
    tempBuffer.push_back(24.7); // size: 5 (이제 버퍼가 가득 찼습니다)
    
    // 6번째 데이터를 추가합니다. 버퍼 용량이 5이므로, 가장 먼저 들어왔던(가장 오래된)
    // 데이터인 23.5가 제거되고 그 자리에 26.1이 덮어써집니다.
    tempBuffer.push_back(26.1); 

    // --- 3. STL 알고리즘 활용 ---
    // 우리가 만든 CircularBuffer가 STL(Standard Template Library)과 얼마나 잘 호환되는지 보여줍니다.

    // 최댓값을 저장할 변수를 선언하고 0.0으로 초기화합니다.
    double maxTemp = 0.0;
    // 버퍼가 비어있지 않은 경우에만 최댓값을 찾습니다. (빈 버퍼에서 찾으면 에러 발생)
    if (!tempBuffer.empty()) {
        // std::max_element는 begin()부터 end()까지 순회하며 가장 큰 값을 가리키는 '반복자'를 반환합니다.
        // 앞에 '*'를 붙여서 그 반복자가 가리키는 실제 값(최댓값)을 가져옵니다.
        maxTemp = *std::max_element(tempBuffer.begin(), tempBuffer.end());
    }
    
    // 평균값을 저장할 변수를 선언하고 0.0으로 초기화합니다.
    double avgTemp = 0.0;
    // 버퍼가 비어있지 않은 경우에만 평균을 계산합니다.
    if (!tempBuffer.empty()) {
        // std::accumulate는 begin()부터 end()까지 모든 요소의 합계를 계산합니다.
        // 0.0은 합계를 시작할 초기값입니다.
        // 계산된 총합을 버퍼의 현재 크기(size)로 나누어 평균을 구합니다.
        avgTemp = std::accumulate(tempBuffer.begin(), tempBuffer.end(), 0.0) / tempBuffer.size();
    }


    // --- 4. 결과 출력 ---
    // 테스트 결과를 콘솔 화면에 출력합니다.
    std::cout << "begin()부터 순회 시: ";
    // 범위 기반 for문(range-based for loop)입니다.
    // CircularBuffer에 begin()과 end()가 올바르게 구현되어 있기 때문에 이 간편한 문법을 사용할 수 있습니다.
    // tempBuffer 안의 모든 요소를 처음부터 끝까지 순서대로 val 변수에 담아 반복합니다.
    for (const auto& val : tempBuffer) {
        std::cout << val << " ";
    }
    std::cout << "(가장 오래된 것부터)" << std::endl;
    std::cout << std::endl; // 가독성을 위해 빈 줄을 하나 출력합니다.

    // 버퍼의 상태 정보를 출력합니다.
    std::cout << "tempBuffer.size() = " << tempBuffer.size() << std::endl;
    std::cout << "tempBuffer.capacity() = " << tempBuffer.capacity() << std::endl;
    // 삼항 연산자: tempBuffer.empty()가 true이면 "true" 문자열을, false이면 "false" 문자열을 출력합니다.
    std::cout << "tempBuffer.empty() = " << (tempBuffer.empty() ? "true" : "false") << std::endl;
    
    // 계산된 최댓값과 평균값을 출력합니다.
    std::cout << "maxTemp = " << maxTemp << std::endl;
    // std::fixed는 소수점을 고정 형식으로, std::setprecision(2)는 소수점 이하 2자리까지 표시하도록 설정합니다.
    std::cout << "avgTemp = " << std::fixed << std::setprecision(2) << avgTemp << std::endl;

    // 버퍼의 첫 번째와 마지막 요소를 출력하여 front()와 back() 메서드가 올바르게 동작하는지 확인합니다.
    std::cout << "tempBuffer.front() = " << tempBuffer.front() << " // 가장 오래된 데이터" << std::endl;
    std::cout << "tempBuffer.back() = " << tempBuffer.back() << " // 가장 최근 데이터" << std::endl;

    // 프로그램이 정상적으로 종료되었음을 운영체제에 알립니다. (0은 보통 성공을 의미)
    return 0;
}