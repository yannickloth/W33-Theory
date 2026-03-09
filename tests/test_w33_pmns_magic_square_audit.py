from fractions import Fraction

from w33_pmns_magic_square_audit import build_pmns_magic_square_audit


def test_pmns_sector_column_is_exact_and_reactor_is_second_order():
    audit = build_pmns_magic_square_audit()

    assert audit.sector_names == ("collinear", "transversal", "tangent")
    assert audit.sector_sizes == (4, 7, 2)
    assert audit.sector_angles == (
        Fraction(4, 13),
        Fraction(7, 13),
        Fraction(2, 91),
    )
    assert audit.reactor_is_second_order is True


def test_magic_square_row_sums_are_not_fibonacci_but_total_987_is():
    audit = build_pmns_magic_square_audit()

    assert audit.magic_square_row_sums == (84, 137, 255, 511)
    assert audit.magic_square_row_sum_is_fibonacci == (False, False, False, False)
    assert audit.magic_square_total_sum == 987
    assert audit.magic_square_total_is_fibonacci is True
    assert audit.magic_square_total_fibonacci_index == 16
    assert audit.row_sum_recurrence_holds is False
    assert "987 = F_16" in audit.interpretation
