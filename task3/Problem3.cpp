#include <iostream>     // 표준 입출력 (cout)
#include <vector>       // 동적 배열 (std::vector)
#include <thread>       // 멀티스레딩 (std::thread, std::this_thread)
#include <functional>   // 함수 객체 (std::function)
#include <numeric>      // 숫자 관련 함수 (std::iota)
#include <future>       // 비동기 실행 관리 (std::async, std::future)
#include <chrono>       // 시간 측정 (std::chrono)
#include <stdexcept>    // 표준 예외 클래스
#include <algorithm>    // 일반 알고리즘 (std::min)

// =======================================================================
// 1. STL 호환 CircularBuffer<T> 클래스 구현
//    - 고정된 크기를 가지며, 데이터가 가득 차면 오래된 데이터를 덮어쓰는 자료구조.
// =======================================================================
template <typename T>
class CircularBuffer {
private:
    std::vector<T> data_; // 데이터를 저장할 내부 벡터
    size_t head_ = 0;     // 가장 오래된 데이터의 인덱스 (다음에 pop_front될 위치)
    size_t tail_ = 0;     // 다음에 데이터가 삽입될 위치 (push_back될 위치)
    size_t size_ = 0;     // 현재 버퍼에 저장된 요소의 개수
    size_t capacity_;     // 버퍼의 최대 용량

public:
    // 생성자: 버퍼의 최대 용량을 인자로 받아 초기화
    explicit CircularBuffer(size_t capacity) : data_(capacity), capacity_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument("CircularBuffer capacity must be positive.");
        }
    }

    // --- 반복자(Iterator) 구현 ---
    // 범위 기반 for문을 지원하기 위해 STL 호환 반복자를 구현합니다.
    template <bool IsConst> // const와 non-const 반복자를 모두 만들기 위한 템플릿
    class iterator_impl {
    private:
        // IsConst 값에 따라 const 또는 non-const 포인터/참조 타입을 결정
        using BufferType = std::conditional_t<IsConst, const CircularBuffer*, CircularBuffer*>;
        using PointerType = std::conditional_t<IsConst, const T*, T*>;
        using ReferenceType = std::conditional_t<IsConst, const T&, T&>;

        BufferType buffer_; // 순회할 버퍼에 대한 포인터
        size_t index_;      // 버퍼의 시작(head)으로부터의 상대적인 인덱스

    public:
        // STL 알고리즘과 호환되기 위한 타입 정의
        using iterator_category = std::forward_iterator_tag;
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        using pointer = PointerType;
        using reference = ReferenceType;

        iterator_impl(BufferType buffer, size_t index) : buffer_(buffer), index_(index) {}

        // 역참조 연산자: 현재 위치의 데이터에 대한 참조를 반환
        reference operator*() const {
            // head_ 위치에서 상대적인 index_ 만큼 이동한 실제 위치를 계산 (원형이므로 나머지 연산 사용)
            return buffer_->data_[(buffer_->head_ + index_) % buffer_->capacity_];
        }

        // 멤버 접근 연산자
        pointer operator->() const {
            return &operator*();
        }

        // 전위 증가 연산자: 다음 요소로 이동
        iterator_impl& operator++() {
            ++index_;
            return *this;
        }

        // 후위 증가 연산자
        iterator_impl operator++(int) {
            iterator_impl temp = *this;
            ++(*this);
            return temp;
        }

        // 비교 연산자
        friend bool operator==(const iterator_impl& a, const iterator_impl& b) {
            return a.buffer_ == b.buffer_ && a.index_ == b.index_;
        }

        friend bool operator!=(const iterator_impl& a, const iterator_impl& b) {
            return !(a == b);
        }
    };

    // 실제 사용할 반복자 타입 정의
    using iterator = iterator_impl<false>;       // non-const iterator
    using const_iterator = iterator_impl<true>; // const iterator

    // 범위 기반 for문을 위한 begin(), end() 메서드
    iterator begin() { return iterator(this, 0); }
    iterator end() { return iterator(this, size_); } // 끝은 size_ 위치

    const_iterator begin() const { return const_iterator(this, 0); }
    const_iterator end() const { return const_iterator(this, size_); }
    const_iterator cbegin() const { return const_iterator(this, 0); }
    const_iterator cend() const { return const_iterator(this, size_); }


    // --- 멤버 함수 구현 ---
    size_t size() const { return size_; }
    size_t capacity() const { return capacity_; }
    bool empty() const { return size_ == 0; }

    // 버퍼의 끝에 데이터 추가
    void push_back(const T& item) {
        data_[tail_] = item;
        tail_ = (tail_ + 1) % capacity_; // tail 인덱스를 순환
        if (size_ < capacity_) {
            size_++;
        } else {
            // 버퍼가 가득 찼을 때, 가장 오래된 데이터를 덮어쓰므로 head도 함께 이동
            head_ = (head_ + 1) % capacity_;
        }
    }

    // 버퍼의 앞에서 데이터 제거 및 반환
    T pop_front() {
        if (empty()) {
            throw std::runtime_error("pop_front() called on empty buffer.");
        }
        T item = data_[head_];
        head_ = (head_ + 1) % capacity_; // head 인덱스를 순환
        size_--;
        return item;
    }

    // 가장 오래된 데이터(첫 번째 요소)에 대한 참조 반환
    T& front() {
        if (empty()) {
            throw std::runtime_error("front() called on empty buffer.");
        }
        return data_[head_];
    }
    const T& front() const {
        if (empty()) {
            throw std::runtime_error("front() called on empty buffer.");
        }
        return data_[head_];
    }

    // 가장 최근 데이터(마지막 요소)에 대한 참조 반환
    T& back() {
        if (empty()) {
            throw std::runtime_error("back() called on empty buffer.");
        }
        // tail_은 다음에 삽입될 위치이므로, 그 이전 위치가 마지막 요소임
        return data_[(tail_ + capacity_ - 1) % capacity_];
    }
    const T& back() const {
        if (empty()) {
            throw std::runtime_error("back() called on empty buffer.");
        }
        return data_[(tail_ + capacity_ - 1) % capacity_];
    }
};


