"""Extended search for Vogel parameter triples matching given dimensions.

This script uses the universal dimension formula from
`tools/vogel_universal_snapshot.py` and scans a grid of rational parameters
(alpha,beta,gamma) within specified bounds.  It can look for a single
dimension (e.g. 648) or for multiple constraints simultaneously.

Usage examples:
    python scripts/vogel_param_search.py --dim 648
    python scripts/vogel_param_search.py --dim 24 --dim 72
    python scripts/vogel_param_search.py --dim 648 --max-num 50 --max-den 10
"""
import argparse
from fractions import Fraction
import math
import sys
sys.path.append('.')
from tools.vogel_universal_snapshot import vogel_dimension


def search(dims, max_num=20, max_den=6, fix_alpha: Fraction | None = None, exceptional_line: bool = False):
    """Return list of (alpha,beta,gamma,dim) matching all dims.

    - If *fix_alpha* is given the search loops only over beta,gamma grids with
      alpha held fixed (saves a factor of max-range).  This is useful for the
      common Vogel gauge alpha=-2.
    - If *exceptional_line* is True the search is restricted to the parametrized
      line beta=m+4, gamma=2*m+4 with m a rational; this is the classical
      exceptional line from Vogel tables.
    """
    results = []
    if exceptional_line and fix_alpha is not None:
        raise ValueError("cannot combine exceptional_line with fixed alpha")

    if exceptional_line:
        # beta = m + 4, gamma = 2m + 4
        for m_num in range(-max_num, max_num + 1):
            for m_den in range(1, max_den + 1):
                m = Fraction(m_num, m_den)
                beta = m + 4
                gamma = 2 * m + 4
                alpha = Fraction(-2)  # conventional gauge on exceptional line
                try:
                    dim = vogel_dimension(alpha, beta, gamma)
                except ZeroDivisionError:
                    continue
                if all(int(dim) == d for d in dims):
                    results.append((alpha, beta, gamma, int(dim)))
        return results

    # general search with optional fixed alpha
    alphas = [fix_alpha] if fix_alpha is not None else []
    if fix_alpha is None:
        for a_num in range(-max_num, max_num + 1):
            for a_den in range(1, max_den + 1):
                alphas.append(Fraction(a_num, a_den))
    for alpha in alphas:
        for b_num in range(-max_num, max_num + 1):
            for b_den in range(1, max_den + 1):
                beta = Fraction(b_num, b_den)
                for g_num in range(-max_num, max_num + 1):
                    for g_den in range(1, max_den + 1):
                        gamma = Fraction(g_num, g_den)
                        try:
                            dim = vogel_dimension(alpha, beta, gamma)
                        except ZeroDivisionError:
                            continue
                        # require exact rational equality to avoid spurious truncation hits
                        dims_match = all(dim == Fraction(d) for d in dims)
                        if dims_match:
                            results.append((alpha, beta, gamma, int(dim)))
    return results


def main():
    parser = argparse.ArgumentParser(description="Vogel parameter search")
    parser.add_argument('--dim', type=int, action='append', required=True,
                        help='target dimension (can specify multiple)')
    parser.add_argument('--max-num', type=int, default=20,
                        help='maximum numerator absolute value')
    parser.add_argument('--max-den', type=int, default=6,
                        help='maximum denominator')
    parser.add_argument('--fix-alpha', type=str, default=None,
                        help='fix alpha to a rational value (e.g. "-2").')
    parser.add_argument('--exceptional-line', action='store_true',
                        help='restrict search to Vogel exceptional line')
    args = parser.parse_args()

    fix_alpha = None
    if args.fix_alpha is not None:
        fix_alpha = Fraction(args.fix_alpha)

    print('searching for dimensions', args.dim,
          'with numerators <=', args.max_num,
          'denominators <=', args.max_den,
          'fix_alpha=', fix_alpha,
          'exceptional_line=', args.exceptional_line)
    sol = search(args.dim, args.max_num, args.max_den,
                 fix_alpha=fix_alpha,
                 exceptional_line=args.exceptional_line)

    def canonicalize(triple):
        # convert to primitive integer vector up to overall scale and permutation
        a,b,c = triple
        # scale to common denominator
        den = a.denominator * b.denominator * c.denominator
        A = int(a * den)
        B = int(b * den)
        C = int(c * den)
        # divide by gcd
        g = math.gcd(math.gcd(abs(A), abs(B)), abs(C))
        if g != 0:
            A //= g; B //= g; C //= g
        # sort by absolute value then sign to normalize permutation
        sorted_vals = sorted([A,B,C], key=lambda x:(abs(x), x))
        return tuple(sorted_vals)

    if not sol:
        print('no solutions found in grid')
    else:
        print(f'found {len(sol)} raw solutions; canonicalizing')
        seen = set()
        uniq = []
        for alpha,beta,gamma,dim in sol:
            key = canonicalize((alpha,beta,gamma))
            if key not in seen:
                seen.add(key)
                uniq.append((alpha,beta,gamma,dim))
        print(f'{len(uniq)} unique triples up to scale/permutation:')
        for alpha,beta,gamma,dim in uniq:
            print('  alpha=',alpha,'beta=',beta,'gamma=',gamma,'dim=',dim)

if __name__ == '__main__':
    main()
