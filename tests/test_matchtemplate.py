import numpy as np
from rich import print

import pycistem
from pycistem.programs import match_template

pycistem.set_cistem_path("/scratch/paris/elferich/cisTEM/build/je_combined_Intel-gpu-debug-static/src/")


par = match_template.MatchTemplateParameters(
    input_search_images_filename="/nrs/elferich/human_neurons/Assets/Images/91-g2_56_00000_767_0.mrc",
    input_reconstruction_filename="/data/elferich/notebook/notebook/protocols/templates/6o2s_halflength_protein_bfm4_ps1.mrc",
    angular_step=10.0,
    in_plane_angular_step=10.0,
    defocus_step=0.0,
    image_number_for_gui=334,
   )

res = match_template.run(par,num_procs=1)

print(res)
