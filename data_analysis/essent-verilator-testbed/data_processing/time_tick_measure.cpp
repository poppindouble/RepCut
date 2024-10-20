#include <iostream>
#include <thread>

#include <chrono>




#if defined(__i386__) || defined(__x86_64__)
#define VL_GET_CPU_TICK(val) \
    { \
        uint32_t hi; \
        uint32_t lo; \
        asm volatile("rdtsc" : "=a"(lo), "=d"(hi)); \
        (val) = ((uint64_t)lo) | (((uint64_t)hi) << 32); \
    }
#elif defined(__aarch64__)
# define VL_GET_CPU_TICK(val) \
    { \
        asm volatile("isb" : : : "memory"); \
        asm volatile("mrs %[rt],CNTVCT_EL0" : [rt] "=r"(val)); \
    }
#else
#error "Unsupported platform"
#endif

inline uint64_t get_tick() {
    uint64_t val;
    VL_GET_CPU_TICK(val);
    return val;
}


int main() {

    auto start_tick = get_tick();

    std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    auto end_tick = get_tick();

    
    int64_t duration_tick = end_tick - start_tick;

    std::cout << "Tick rate is " << duration_tick << " per second" << std::endl;
}