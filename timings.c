#include <stdio.h>
#include <time.h>

#define N 100000

int a[N], b[N], c[N], x;

void unoptimized_version() {
    for (int i = 0; i < N; i++) {
        a[i] = b[i] + c[i];
        x = b[0] + c[0];  // LICM target
    }

    for (int i = 0; i < N; i++) {
        a[i] = a[i] + 1;
    }
}

void optimized_version() {
    x = b[0] + c[0];  // LICM result

    for (int i = 0; i < N; i += 2) {  // Unrolled + Fused
        a[i] = b[i] + c[i];
        a[i] = a[i] + 1;

        a[i+1] = b[i+1] + c[i+1];
        a[i+1] = a[i+1] + 1;
    }
}

double get_time_sec() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

int main() {
    // Initialize arrays
    for (int i = 0; i < N; i++) {
        b[i] = i;
        c[i] = N - i;
        a[i] = 0;
    }

    double start, end;

    // Unoptimized timing
    start = get_time_sec();
    unoptimized_version();
    end = get_time_sec();
    printf("Unoptimized time: %.9f seconds\n", end - start);

    // Reset
    for (int i = 0; i < N; i++) a[i] = 0;

    // Optimized timing
    start = get_time_sec();
    optimized_version();
    end = get_time_sec();
    printf("Optimized time: %.9f seconds\n", end - start);

    return 0;
}
