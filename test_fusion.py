import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compiler import compile_code

def normalize_output(code):
    """Remove extra whitespace and newlines for comparison."""
    return ' '.join(code.strip().split())

def test_fusion():
    input_code = """
    int a[100];
    int b[100];
    int c[100];
    for (int i = 0; i <= 100; i++) {
        a[i] = b[i] + c[i];
    }
    for (int i = 0; i <= 100; i++) {
        a[i] = a[i] + 1;
    }
    """
    # Expected: Loops fused into one, then unrolled by factor of 2
    # No LICM applies
    expected_output = """
    int a[100];
    int b[100];
    int c[100];
    for (int i = 0; i <= 50; i++) {
      a[i] = b[i] + c[i];
      a[i+1] = b[i+1] + c[i+1];
      a[i] = a[i] + 1;
      a[i+1] = a[i+1] + 1;
      i += 2;
    }
    """
    try:
        actual_output = compile_code(input_code)
        actual_normalized = normalize_output(actual_output)
        expected_normalized = normalize_output(expected_output)
        if actual_normalized == expected_normalized:
            print("Fusion Test: PASSED")
        else:
            print("Fusion Test: FAILED")
            print("Expected Output:")
            print(expected_output)
            print("Actual Output:")
            print(actual_output)
    except Exception as e:
        print(f"Fusion Test: ERROR - {e}")

if __name__ == "__main__":
    test_fusion()