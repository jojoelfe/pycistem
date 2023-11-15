import numpy as np
from rich import print

import pycistem


pycistem.set_cistem_path("/groups/cryoadmin/software/CISTEM/je_dev/")
pa = pycistem.programs.refine_ctf.RefineCtfParameters(
    input_particle_images="/scratch/erice/elferich/processing_thp1_ribosomes_unbinned/Assets/ParticleStacks/particle_stack_2.mrc",
    input_star_filename="/scratch/erice/elferich/processing_thp1_ribosomes_unbinned/Assets/Parameters/refine_ctf_input_star_7_Johannes_20230628_-1.0_-1.0.star",
    input_reconstruction="/groups/elferich/pycistem/examples/volume_9_1_masked.mrc",
    molecular_mass_kDa=3000.0,
    outer_mask_radius=200.0,
    beamtilt_refinement=True,
)

# pycistem.programs.refine_ctf.run(pa,num_threads=10)

pbs = []
for i in range(0,500):
    start_position = i*(290880//500)
    end_position = (i+1)*(290880//500)
    if end_position > 290880:
        end_position = 290880
    pbs.append(pycistem.programs.EstimateBeamtiltParameters(
        input_phase_difference_image = "test.mrc",
        pixel_size = 1.0,
        voltage_kV = 300.0,
        spherical_aberration_mm = 2.7,
        first_position_to_search = start_position,
        last_position_to_search = end_position
    ))

result = pycistem.programs.estimate_beamtilt.run(pbs,num_procs=10)
result.to_csv("test.csv")