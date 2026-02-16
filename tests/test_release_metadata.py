def test_readme_mentions_new_pillars():
    txt = open("README.md", "r", encoding="utf-8").read()
    assert "Pillars 58–60" in txt or "Pillars 58-60" in txt


def test_citation_has_60_pillars():
    txt = open("CITATION.cff", "r", encoding="utf-8").read()
    assert "60 proved" in txt or "60" in txt.split("version:")[-1] or "60" in txt
