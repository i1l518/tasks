#pragma once
#include <memory>
#include <stdexcept>
#include <iterator>

template <typename T>
class CircularBuffer {
private:
    std::unique_ptr<T[]> buffer_;
    size_t head_ = 0;
    size_t tail_ = 0;
    size_t capacity_;
    size_t size_ = 0;

public:
    // --- 개선된 STL 호환 Forward Iterator ---
    template <bool IsConst>
    class base_iterator {
    public:
        // const 여부에 따라 타입 변경
        using value_type = T;
        using pointer = typename std::conditional<IsConst, const T*, T*>::type;
        using reference = typename std::conditional<IsConst, const T&, T&>::type;
        using iterator_category = std::forward_iterator_tag;
        using difference_type = std::ptrdiff_t;
        using parent_pointer = typename std::conditional<IsConst, const CircularBuffer*, CircularBuffer*>::type;

        base_iterator(parent_pointer parent, size_t pos, size_t traversed)
            : parent_(parent), pos_(pos), traversed_(traversed) {}

        reference operator*() const {
            return parent_->buffer_[pos_];
        }

        pointer operator->() const {
            return &parent_->buffer_[pos_];
        }

        base_iterator& operator++() {
            if (traversed_ < parent_->size_) {
                pos_ = (pos_ + 1) % parent_->capacity_;
                traversed_++;
            }
            return *this;
        }

        base_iterator operator++(int) {
            base_iterator temp = *this;
            ++(*this);
            return temp;
        }

        bool operator!=(const base_iterator& other) const {
            // 순회한 거리를 기준으로 비교
            return traversed_ != other.traversed_;
        }
        
        bool operator==(const base_iterator& other) const {
            return !(*this != other);
        }

    private:
        parent_pointer parent_;
        size_t pos_;
        size_t traversed_; // 순회한 요소의 개수
    };

    using iterator = base_iterator<false>;
    using const_iterator = base_iterator<true>;

    // 생성자
    explicit CircularBuffer(size_t capacity)
        : capacity_(capacity), buffer_(std::make_unique<T[]>(capacity)) {
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be positive");
        }
    }

    // begin(), end() 메서드
    iterator begin() {
        return iterator(this, head_, 0);
    }
    iterator end() {
        // end는 size만큼 순회한 상태를 의미
        return iterator(this, tail_, size_);
    }
    const_iterator begin() const {
        return const_iterator(this, head_, 0);
    }
    const_iterator end() const {
        return const_iterator(this, tail_, size_);
    }
     const_iterator cbegin() const {
        return begin();
    }
    const_iterator cend() const {
        return end();
    }


    // size(), capacity(), empty()
    size_t size() const { return size_; }
    size_t capacity() const { return capacity_; }
    bool empty() const { return size_ == 0; }

    // push_back(), pop_front()
    void push_back(const T& item) {
        buffer_[tail_] = item;
        tail_ = (tail_ + 1) % capacity_;

        if (size_ < capacity_) {
            size_++;
        } else {
            // 버퍼가 가득 찼으면 head도 함께 이동 (가장 오래된 데이터 덮어쓰기)
            head_ = (head_ + 1) % capacity_;
        }
    }

    void pop_front() {
        if (empty()) {
            throw std::out_of_range("Buffer is empty");
        }
        head_ = (head_ + 1) % capacity_;
        size_--;
    }

    // front(), back() (const 및 non-const)
    T& front() {
        if (empty()) throw std::out_of_range("Buffer is empty");
        return buffer_[head_];
    }
    const T& front() const {
        if (empty()) throw std::out_of_range("Buffer is empty");
        return buffer_[head_];
    }
    T& back() {
        if (empty()) throw std::out_of_range("Buffer is empty");
        // tail은 다음에 쓸 위치이므로, 그 이전 인덱스가 마지막 요소
        return buffer_[(tail_ == 0) ? capacity_ - 1 : tail_ - 1];
    }
    const T& back() const {
        if (empty()) throw std::out_of_range("Buffer is empty");
        return buffer_[(tail_ == 0) ? capacity_ - 1 : tail_ - 1];
    }
};