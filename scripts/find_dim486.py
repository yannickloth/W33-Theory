import sys
sys.path.append('.')
from fractions import Fraction
from tools.vogel_universal_snapshot import vogel_dimension


def find_dim(target, max_num=50, max_den=10):
    for a_num in range(-10,11):
        for a_den in range(1,6):
            a = Fraction(a_num, a_den)
            for b_num in range(-50,51):
                for b_den in range(1,11):
                    b = Fraction(b_num, b_den)
                    for c_num in range(-50,51):
                        for c_den in range(1,11):
                            c = Fraction(c_num, c_den)
                            try:
                                d = vogel_dimension(a,b,c)
                            except ZeroDivisionError:
                                continue
                            if d == target:
                                print('found', a, b, c)
                                return True
    return False

if __name__ == '__main__':
    print('search result', find_dim(486))
