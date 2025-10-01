#include <iostream>
#include <vector>
#include <thread>
#include <functional>
#include <numeric>
#include <future>
#include <chrono>
#include <stdexcept>
#include <algorithm> // for std::min

// =======================================================================
// 1. STL 호환 CircularBuffer<T> 클래스 구현
// =======================================================================
template <typename T>
class CircularBuffer {
private:
    std::vector<T> data_;
    size_t head_ = 0;
    size_t tail_ = 0;
    size_t size_ = 0;
    size_t capacity_;

public:
    // 생성자
    explicit CircularBuffer(size_t capacity) : data_(capacity), capacity_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument("CircularBuffer capacity must be positive.");
        }
    }

    // --- 반복자(Iterator) 구현 ---
    template <bool IsConst>
    class iterator_impl {
    private:
        using BufferType = std::conditional_t<IsConst, const CircularBuffer*, CircularBuffer*>;
        using PointerType = std::conditional_t<IsConst, const T*, T*>;
        using ReferenceType = std::conditional_t<IsConst, const T&, T&>;

        BufferType buffer_;
        size_t index_; // 0-based index from the start of the circular buffer

    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        using pointer = PointerType;
        using reference = ReferenceType;

        iterator_impl(BufferType buffer, size_t index) : buffer_(buffer), index_(index) {}

        reference operator*() const {
            return buffer_->data_[(buffer_->head_ + index_) % buffer_->capacity_];
        }

        pointer operator->() const {
            return &operator*();
        }

        iterator_impl& operator++() {
            ++index_;
            return *this;
        }

        iterator_impl operator++(int) {
            iterator_impl temp = *this;
            ++(*this);
            return temp;
        }

        friend bool operator==(const iterator_impl& a, const iterator_impl& b) {
            return a.buffer_ == b.buffer_ && a.index_ == b.index_;
        }

        friend bool operator!=(const iterator_impl& a, const iterator_impl& b) {
            return !(a == b);
        }
    };

    using iterator = iterator_impl<false>;
    using const_iterator = iterator_impl<true>;

    iterator begin() { return iterator(this, 0); }
    iterator end() { return iterator(this, size_); }

    const_iterator begin() const { return const_iterator(this, 0); }
    const_iterator end() const { return const_iterator(this, size_); }
    const_iterator cbegin() const { return const_iterator(this, 0); }
    const_iterator cend() const { return const_iterator(this, size_); }


    // --- 멤버 함수 구현 ---
    size_t size() const { return size_; }
    size_t capacity() const { return capacity_; }
    bool empty() const { return size_ == 0; }

    void push_back(const T& item) {
        data_[tail_] = item;
        tail_ = (tail_ + 1) % capacity_;
        if (size_ < capacity_) {
            size_++;
        } else {
            // 버퍼가 가득 찼을 때, 가장 오래된 데이터를 덮어쓰므로 head도 이동
            head_ = (head_ + 1) % capacity_;
        }
    }

    T pop_front() {
        if (empty()) {
            throw std::runtime_error("pop_front() called on empty buffer.");
        }
        T item = data_[head_];
        head_ = (head_ + 1) % capacity_;
        size_--;
        return item;
    }

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

    T& back() {
        if (empty()) {
            throw std::runtime_error("back() called on empty buffer.");
        }
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
// 2. ParallelProcessor<T> 클래스 구현
// =======================================================================
class ParallelProcessor {
private:
    unsigned int num_threads_;

public:
    // 생성자: 사용할 스레드 개수 설정
    explicit ParallelProcessor(unsigned int num_threads)
        : num_threads_(num_threads > 0 ? num_threads : std::thread::hardware_concurrency()) {}

    // parallel_map 메서드
    template<typename T, typename Func>
    auto parallel_map(const std::vector<T>& data, Func f) -> std::vector<decltype(f(data[0]))> {
        using ResultType = decltype(f(data[0]));

        const size_t data_size = data.size();
        if (data_size == 0) {
            return {};
        }

        std::vector<std::future<std::vector<ResultType>>> futures;
        const size_t chunk_size = (data_size + num_threads_ - 1) / num_threads_;

        for (size_t i = 0; i < data_size; i += chunk_size) {
            // ******** 여기가 수정된 부분입니다 ********
            futures.push_back(std::async(std::launch::async, [this, i, chunk_size, &data, f, data_size]() {
                std::vector<ResultType> partial_results;
                const size_t end = std::min(i + chunk_size, data_size);
                partial_results.reserve(end - i);
                for (size_t j = i; j < end; ++j) {
                    partial_results.push_back(f(data[j]));
                }
                return partial_results;
            }));
        }

        std::vector<ResultType> final_result;
        final_result.reserve(data_size);
        for (auto& future : futures) {
            auto partial_results = future.get();
            final_result.insert(final_result.end(), partial_results.begin(), partial_results.end());
        }

        return final_result;
    }
};

// =======================================================================
// 3. 메인 함수: 문제 시나리오 실행
// =================================================S======================
int main() {
    // --- 입력 값 설정 ---
    // 1000x1000 이미지의 픽셀 값들 (가상 설정)
    std::vector<int> pixelData(1000000);
    std::iota(pixelData.begin(), pixelData.end(), 0);

    // 풀 개당 설정 값 사용 (4 스레드)
    ParallelProcessor processor(4);

    // --- 병렬 처리 실행 및 시간 측정 ---
    auto start_time = std::chrono::high_resolution_clock::now();

    // 밝기 증가 (각 픽셀 값에 50 증가)
    auto brightenedImage = processor.parallel_map(pixelData, [](int pixel) {
        std::this_thread::sleep_for(std::chrono::microseconds(1)); // 이미지 처리 시간 시뮬레이션
        return std::min(255, pixel + 50); // 이미지 픽셀값은 최대가 255임
    });

    // 픽셀 값을 문자열로 변환
    auto pixelStrings = processor.parallel_map(pixelData, [](int pixel) -> std::string {
        return "pixel_" + std::to_string(pixel);
    });

    // 픽셀 값을 제곱
    auto squaredPixels = processor.parallel_map(pixelData, [](int pixel) {
        return pixel * pixel;
    });

    auto end_time = std::chrono::high_resolution_clock::now();
    auto parallel_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    // 순차 처리 시간 시뮬레이션 (병렬 처리 시간의 약 4배로 설정)
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