import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compi import compile_code

def normalize_output(code):
    """Remove extra whitespace and newlines for comparison."""
    return ' '.join(code.strip().split())

def test_licm():
    input_code = """
    int a[100];
    int b[100];
    int c[100];
    for (int i = 0; i <= 100; i++) {
        a[i] = b[i] + c[i];
        x = b[0] + c[0];
    }
    """
    # Expected: The x = b[0] + c[0] is moved outside the loop
    # Unrolling (factor=2) and fusion may also apply, but LICM is the focus
    expected_output = """
    int a[100];
    int b[100];
    int c[100];
    x = b[0] + c[0];
    for (int i = 0; i <= 50; i++) {
      a[i] = b[i] + c[i];
      a[i+1] = b[i+1] + c[i+1];
      i += 2;
    }
    """
    try:
        actual_output = compile_code(input_code)
        actual_normalized = normalize_output(actual_output)
        expected_normalized = normalize_output(expected_output)
        if actual_normalized == expected_normalized:
            print("LICM Test: PASSED")
            print("Expected Output:")
            print(expected_output)
            print("Actual Output:")
            print(actual_output)
        else:
            print("LICM Test: FAILED")
            print("Expected Output:")
            print(expected_output)
            print("Actual Output:")
            print(actual_output)
    except Exception as e:
        print(f"LICM Test: ERROR - {e}")

if __name__ == "__main__":
    test_licm()