def test_readme_mentions_new_pillars():
    txt = open("README.md", "r", encoding="utf-8").read()
    # README should mention the current pillar range section (58-71 encoded as HTML entity)
    assert "Pillars 58" in txt
    # README should have The 71 Pillars section (or higher)
    assert "## The 71 Pillars" in txt or "## The 74 Pillars" in txt
    # README should mention pillar count >= 71
    assert "71 pillars" in txt or "74 pillars" in txt

    import json

    zen = json.load(open(".zenodo.json", "r", encoding="utf-8"))
    blob = (zen.get("description", "") or "") + "\n" + (zen.get("notes", "") or "")
    assert "71 pillars" in blob or "69 pillars" in blob
    assert "882" in blob or "880" in blob or "877" in blob


def test_citation_mentions_69_pillars():
    txt = open("CITATION.cff", "r", encoding="utf-8").read()
    assert "71 proved pillars" in txt or "69 proved pillars" in txt
    assert "882" in txt or "880" in txt or "877" in txt
