from dataclasses import dataclass
from pycistem.programs import cistem_program
import pandas as pd
import asyncio
import struct
from typing import Union, List
from pathlib import Path
import mrcfile
import sqlite3
import datetime
from ._cistem_constants import socket_send_next_job
from ..database import get_image_info_from_db
@dataclass
class CtffindParameters:
    input_filename : str
    input_is_a_movie: bool = True
    number_of_frames_to_average : int = 3
    output_diagnostic_filename : str = "diagnostic.mrc"
    pixel_size_of_input_image : float = 1.0
    acceleration_voltage : float = 300.0
    spherical_aberration : float = 2.7
    amplitude_contrast: float = 0.07
    box_size: int = 512
    minimum_resolution: float = 30.0
    maximum_resolution: float = 5.0
    minimum_defocus: float = 3000.0
    maximum_defocus: float = 30000.0
    defocus_search_step: float = 100.0
    slower_search: bool = False
    astigmatism_tolerance: float = 100.0
    find_additional_phase_shift: bool = False
    minimum_additional_phase_shift: float = 0.0
    maximum_additional_phase_shift: float = 0.0
    additional_phase_shift_search_step: float = 0.0
    astigmatism_is_known: bool = False
    known_astigmatism: float = 0.0
    known_astigmatism_angle: float = 0.0
    resample_if_pixel_too_small: bool = True
    movie_is_gain_corrected: bool = False
    gain_filename: str = "gain.mrc"
    movie_is_dark_corrected: bool = True
    dark_filename: str = "dark.mrc"
    correct_movie_mag_distortion: bool = False
    movie_mag_distortion_angle: float = 0.0
    movie_mag_distortion_major_scale: float = 1.0
    movie_mag_distortion_minor_scale: float = 1.0
    defocus_is_known: bool = False
    known_defocus_1: float = 0.0
    known_defocus_2: float = 0.0
    known_phase_shift: float = 0.0
    determine_tilt: bool = False
    desired_number_of_threads: int = 1
    eer_frames_per_image: int = 0
    eer_super_res_factor: int = 1
    fit_nodes: bool = False
    fit_nodes_1D_brute_force: bool = True
    fit_nodes_2D_refine: bool = True
    fit_nodes_low_resolution_limit: float = 25.0
    fit_nodes_high_resolution_limit: float = 3.0
    target_pixel_size_after_resampling: float = 1.4
    fit_nodes_use_rounded_square: bool = False
    fit_nodes_downweight_nodes: bool = False

def parameters_from_database(database, decolace=False, **kwargs):
    movie_info = get_image_info_from_db(database,get_ctf=False)
    ProjectDirectory = Path(database).parent
    par = [CtffindParameters(
        input_filename = movie["FILENAME"],
        output_filename= (ProjectDirectory / "Assets" / "Images" / f"{Path(movie['FILENAME']).stem}_{movie['MOVIE_ASSET_ID']}_auto.mrc").as_posix(),
        pixel_size = movie["PIXEL_SIZE"],
        gain_filename=movie["GAIN_FILENAME"],
        output_binning_factor=movie["OUTPUT_BINNING_FACTOR"],
        exposure_per_frame=movie["DOSE_PER_FRAME"],
        amplitude_spectrum_filename=(ProjectDirectory / "Assets" / "Images" / "Spectra" / f"{Path(movie['FILENAME']).stem}_{movie['MOVIE_ASSET_ID']}_auto.mrc").as_posix(),
        small_sum_image_filename=(ProjectDirectory / "Assets" / "Images" / "Scaled" / f"{Path(movie['FILENAME']).stem}_{movie['MOVIE_ASSET_ID']}_auto.mrc").as_posix(),
        align_on_cropped_area=decolace,
        replace_dark_areas_with_gaussian_noise=decolace
    ) for i,movie in movie_info.iterrows()]
    return(par)


async def handle_results(reader, writer, logger):
    #logger.info("Handling results")
    await reader.read(4)
    length = await reader.read(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    results = await reader.read(number_of_bytes*4)
    return(results)

signal_handlers = {
    socket_send_next_job : handle_results
}

def run(parameters: Union[CtffindParameters,list[CtffindParameters]],**kwargs):

    if not isinstance(parameters, list):
        parameters = [parameters]

    byte_results = asyncio.run(cistem_program.run("ctffind", parameters, signal_handlers=signal_handlers,**kwargs))
    result_ctf = []

    for parameter_index,byte_result in byte_results:
        defocus1 = struct.unpack("<f",byte_result[0:4])[0]
        defocus2 = struct.unpack("<f",byte_result[4:8])[0]
        astigmatism_angle = struct.unpack("<f",byte_result[8:12])[0]
        phase_shift = struct.unpack("<f",byte_result[12:16])[0]
        score = struct.unpack("<f",byte_result[16:20])[0]
        fit_resolution = struct.unpack("<f",byte_result[20:24])[0]
        aliasing_resolution = struct.unpack("<f",byte_result[24:28])[0]
        iciness = struct.unpack("<f",byte_result[28:32])[0]
        tilt_angle = struct.unpack("<f",byte_result[32:36])[0]
        tilt_axis = struct.unpack("<f",byte_result[36:40])[0]
        sample_thickness = struct.unpack("<f",byte_result[40:44])[0]

        result_ctf.append({
            "parameter_index" : parameter_index,
            "defocus1" : defocus1,
            "defocus2" : defocus2,
            "astigmatism_angle" : astigmatism_angle,
            "phase_shift" : phase_shift,
            "score" : score,
            "fit_resolution" : fit_resolution,
            "aliasing_resolution" : aliasing_resolution,
            "iciness" : iciness,
            "tilt_angle" : tilt_angle,
            "tilt_axis" : tilt_axis,
            "sample_thickness" : sample_thickness,
            "parameter_index" : parameter_index
        })


    return(result_ctf)
