from dataclasses import dataclass
from pycistem.programs import cistem_program
import pandas as pd
import asyncio
import struct
from typing import Union, List

@dataclass
class UnblurParameters:
    input_filename: str
    output_filename: str = "unblurred.mrc"
    pixel_size: float = 1.0
    minimum_shift_in_angstroms: float = 1.001
    maximum_shift_in_angstroms: float = 100.0
    should_dose_filter: bool = True
    should_restore_power: bool = True
    termination_threshold_in_angstroms: float = 1.0
    max_iterations: int = 20
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

signal_handlers = {
}

def run(parameters: Union[UnblurParameters,list[UnblurParameters]],**kwargs):
    
    if not isinstance(parameters, list):
        parameters = [parameters]
    
    byte_results = asyncio.run(cistem_program.run("unblur", parameters, signal_handlers=signal_handlers,**kwargs))
    #File names of original image file name, 3D template file name, energy, Cs, amp. contrast, phase shift, X, Y position, Euler angles, defocus 1 & 2 & angle, pixel size, CC average, CC STD, SNR, scaled SNR 
    result_shifts = pd.DataFrame({
        'x_shift': pd.Series(dtype='object'),
        'y_shift': pd.Series(dtype='object'),
       
        })

    for parameter_index,byte_result in byte_results:
        number_of_images = len(byte_results)
        print (number_of_images)
        continue
        image_number = struct.unpack_from('<i',byte_result,offset=0)[0]
        peak_numbers = struct.unpack_from('<i',byte_result,offset=4)[0]
        changes_numbers = struct.unpack_from('<i',byte_result,offset=8)[0]
        threshold = struct.unpack_from('<f',byte_result,offset=12)[0]

        
        for peak_number in range(peak_numbers):
            (x, y, psi, theta, phi, defocus, pixel_size, peak_height) = struct.unpack_from('<ffffffff',byte_result,offset=16+peak_number*32)
            new_peak_series = pd.Series([
                parameters[parameter_index].input_search_image, 
                parameters[parameter_index].input_reconstruction,
                parameters[parameter_index].voltate_kV,
                parameters[parameter_index].spherical_aberration_mm,
                parameters[parameter_index].amplitude_contrast, 
                parameters[parameter_index].phase_shift,
                parameters[parameter_index].defocus1,
                parameters[parameter_index].defocus2,
                parameters[parameter_index].defocus_angle,                
                int(peak_number), 
                x, 
                y, 
                psi, 
                theta, 
                phi, 
                defocus, 
                pixel_size, 
                peak_height], index = result_peaks.columns)
            result_peaks.loc[len(result_peaks.index)] = new_peak_series

    return(result_shifts)