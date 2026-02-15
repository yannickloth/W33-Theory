import pstats

p = pstats.Stats("checks/prof_jacobi_sample.prof")
p.sort_stats("cumtime")
items = sorted(p.stats.items(), key=lambda kv: kv[1][3], reverse=True)[:25]
for func, stat in items:
    cc, nc, tt, ct, callers = stat
    print(
        f"{ct:.6f}s  total_calls={cc}  primitive_calls={nc}  totaltime={tt:.6f}  func={func}"
    )
