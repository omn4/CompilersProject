import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compi import compile_code

def normalize_output(code):
    """Remove extra whitespace and newlines for comparison."""
    return ' '.join(code.strip().split())

def test_all_optimizations():
    input_code = """
    int a[100];
    int b[100];
    int c[100];
    int x;
    for (int i = 0; i <= 99; i++) {
        a[i] = b[i] + c[i];
        x = b[0] + c[0];
    }
    for (int i = 0; i <= 99; i++) {
        a[i] = a[i] + 1;
    }
    """
    # Expected: 
    # - LICM moves x = b[0] + c[0] outside
    # - Fusion combines the two loops
    # - Unrolling replicates the body twice, halves iterations to 49
    expected_output = """
    int a[100];
    int b[100];
    int c[100];
    int x;
    x = b[0] + c[0];
    for (int i = 0; i <= 99; i++) {
      a[i] = b[i] + c[i];
      a[i+1] = b[i+1] + c[i+1];
      a[i] = a[i] + 1;
      a[i+1] = a[i+1] + 1;
      i += 1;
    }
    """
    try:
        actual_output = compile_code(input_code)
        actual_normalized = normalize_output(actual_output)
        expected_normalized = normalize_output(expected_output)
        if actual_normalized == expected_normalized:
            print("All Optimizations Test: PASSED")
        else:
            print("All Optimizations Test: FAILED")
            print("Expected Output:")
            print(expected_output)
            print("Actual Output:")
            print(actual_output)
    except Exception as e:
        print(f"All Optimizations Test: ERROR - {e}")

if __name__ == "__main__":
    test_all_optimizations()