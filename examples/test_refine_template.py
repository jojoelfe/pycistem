import numpy as np
from rich import print
from rich_tools import df_to_table

import pycistem

image_ass_id = 185

image_info = pycistem.database.get_image_info_from_db("/scratch/bern/elferich/ER_HoxB8_96h/ER_HoxB8_96h.db",image_ass_id)
tm_info = pycistem.database.get_tm_info_from_db("/scratch/bern/elferich/ER_HoxB8_96h/ER_HoxB8_96h.db",image_ass_id,4)

pycistem.set_cistem_path("/groups/elferich/cisTEM/build/fowl_template_matching_Intel-gpu-debug/src/")
results = []
for ps in np.arange(-180,180,30):
    pa = pycistem.programs.refine_template.RefineTemplateParameters(input_search_image=image_info["FILENAME"],
                                                                    pixel_size=1.5,
                                                                    input_reconstruction="/groups/elferich/mammalian_ribosome_structures/6swa_simulate_bfsca1_5.mrc",
                                                                    defocus1=image_info["DEFOCUS1"],
                                                                    defocus2=image_info["DEFOCUS2"],
                                                                    defocus_angle=ps,
                                                                    mip_input_filename=tm_info["MIP_OUTPUT_FILE"],
                                                                    scaled_mip_input_filename=tm_info["SCALED_MIP_OUTPUT_FILE"],
                                                                    best_defocus_input_filename=tm_info["DEFOCUS_OUTPUT_FILE"],
                                                                    best_pixel_size_input_filename=tm_info["PIXEL_SIZE_OUTPUT_FILE"],
                                                                    best_psi_input_filename=tm_info["PSI_OUTPUT_FILE"],
                                                                    best_theta_input_filename=tm_info["THETA_OUTPUT_FILE"],
                                                                    best_phi_input_filename=tm_info["PHI_OUTPUT_FILE"],
                                                                    angular_step=0.2,
                                                                    in_plane_angular_step=0.1,

                                                                    wanted_threshold=9.0)
    results.append(pycistem.programs.refine_template.run(pa))
    if len(results) == 1:
        print(df_to_table(results[0]))
print(np.arange(-180,180,30))
print([df["peak_value"].mean() for df in results])
