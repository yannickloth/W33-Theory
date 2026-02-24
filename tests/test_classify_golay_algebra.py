import re
from scripts.classify_golay_algebra import main

# Smoke test: running classification should not raise and should mention Skryabin

def test_classify_prints_name(capsys):
    main()
    captured = capsys.readouterr().out
    assert 'Skryabin' in captured
    assert '24' in captured
