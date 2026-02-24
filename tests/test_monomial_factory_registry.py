from scripts.w33_monster_structure_bridge_report import (
    register_monomial_factory,
    get_monomial_factories,
    unregister_monomial_factory,
)


def test_register_and_retrieve_factory(tmp_path):
    # make sure registry copy works and new factory can be added
    before = get_monomial_factories()
    name = "dummy"
    def dummy_factory():
        return [tuple(range(5))]
    try:
        register_monomial_factory(name, dummy_factory)
        after = get_monomial_factories()
        assert name in after
        assert after[name] is dummy_factory
        # original dict from before should not contain the new name
        assert name not in before
    finally:
        unregister_monomial_factory(name)
