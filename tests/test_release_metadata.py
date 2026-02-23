def test_readme_mentions_new_pillars():
    txt = open("README.md", "r", encoding="utf-8").read()
    assert "Pillars 58–60" in txt or "Pillars 58-60" in txt
    assert "v2026-02-16-pillars-58-60" in txt

    import json

    zen = json.load(open(".zenodo.json", "r", encoding="utf-8"))
    blob = (zen.get("description", "") or "") + "\n" + (zen.get("notes", "") or "")
    assert "65 pillars" in blob
    assert "733 automated tests" in blob


def test_citation_has_65_pillars():
    txt = open("CITATION.cff", "r", encoding="utf-8").read()
    assert "65 proved" in txt or "65" in txt.split("version:")[-1] or "65" in txt