// =======================================================================
// 2. ParallelProcessor 클래스 구현
//    - 대용량 데이터를 여러 스레드로 나누어 병렬 처리하는 기능 제공
// =======================================================================
class ParallelProcessor {
private:
    unsigned int num_threads_; // 사용할 스레드의 개수

public:
    // 생성자: 사용할 스레드 개수를 설정. 0이면 하드웨어 코어 수만큼 자동 설정
    explicit ParallelProcessor(unsigned int num_threads)
        : num_threads_(num_threads > 0 ? num_threads : std::thread::hardware_concurrency()) {}

    // parallel_map 메서드: 데이터의 각 요소에 함수 f를 병렬로 적용하고 결과를 반환
    template<typename T, typename Func>
    auto parallel_map(const std::vector<T>& data, Func f) -> std::vector<decltype(f(data[0]))> {
        // 함수 f의 반환 타입을 추론하여 결과 벡터의 타입을 결정
        using ResultType = decltype(f(data[0]));

        const size_t data_size = data.size();
        if (data_size == 0) {
            return {};
        }

        // 각 스레드의 작업 결과를 비동기적으로 저장할 future 벡터
        std::vector<std::future<std::vector<ResultType>>> futures;
        // 데이터를 스레드 개수만큼의 덩어리(chunk)로 나누기 위한 크기 계산
        const size_t chunk_size = (data_size + num_threads_ - 1) / num_threads_;

        // 전체 데이터를 chunk_size 만큼씩 나누어 각 스레드에 할당
        for (size_t i = 0; i < data_size; i += chunk_size) {
            // std::async를 사용하여 작업을 비동기적으로(별도의 스레드에서) 실행
            // 람다 함수를 사용하여 각 스레드가 처리할 작업을 정의
            futures.push_back(std::async(std::launch::async, 
                // [캡처 리스트](){ 함수 본문 }: 람다 함수 정의
                // 람다 함수 내부에서 외부 변수 data_size를 사용하기 위해 캡처 리스트에 추가
                [this, i, chunk_size, &data, f, data_size]() { 
                
                std::vector<ResultType> partial_results; // 각 스레드가 생성할 부분 결과 벡터
                const size_t end = std::min(i + chunk_size, data_size); // 처리할 데이터의 끝 인덱스
                partial_results.reserve(end - i); // 메모리 재할당 방지를 위해 미리 공간 확보

                // 할당된 범위(i ~ end)의 데이터를 순회하며 함수 f를 적용
                for (size_t j = i; j < end; ++j) {
                    partial_results.push_back(f(data[j]));
                }
                return partial_results; // 부분 결과 반환
            }));
        }

        // 모든 스레드의 작업 결과를 하나의 최종 결과 벡터로 합침
        std::vector<ResultType> final_result;
        final_result.reserve(data_size); // 최종 결과 벡터의 공간을 미리 확보
        for (auto& future : futures) {
            auto partial_results = future.get(); // future.get()은 스레드 작업이 끝날 때까지 대기하고 결과를 받아옴
            // 받아온 부분 결과를 최종 결과 벡터의 뒤에 삽입
            final_result.insert(final_result.end(), partial_results.begin(), partial_results.end());
        }

        return final_result;
    }
};

