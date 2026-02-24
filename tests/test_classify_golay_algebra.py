import re
from scripts.classify_golay_algebra import main

# Smoke test: running classification should not raise and should mention Skryabin

def test_classify_prints_name(capsys):
    main()
    captured = capsys.readouterr().out
    assert 'Skryabin' in captured
    assert '24' in captured
    # inner automorphism group should not be completely commuting in normal form
    assert 'inner_aut_commuting? False' in captured
    # symplectic grade permutations present
    assert 'symplectic grade perms: 24 distinct' in captured
