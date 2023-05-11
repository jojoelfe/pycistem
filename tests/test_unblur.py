from pycistem.programs import unblur
import pycistem
import numpy as np
from rich import print

pycistem.set_cistem_path("/scratch/paris/elferich/cisTEM/build/je_combined_Intel-gpu-debug-static/src/")


par = unblur.UnblurParameters(
    input_filename="/data/elferich/CryoTEM/Johannes_20230317/THP1_24hbr_g1/lamella1/frames/s_THP1_24hbr_g1_niceview_00182_20.0_Mar18_08.41.58.tif",
    gain_filename="/data/elferich/CryoTEM/Johannes_20230317/THP1_24hbr_g1/lamella1/frames/SuperCDSRef_s_THP1_24hbr_g1_niceview_00000_20.0_Mar18_08.02.25.dm4",
    align_on_cropped_area=True,
    replace_dark_areas_with_gaussian_noise=True,
    pixel_size=0.53,
    output_binning_factor= 3.774,
    exposure_per_frame=0.8)

par2 = unblur.UnblurParameters(
    input_filename="/data/elferich/CryoTEM/Johannes_20230317/THP1_24hbr_g1/lamella1/frames/s_THP1_24hbr_g1_niceview_00181_20.0_Mar18_08.41.47.tif",
    gain_filename="/data/elferich/CryoTEM/Johannes_20230317/THP1_24hbr_g1/lamella1/frames/SuperCDSRef_s_THP1_24hbr_g1_niceview_00000_20.0_Mar18_08.02.25.dm4",
    align_on_cropped_area=True,
    replace_dark_areas_with_gaussian_noise=True,
    pixel_size=0.53,
    output_binning_factor= 3.774,
    exposure_per_frame=0.8)

print(unblur.run([par,par2],num_procs=2))