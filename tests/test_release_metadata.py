def test_readme_mentions_release_metadata():
    import json
    import re

    txt = open("README.md", "r", encoding="utf-8").read()
    assert "Wil Dahn" in txt
    assert "10.5281/zenodo.18652825" in txt

    # README should advertise the current scale of the repo.
    assert "207+ pillar verification scripts" in txt
    assert "5500+ automated tests" in txt

    # Sanity: the pillar table should include at least up through Pillar 207.
    nums = [int(x) for x in re.findall(r"Pillar (\d+)", txt)]
    assert nums and max(nums) >= 207

    zen = json.load(open(".zenodo.json", "r", encoding="utf-8"))
    blob = (zen.get("description", "") or "") + "\n" + (zen.get("notes", "") or "")
    assert "207" in blob
    assert "5500+" in blob or "5584" in blob
    # keep at least one canonical release tag URL so Zenodo lookups are robust
    assert "v2026-02-21-fieldtheory" in json.dumps(zen)


def test_citation_mentions_pillars_and_tests():
    txt = open("CITATION.cff", "r", encoding="utf-8").read()
    assert "Dahn" in txt
    assert "207 proved pillars" in txt or "207+ proved pillars" in txt
    assert "5500+ automated tests" in txt or "5584 automated tests" in txt
