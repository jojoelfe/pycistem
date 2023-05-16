import numpy as np
from rich import print

import pycistem

image_ass_ids = [71 + i for i in range(900)]

pycistem.set_cistem_path("/groups/elferich/cisTEM/build/refine_template_tests_Intel-gpu-debug/src/")

pa = [pycistem.programs.refine_template.parameters_from_database("/scratch/bern/elferich/ER_Hox_120h_20211029_g1_l2/ER_Hox_120h_20211029_g1_l2.db",
                                                                     image_ass_id,
                                                                     template_match_id=1,
                                                                     wanted_threshold=7.5,
                                                                     input_reconstruction="/groups/elferich/mammalian_ribosome_structures/6swa_simulate_bfsca1_5.mrc",)
        for image_ass_id in image_ass_ids]

# Remove None from pa
pa = [p for p in pa if p is not None]

res_my = pycistem.programs.refine_template.run(pa,num_procs=20)

pycistem.programs.refine_template.write_starfile(res_my, "out.star")
