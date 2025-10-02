#pragma once
#include <memory>       
#include <stdexcept>    
#include <iterator>     
// T라는 임의의 데이터 타입을 받을 수 있는 템플릿 클래스를 선언합니다.
// 이를 통해 CircularBuffer<int>, CircularBuffer<double> 등 다양한 타입의 버퍼를 만들 수 있습니다.
template <typename T>
class CircularBuffer {
private:
    // 실제 데이터를 저장할 동적 배열을 가리키는 스마트 포인터입니다.
    // unique_ptr를 사용하면 객체가 소멸될 때 자동으로 메모리를 해제해주어 메모리 누수를 방지합니다.
    std::unique_ptr<T[]> buffer_;

    // 버퍼에서 가장 오래된 데이터(첫 번째 요소)의 인덱스를 가리킵니다. (다음에 읽을 위치)
    size_t head_ = 0;

    // 버퍼에서 다음에 새로운 데이터를 삽입할 위치의 인덱스를 가리킵니다.
    size_t tail_ = 0;

    // 버퍼의 최대 용량을 저장합니다. 이 값은 생성자에서 설정된 후 변하지 않습니다.
    size_t capacity_;

    // 현재 버퍼에 저장된 요소의 개수를 저장합니다.
    size_t size_ = 0;


public:
    
    // iterator와 const_iterator의 중복 코드를 없애기 위해 템플릿으로 구현된 기반 반복자 클래스입니다.
    // IsConst가 true이면 const_iterator, false이면 일반 iterator로 동작합니다.
    template <bool IsConst>
    class base_iterator {
    public:
        using value_type = T;
        // std::conditional을 사용하여 IsConst 값에 따라 포인터/참조 타입을 결정합니다.
        // IsConst가 true -> const T* / const T& (읽기 전용)
        // IsConst가 false -> T* / T& (읽기/쓰기 가능)
        using pointer = typename std::conditional<IsConst, const T*, T*>::type;
        using reference = typename std::conditional<IsConst, const T&, T&>::type;
        using iterator_category = std::forward_iterator_tag; // 이 반복자는 전방향으로만 이동 가능함을 명시합니다.
        using difference_type = std::ptrdiff_t; // 두 반복자 사이의 거리를 나타내는 타입입니다.

        // IsConst 값에 따라 부모 CircularBuffer 객체를 가리키는 포인터 타입을 결정합니다.
        using parent_pointer = typename std::conditional<IsConst, const CircularBuffer*, CircularBuffer*>::type;

        // 반복자 생성자
        base_iterator(parent_pointer parent, size_t pos, size_t traversed)
            : parent_(parent), pos_(pos), traversed_(traversed) {}

        // 역참조 연산자 오버로딩 (예: *it)
        // 반복자가 현재 가리키는 위치의 데이터에 대한 참조를 반환합니다.
        reference operator*() const {
            return parent_->buffer_[pos_];
        }

        // 멤버 접근 연산자 오버로딩 (예: it->member)
        // 반복자가 가리키는 객체의 멤버에 접근할 수 있게 포인터를 반환합니다.
        pointer operator->() const {
            return &parent_->buffer_[pos_];
        }

        // 전위 증가 연산자 오버로딩 (예: ++it)
        base_iterator& operator++() {
            // 순회가 끝나지 않았을 경우에만 이동합니다.
            if (traversed_ < parent_->size_) {
                // 나머지 연산(%)을 통해 인덱스가 배열 끝에 도달하면 다시 0으로 돌아가도록 합니다. (원형 구조 구현)
                pos_ = (pos_ + 1) % parent_->capacity_;
                // 순회한 거리를 1 증가시킵니다.
                traversed_++;
            }
            return *this; // 자기 자신에 대한 참조를 반환합니다.
        }

        // 후위 증가 연산자 오버로딩 (예: it++)
        base_iterator operator++(int) {
            base_iterator temp = *this; // 변경 전의 상태를 복사해 둡니다.
            ++(*this);                  // 전위 증가 연산을 호출하여 현재 객체를 다음 위치로 이동시킵니다.
            return temp;                // 변경 전의 상태를 반환합니다.
        }

        // 같지 않음 비교 연산자 오버로딩 (예: it != other)
        bool operator!=(const base_iterator& other) const {
            // [핵심] 물리적인 인덱스(pos_)가 아닌, 논리적인 순회 거리(traversed_)를 비교합니다.
            // 이를 통해 버퍼가 가득 차 head와 tail이 같아져도 begin()과 end()를 구분할 수 있습니다.
            return traversed_ != other.traversed_;
        }
        
        // 같음 비교 연산자 오버로딩 (예: it == other)
        bool operator==(const base_iterator& other) const {
            return !(*this != other); // != 연산의 결과를 반대로 하여 구현합니다.
        }

    private:
        parent_pointer parent_; // 부모 CircularBuffer 객체를 가리키는 포인터
        size_t pos_;            // 버퍼 내의 실제 물리적 인덱스
        size_t traversed_;      // begin()으로부터 얼마나 이동했는지를 나타내는 논리적 거리
    };

