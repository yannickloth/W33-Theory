import sys
from tools.map_edges_to_octonion_orients import main

if __name__=='__main__':
    sys.argv = [sys.argv[0],
        '--tri_zip','TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle/TOE_E6pair_SRG_triangle_decomp_v01_20260227.zip',
        '--edge_zip','dummy.zip',
        '--out','map_example.json']
    main()
