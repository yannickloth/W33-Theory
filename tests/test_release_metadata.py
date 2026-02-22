def test_readme_mentions_new_pillars():
    txt = open("README.md", "r", encoding="utf-8").read()
    assert "Pillars 58–60" in txt or "Pillars 58-60" in txt
    assert "v2026-02-16-pillars-58-60" in txt

    import json

    zen = json.load(open(".zenodo.json", "r", encoding="utf-8"))
    blob = (zen.get("description", "") or "") + "\n" + (zen.get("notes", "") or "")
    assert "60 pillars" in blob


def test_citation_has_60_pillars():
    txt = open("CITATION.cff", "r", encoding="utf-8").read()
    assert "60 proved" in txt or "60" in txt.split("version:")[-1] or "60" in txt