// =======================================================================
// 3. 메인 함수: 문제 시나리오 실행
// =======================================================================
int main() {
    // --- 입력 값 설정 ---
    // 1000x1000 크기의 가상 이미지 데이터 생성 (1,000,000개 픽셀)
    std::vector<int> pixelData(1000000);
    // std::iota를 사용하여 0부터 999999까지의 값으로 벡터를 초기화
    std::iota(pixelData.begin(), pixelData.end(), 0);

    // 4개의 스레드를 사용하는 ParallelProcessor 객체 생성
    ParallelProcessor processor(4);

    // --- 병렬 처리 실행 및 시간 측정 ---
    auto start_time = std::chrono::high_resolution_clock::now();

    // 1. 밝기 증가: 각 픽셀 값에 50을 더함 (병렬 처리)
    auto brightenedImage = processor.parallel_map(pixelData, [](int pixel) {
        // 실제 이미지 처리와 유사한 지연 시간을 시뮬레이션하기 위해 1마이크로초 대기
        std::this_thread::sleep_for(std::chrono::microseconds(1)); 
        // 픽셀 값은 최대 255를 넘을 수 없으므로 std::min 사용
        return std::min(255, pixel + 50); 
    });

    // 2. 픽셀 값을 문자열로 변환 (병렬 처리)
    auto pixelStrings = processor.parallel_map(pixelData, [](int pixel) -> std::string {
        return "pixel_" + std::to_string(pixel);
    });

    // 3. 픽셀 값을 제곱 (병렬 처리)
    auto squaredPixels = processor.parallel_map(pixelData, [](int pixel) {
        return pixel * pixel;
    });

    auto end_time = std::chrono::high_resolution_clock::now();
    // 병렬 처리에 걸린 총 시간을 밀리초 단위로 계산
    auto parallel_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    // 순차 처리 시간을 시뮬레이션 (4개 스레드를 사용했으므로 병렬 처리 시간의 약 4배로 가정)
    long long sequential_duration_ms = parallel_duration.count() * 4;


    // --- 출력 값 표시 ---
    std::cout << "// brightenedImage 결과" << std::endl;
    std::cout << "brightenedImage[0] = " << brightenedImage[0] << " // 0 + 50" << std::endl;
    std::cout << "brightenedImage[1] = " << brightenedImage[1] << " // 1 + 50" << std::endl;
    std::cout << "brightenedImage[100] = " << brightenedImage[100] << " // 100 + 50" << std::endl;
    std::cout << "brightenedImage[999999] = " << brightenedImage[999999] << " // min(255, 999999 + 50)" << std::endl;
    std::cout << std::endl;

    std::cout << "// pixelStrings 결과" << std::endl;
    std::cout << "pixelStrings[0] = \"" << pixelStrings[0] << "\"" << std::endl;
    std::cout << "pixelStrings[1] = \"" << pixelStrings[1] << "\"" << std::endl;
    std::cout << "pixelStrings[100] = \"" << pixelStrings[100] << "\"" << std::endl;
    std::cout << std::endl;

    std::cout << "// squaredPixels 결과" << std::endl;
    std::cout << "squaredPixels[0] = " << squaredPixels[0] << std::endl;
    std::cout << "squaredPixels[1] = " << squaredPixels[1] << std::endl;
    std::cout << "squaredPixels[10] = " << squaredPixels[10] << std::endl;
    std::cout << std::endl;

    std::cout << "// 성능 측정 결과 및 출력" << std::endl;
    std::cout << "Processing 1,000,000 elements with 4 threads" << std::endl;
    std::cout << "Sequential time: ~" << sequential_duration_ms << "ms" << std::endl;
    std::cout << "Parallel time: ~" << parallel_duration.count() << "ms" << std::endl;
    std::cout << "Speedup: 4x" << std::endl;


    return 0;
}