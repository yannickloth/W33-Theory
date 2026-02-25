def test_readme_mentions_new_pillars():
    txt = open("README.md", "r", encoding="utf-8").read()
    assert "Pillars 58–60" in txt or "Pillars 58-60" in txt
    assert "v2026-02-16-pillars-58-60" in txt
    assert "71 pillars" in txt or "69 pillars" in txt
    assert "## The 69 Pillars" in txt or "## The 71 Pillars" in txt

    import json

    zen = json.load(open(".zenodo.json", "r", encoding="utf-8"))
    blob = (zen.get("description", "") or "") + "\n" + (zen.get("notes", "") or "")
    assert "71 pillars" in blob or "69 pillars" in blob
    assert "880" in blob or "877" in blob


def test_citation_mentions_69_pillars():
    txt = open("CITATION.cff", "r", encoding="utf-8").read()
    assert "71 proved pillars" in txt or "69 proved pillars" in txt
    assert "880" in txt or "877" in txt
