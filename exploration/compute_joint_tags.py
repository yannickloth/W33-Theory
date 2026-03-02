from collections import defaultdict

from refine_kernel_state import output_patterns, seed_patterns

# repeat refine function

def refine_tags_for_swap(swap_id, output_patterns, seed_patterns):
    tags = list(output_patterns[swap_id].keys())
    out = output_patterns[swap_id]
    eq_classes = []
    while tags:
        base = tags.pop()
        cls = [base]
        t0, w0, z0 = base
        for other in tags[:]:
            t1, w1, z1 = other
            if t0 != t1 or z0 != z1:
                continue
            good = True
            for (t_s, s0, z_s), seed_pat in seed_patterns.items():
                if t_s != t0 or z_s != z0:
                    continue
                if out[base] != out[other]:
                    good = False
                    break
            if good:
                cls.append(other)
                tags.remove(other)
        eq_classes.append(cls)
    return eq_classes

classes1 = refine_tags_for_swap(1, output_patterns, seed_patterns)
classes2 = refine_tags_for_swap(2, output_patterns, seed_patterns)

joint = defaultdict(list)
for tag in set(output_patterns[1].keys()) | set(output_patterns[2].keys()):
    def find_class(tag, classes):
        for i, cls in enumerate(classes):
            if tag in cls:
                return i
    joint[(find_class(tag, classes1), find_class(tag, classes2))].append(tag)

print('joint classes count', len(joint))
for k, v in joint.items():
    print(k, v)
