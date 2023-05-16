import asyncio
import struct
from dataclasses import dataclass
from pickle import FALSE

import pandas as pd

from pycistem.database import get_image_info_from_db, get_tm_info_from_db
from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_template_match_result_ready


@dataclass
class RefineTemplateParameters:
    input_search_image: str
    input_reconstruction: str = "template.mrc"
    pixel_size: float = 1.0
    voltate_kV: float = 300.0
    spherical_aberration_mm: float = 2.7
    amplitude_contrast: float = 0.07
    defocus1: float = 10000
    defocus2: float = 10000
    defocus_angle: float = 0.0
    low_resolution_limit: float = 300.0
    high_resolution_limit: float = 3.0
    angular_range: float = 0.2
    angular_step: float = 0.2
    best_parameters_to_keep: int = 20
    defocus_search_range: float = 200.0
    defocus_search_step: float = 10.0
    pixel_size_search_range: float = 0.0
    pixel_size_step: float = 0.01
    padding: float = 1.0
    ctf_refinement: bool = True
    mask_radius: float = 0.0
    phase_shift: float = 0.0
    mip_input_filename: str = "input_mip.mrc"
    scaled_mip_input_filename: str = "input_scaled_mip.mrc"
    best_psi_input_filename: str = "input_psi.mrc"
    best_theta_input_filename: str = "input_theta.mrc"
    best_phi_input_filename: str = "input_phi.mrc"
    best_defocus_input_filename: str = "input_defocus.mrc"
    best_pixel_size_input_filename: str = "input_pixel_size.mrc"
    best_psi_output_file: str = "/tmp/psi.mrc"
    best_theta_output_file: str = "/tmp/theta.mrc"
    best_phi_output_file: str = "/tmp/phi.mrc"
    best_defocus_output_file: str = "/tmp/defocus.mrc"
    best_pixel_size_output_file: str = "/tmp/pixel_size.mrc"
    mip_output_file: str = "/tmp/mip.mrc"
    scaled_mip_output_file: str = "/tmp/scaled_mip.mrc"
    wanted_threshold: float = 7.5
    min_peak_radius: float = 10.0
    xy_change_threshold: float = 10.0
    exclude_above_xy_threshold: bool = False
    my_symmetry: str = "C1"
    in_plane_angular_step: float = 0.1
    first_search_position: int = -1
    last_search_position: int = -1
    image_number_for_gui: int = 0
    number_of_jobs_per_image_in_gui: int = 0
    result_number: int = 1
    max_threads: int = 1
    directory_for_results: str = "/tmp"
    threshold_for_result_plotting: float = 8.0
    filename_for_gui_result_image: str = "/tmp/gui_result.mrc"
    xyz_coords_filename: str ="/tmp/test.txt"
    read_coordinates: bool = False

async def handle_results(reader, writer, logger):
    logger.info("Handling results")
    data = await reader.read(4)
    number_of_bytes = int.from_bytes(data[0:3], byteorder="little")
    results = await reader.read(number_of_bytes)
    return(results)

signal_handlers = {
    socket_template_match_result_ready : handle_results
}

def parameters_from_database(database, image_asset_id, template_match_id, **kwargs):
    image_info = get_image_info_from_db(database, image_asset=image_asset_id)
    tm_info = get_tm_info_from_db(database,image_asset_id, template_match_id)
    par = RefineTemplateParameters(input_search_image=image_info["FILENAME"],
                             pixel_size=image_info["image_pixel_size"],
                             voltate_kV=image_info["VOLTAGE"],
                             spherical_aberration_mm=image_info["SPHERICAL_ABERRATION"],
                             amplitude_contrast=image_info["AMPLITUDE_CONTRAST"],
                             defocus1=image_info["DEFOCUS1"],
                             defocus2=image_info["DEFOCUS2"],
                             defocus_angle=image_info["DEFOCUS_ANGLE"],
                             mip_input_filename=tm_info["MIP_OUTPUT_FILE"],
                             scaled_mip_input_filename=tm_info["SCALED_MIP_OUTPUT_FILE"],
                             best_defocus_input_filename=tm_info["DEFOCUS_OUTPUT_FILE"],
                             best_pixel_size_input_filename=tm_info["PIXEL_SIZE_OUTPUT_FILE"],
                             best_psi_input_filename=tm_info["PSI_OUTPUT_FILE"],
                             best_theta_input_filename=tm_info["THETA_OUTPUT_FILE"],
                             best_phi_input_filename=tm_info["PHI_OUTPUT_FILE"],
                             **kwargs)
    return(par)

def run(parameters: RefineTemplateParameters):
    byte_result = asyncio.run(cistem_program.run("refine_template", parameters, signal_handlers=signal_handlers))[0]
    struct.unpack_from("<i",byte_result,offset=0)[0]
    peak_numbers = struct.unpack_from("<i",byte_result,offset=4)[0]
    struct.unpack_from("<i",byte_result,offset=8)[0]
    struct.unpack_from("<f",byte_result,offset=12)[0]

    result_peaks = pd.DataFrame({"peak_number": pd.Series(dtype="int"),
                                 "x": pd.Series(dtype="float"),
                                 "y": pd.Series(dtype="float"),
                                 "psi": pd.Series(dtype="float"),
                                 "theta": pd.Series(dtype="float"),
                                 "phi": pd.Series(dtype="float"),
                                 "defocus": pd.Series(dtype="float"),
                                 "pixel_size": pd.Series(dtype="float"),
                                 "peak_value": pd.Series(dtype="float")})

    for peak_number in range(peak_numbers):
        (x, y, psi, theta, phi, defocus, pixel_size, peak_height) = struct.unpack_from("<ffffffff",byte_result,offset=16+peak_number*32)
        a_series = pd.Series([peak_number, x, y, psi, theta, phi, defocus, pixel_size, peak_height], index = result_peaks.columns)
        result_peaks = result_peaks.append(a_series, ignore_index=True)

    return(result_peaks)

