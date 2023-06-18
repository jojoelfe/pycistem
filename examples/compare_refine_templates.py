import numpy as np
from rich import print
from rich_tools import df_to_table

import pycistem

image_ass_id = 185
pycistem.set_cistem_path("/groups/grigorieffn/workspace/cisTEM/build/src/")
pa = pycistem.programs.refine_template_niko.parameters_from_database("/scratch/bern/elferich/ER_HoxB8_96h/ER_HoxB8_96h.db",
                                                                     image_ass_id,
                                                                     template_match_id=4,
                                                                     wanted_threshold=9.0,
                                                                     input_reconstruction="/groups/elferich/mammalian_ribosome_structures/6swa_simulate_bfsca1_5.mrc",)
res_niko = pycistem.programs.refine_template_niko.run(pa)

print(df_to_table(res_niko))

pycistem.set_cistem_path("/groups/elferich/cisTEM/build/refine_template_tests_Intel-gpu-debug/src/")

pa = pycistem.programs.refine_template.parameters_from_database("/scratch/bern/elferich/ER_HoxB8_96h/ER_HoxB8_96h.db",
                                                                     image_ass_id,
                                                                     template_match_id=4,
                                                                     wanted_threshold=9.0,
                                                                     input_reconstruction="/groups/elferich/mammalian_ribosome_structures/6swa_simulate_bfsca1_5.mrc",)
res_my = pycistem.programs.refine_template.run(pa)

print(df_to_table(res_my))
