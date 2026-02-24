import pytest
import sys

# run entire test suite programmatically
if __name__ == "__main__":
    sys.exit(pytest.main(["tests", "-q"]))
