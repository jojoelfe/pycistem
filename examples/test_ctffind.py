import numpy as np
from rich import print

import pycistem
from pycistem.programs import ctffind

pycistem.set_cistem_path("/scratch/paris/elferich/cisTEM/build/je_combined_Intel-gpu-debug-static/src/")


par = ctffind.CtffindParameters(
    input_filename="/data/elferich/CryoTEM/Johannes_20230317/THP1_24hbr_g1/lamella1/frames/s_THP1_24hbr_g1_niceview_00182_20.0_Mar18_08.41.58.tif",
    gain_filename="/data/elferich/CryoTEM/Johannes_20230317/THP1_24hbr_g1/lamella1/frames/SuperCDSRef_s_THP1_24hbr_g1_niceview_00000_20.0_Mar18_08.02.25.dm4",
    pixel_size_of_input_image=0.53,
    fit_nodes=True,
   )

par2 = ctffind.CtffindParameters(
    input_filename="/data/elferich/CryoTEM/Johannes_20230317/THP1_24hbr_g1/lamella1/frames/s_THP1_24hbr_g1_niceview_00181_20.0_Mar18_08.41.47.tif",
    gain_filename="/data/elferich/CryoTEM/Johannes_20230317/THP1_24hbr_g1/lamella1/frames/SuperCDSRef_s_THP1_24hbr_g1_niceview_00000_20.0_Mar18_08.02.25.dm4",
    pixel_size_of_input_image=0.53,
    fit_nodes=True
)

pars, image_info = ctffind.parameters_from_database("/nrs/elferich/old_THP1_brequinar/20230407_THP1_C_glycerol_g2_aa26/20230407_THP1_C_glycerol_g2_aa26.db")
res = ctffind.run(pars,num_procs=10)

ctffind.write_results_to_database("/nrs/elferich/old_THP1_brequinar/20230407_THP1_C_glycerol_g2_aa26/20230407_THP1_C_glycerol_g2_aa26.db",pars,res,image_info)
