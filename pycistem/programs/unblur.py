from dataclasses import dataclass
from pycistem.programs import cistem_program
import pandas as pd
import asyncio
import struct
from typing import Union, List
from ._cistem_constants import socket_job_result, socket_send_next_job


@dataclass
class UnblurParameters:
    input_filename: str
    output_filename: str = "unblurred.mrc"
    pixel_size: float = 1.0
    minimum_shift_in_angstroms: float = 2.00
    maximum_shift_in_angstroms: float = 40.0
    should_dose_filter: bool = True
    should_restore_power: bool = True
    termination_threshold_in_angstroms: float = 1.0
    max_iterations: int = 10
    bfactor_in_angstroms: float = 1500
    should_mask_central_cross: bool = True
    horizontal_mask_size: int = 1
    vertical_mask_size: int = 1
    acceleration_voltage: float = 300.0
    exposure_per_frame: float = 0.0
    pre_exposure_amount: float = 0.0
    movie_is_gain_corrected: bool = False
    gain_filename: str = "gain.mrc"
    movie_is_dark_corrected: bool = True
    dark_filename: str = "dark.mrc"
    output_binning_factor: float = 2.0
    correct_mag_distortion: bool = False
    mag_distortion_angle: float = 0.0
    mag_distortion_major_scale: float = 1.0
    mag_distortion_minor_scale: float = 1.0
    write_out_amplitude_spectrum: bool = True
    amplitude_spectrum_filename: str = "amplitude_spectrum.mrc"
    write_out_small_sum_image: bool = True
    small_sum_image_filename: str = "scaled_sum.mrc"
    first_frame: int = 1
    last_frame: int = 0
    number_of_frames_for_running_average: int = 1
    max_threads: int = 1
    save_aligned_frames: bool = False
    aligned_frames_filename: str = "aligned_frames.mrc"
    output_shift_text_file: str = "shifts.txt"
    eer_frames_per_image: int = 0
    eer_super_res_factor: int = 1
    align_on_cropped_area: bool = True                       
    cropped_area_center_x : int = 0                      
    cropped_area_center_y : int = 0 
    cropped_area_size_x : int = -1
    cropped_area_size_y  : int = -1
    replace_dark_areas_with_gaussian_noise: bool = False     
    threshold_for_gaussian_noise: float = 0.1
    measure_mean_and_variance_for_gaussian_noise : bool = False
    mean_for_gaussian_noise : float = 0.0
    variance_for_gaussian_noise : float = 0.0

async def handle_results(reader, writer, logger):
    #logger.info("Handling results")
    job_number = await reader.read(4)
    length = await reader.read(4)
    number_of_bytes = int.from_bytes(length, byteorder='little')
    results = await reader.read(number_of_bytes*4)
    return(results)

signal_handlers = {
    socket_send_next_job : handle_results
}

def run(parameters: Union[UnblurParameters,list[UnblurParameters]],**kwargs):
    
    if not isinstance(parameters, list):
        parameters = [parameters]
    
    byte_results = asyncio.run(cistem_program.run("unblur", parameters, signal_handlers=signal_handlers,**kwargs))
    print(byte_results)
    result_shifts = []

    for parameter_index,byte_result in byte_results:
        number_of_images = int(((len(byte_result) /4 ) - 4 ) /2)
        x_shifts = []
        for offset in range(number_of_images):
            x_shifts.append(struct.unpack_from('<f',byte_result,offset=offset*4)[0])
        y_shifts = []
        for offset in range(number_of_images):
            y_shifts.append(struct.unpack_from('<f',byte_result,offset=offset*4+number_of_images*4)[0])
        orig_x = int(struct.unpack_from('<f',byte_result,offset=2*4*number_of_images)[0])
        orig_y = int(struct.unpack_from('<f',byte_result,offset=2*4*number_of_images+4)[0])
        crop_x = int(struct.unpack_from('<f',byte_result,offset=2*4*number_of_images+8)[0])
        crop_y = int(struct.unpack_from('<f',byte_result,offset=2*4*number_of_images+12)[0])
        result_shifts.append({
            "parameter_index": parameter_index,
            "x_shifts": x_shifts,
            "y_shifts": y_shifts,
            "orig_x": orig_x,
            "orig_y": orig_y,
            "crop_x": crop_x,
            "crop_y": crop_y
        })
        

    return(result_shifts)