    // 위 base_iterator를 사용하여 실제 iterator 타입을 정의합니다.
    using iterator = base_iterator<false>;      // IsConst=false -> 수정 가능한 반복자
    using const_iterator = base_iterator<true>; // IsConst=true -> 수정 불가능한 (읽기 전용) 반복자

    // 생성자: 버퍼의 용량(capacity)을 인자로 받습니다.
    // explicit 키워드는 CircularBuffer buf = 5; 와 같이 의도치 않은 암시적 형변환을 방지합니다.
    explicit CircularBuffer(size_t capacity)
        // 멤버 이니셜라이저 리스트: 객체가 생성될 때 멤버 변수들을 효율적으로 초기화합니다.
        : capacity_(capacity), buffer_(std::make_unique<T[]>(capacity)) {
        if (capacity == 0) {
            // 용량이 0이면 버퍼를 만들 수 없으므로 예외를 발생시킵니다.
            throw std::invalid_argument("Capacity must be positive");
        }
    }

    // --- 범위 기반 for문 및 STL 알고리즘 지원을 위한 메서드 ---
    // 논리적인 시작점(가장 오래된 데이터)을 가리키는 반복자를 반환합니다.
    iterator begin() {
        // 물리적 위치는 head_, 순회 거리는 0에서 시작합니다.
        return iterator(this, head_, 0);
    }
    // 논리적인 끝점(마지막 데이터의 다음 위치)을 가리키는 반복자를 반환합니다.
    iterator end() {
        // 물리적 위치는 tail_이지만, 순회 거리를 size_로 설정하여 루프의 종료 조건을 만듭니다.
        return iterator(this, tail_, size_);
    }
    // const 객체(읽기 전용)를 위한 begin/end 메서드 오버로딩입니다. const_iterator를 반환합니다.
    const_iterator begin() const {
        return const_iterator(this, head_, 0);
    }
    const_iterator end() const {
        return const_iterator(this, tail_, size_);
    }
    // C++11 표준에 따라 const 버전을 명시적으로 호출하는 cbegin/cend입니다.
     const_iterator cbegin() const {
        return begin();
    }
    const_iterator cend() const {
        return end();
    }


    // --- 컨테이너 상태 정보 반환 메서드 ---
    size_t size() const { return size_; }         // 현재 요소의 개수를 반환합니다.
    size_t capacity() const { return capacity_; } // 최대 용량을 반환합니다.
    bool empty() const { return size_ == 0; }     // 버퍼가 비어있는지 여부를 반환합니다.

    // --- 데이터 추가 및 삭제 메서드 ---
    // 버퍼의 끝에 새로운 데이터를 추가합니다.
    void push_back(const T& item) {
        buffer_[tail_] = item; // 현재 tail 위치에 데이터를 삽입합니다.
        tail_ = (tail_ + 1) % capacity_; // tail을 다음 위치로 이동시킵니다 (원형으로).

        if (size_ < capacity_) {
            // 버퍼에 아직 공간이 있으면, size를 1 증가시킵니다.
            size_++;
        } else {
            // 버퍼가 가득 찼으면, 가장 오래된 데이터를 덮어쓴 셈이므로 head도 다음 위치로 이동시킵니다.
            head_ = (head_ + 1) % capacity_;
        }
    }

    // 버퍼의 가장 오래된 데이터(첫 번째 요소)를 제거합니다.
    void pop_front() {
        if (empty()) {
            throw std::out_of_range("Buffer is empty"); // 비어있으면 예외를 발생시킵니다.
        }
        // 실제로 데이터를 지우는 것이 아니라, head를 다음 위치로 이동시켜 접근 불가능하게 만듭니다.
        head_ = (head_ + 1) % capacity_;
        size_--; // 요소 개수를 하나 줄입니다.
    }

    // --- 데이터 접근 메서드 ---
    // 가장 오래된 데이터(첫 번째 요소)에 대한 참조를 반환합니다. (수정 가능 버전)
    T& front() {
        if (empty()) throw std::out_of_range("Buffer is empty");
        return buffer_[head_];
    }
    // 가장 오래된 데이터(첫 번째 요소)에 대한 상수 참조를 반환합니다. (읽기 전용 버전)
    const T& front() const {
        if (empty()) throw std::out_of_range("Buffer is empty");
        return buffer_[head_];
    }
    // 가장 최근 데이터(마지막 요소)에 대한 참조를 반환합니다. (수정 가능 버전)
    T& back() {
        if (empty()) throw std::out_of_range("Buffer is empty");
        // tail은 다음에 '쓸' 위치이므로, 마지막 요소는 그 바로 이전 위치입니다.
        // tail이 0일 경우, 마지막 요소는 배열의 맨 끝인 capacity_ - 1이 됩니다.
        return buffer_[(tail_ == 0) ? capacity_ - 1 : tail_ - 1];
    }
    // 가장 최근 데이터(마지막 요소)에 대한 상수 참조를 반환합니다. (읽기 전용 버전)
    const T& back() const {
        if (empty()) throw std::out_of_range("Buffer is empty");
        return buffer_[(tail_ == 0) ? capacity_ - 1 : tail_ - 1];
    }
};