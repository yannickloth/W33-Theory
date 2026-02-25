import pytest

if __name__ == "__main__":
    # run only the fast, newly added regression tests
    pytest.main([
        "tests/test_monster_rp_index_table.py",
        "tests/test_combined_landscape.py",
        "tests/test_ce2_explanations.py",
        "-q",
    ])
