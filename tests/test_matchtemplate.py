import numpy as np
from rich import print

import pycistem
from pycistem.programs import match_template
from pycistem.programs import generate_gpu_prefix, generate_num_procs

pycistem.set_cistem_path("/groups/elferich/cistem_binaries/")


par = match_template.MatchTemplateParameters(
    input_search_images_filename="/nrs/elferich/human_neurons/Assets/Images/91-g2_56_00000_767_0.mrc",
    input_reconstruction_filename="/data/elferich/notebook/notebook/protocols/templates/6o2s_halflength_protein_bfm4_ps1.mrc",
    angular_step=10.0,
    in_plane_angular_step=10.0,
    defocus_step=0.0,
    image_number_for_gui=334,
   )

pars, image_info = match_template.parameters_from_database("/nrs/elferich/old_THP1_brequinar/20230407_THP1_C_glycerol_g2_aa26/20230407_THP1_C_glycerol_g2_aa26.db","/nrs/elferich/old_THP1_brequinar/7cpu_centered_60S_200px_2.0A_bfm2.mrc",0)


run_profile = {
    "zamor1": 8,
}

print(pars)

res = match_template.run(pars,num_procs=generate_num_procs(run_profile),cmd_prefix=list(generate_gpu_prefix(run_profile)),cmd_suffix='"')

print(res)
