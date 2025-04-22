import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compi import compile_code

def normalize_output(code):
    """Remove extra whitespace and newlines for comparison."""
    return ' '.join(code.strip().split())

def test_unrolling():
    input_code = """
    int a[100];
    int b[100];
    for (int i = 0; i < 100; i++) {
        a[i] = b[i] + 1;
    }
    """
    # Expected: Loop unrolled by factor of 2, bounds adjusted to 50
    # No LICM or fusion applies
    expected_output = """
    int a[100];
    int b[100];
    for (int i = 0; i < 100; i++) {
      a[i] = b[i] + 1;
      a[i+1] = b[i+1] + 1;
      i += 1;
    }
    """
    try:
        actual_output = compile_code(input_code)
        actual_normalized = normalize_output(actual_output)
        expected_normalized = normalize_output(expected_output)
        if actual_normalized == expected_normalized:
            print("Unrolling Test: PASSED")
        else:
            print("Unrolling Test: FAILED")
            print("Expected Output:")
            print(expected_output)
            print("Actual Output:")
            print(actual_output)
    except Exception as e:
        print(f"Unrolling Test: ERROR - {e}")

if __name__ == "__main__":
    test_unrolling()