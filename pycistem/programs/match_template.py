import asyncio
import struct
from dataclasses import dataclass
from functools import partial
from typing import List, Union

import mrcfile
import numpy as np
import pandas as pd
from skimage.feature import peak_local_max

from pycistem.core import EulerSearch, ParameterMap
from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_job_result_queue, socket_program_defined_result


@dataclass
class MatchTemplateParameters:
    input_search_images_filename: str #0
    input_reconstruction_filename: str #1
    pixel_size: float = 1.0 #2
    voltage_kV: float = 300.0 #3
    spherical_aberration_mm: float = 2.7
    amplitude_contrast: float = 0.07
    defocus1: float = 10000.0
    defocus2: float = 10000.0
    defocus_angle: float = 0.0
    low_resolution_limit: float = 30.0
    high_resolution_limit_search: float = 3.0
    angular_step: float = 2.5 #10
    best_parameters_to_keep: int = 1
    defocus_search_range: float = 1000.0
    defocus_step: float = 200.0
    pixel_size_search_range: float = 0.0
    pixel_size_step: float = 0.0
    padding: float = 1.0
    ctf_refinement: bool = False
    particle_radius_angstroms: float = 0.0
    phase_shift: float = 0.0
    mip_output_file: str = "mip.mrc"
    best_psi_output_file: str = "best_psi.mrc"
    best_theta_output_file: str = "best_theta.mrc"
    best_phi_output_file: str = "best_phi.mrc"
    best_defocus_output_file: str = "best_defocus.mrc"
    best_pixel_size_output_file: str = "best_pixel_size.mrc"
    scaled_mip_output_file: str = "scaled_mip.mrc"
    correlation_avg_output_file : str = "correlation_avg.mrc"
    my_symmetry: str = "C1"
    in_plane_angular_step: float = 1.5
    output_histogram_file: str = "histogram.txt"
    first_search_position: int = 0
    last_search_position: int = 100
    image_number_for_gui: int = 0
    number_of_jobs_per_image_in_gui: int = 1
    correlation_std_output_file: str = "correlation_std.mrc"
    directory_for_results: str = "/dev/null"
    result_output_filename: str = "/dev/null"
    min_peak_radius: float = 10.0
    use_gpu: bool = True
    max_threads: int = 4

# PLan: Use normal cistem_program and assign each image a a job.
# Workers will use Send program defined result to send all the images
# Maybe that will overwhelm python???

# Use scikit-image to find peaks myself (peak_local_max)
# Will have no preview, but that's fine
# Will still write scaled_mip

def get_np_arrays(bytes,o,i,x,y,numpix):
    array = np.frombuffer(bytes,offset=o+i*numpix*4, count=numpix,dtype=np.float32).copy()
    array = array.reshape((y,-1))
    array = array[:,:x]
    return array

async def handle_results(reader, writer, logger, parameters):
    logger.info("Handling results")
    size_of_array= await reader.read(4)
    result_number= await reader.read(4)
    number_of_expected_results= await reader.read(4)
    number_of_floats = int.from_bytes(size_of_array, byteorder="little")
    result_number = int.from_bytes(result_number, byteorder="little")
    number_of_expected_results = int.from_bytes(number_of_expected_results, byteorder="little")
    print(f"Result number {result_number} of {number_of_expected_results} with {number_of_floats} floats")
    results = await reader.readexactly(number_of_floats*4)
    x_dim = int(struct.unpack("<f",results[0:4])[0])
    y_dim = int(struct.unpack("<f",results[4:8])[0])
    num_pixels = int(struct.unpack("<f",results[8:12])[0])
    num_histogram_points = struct.unpack("<f",results[12:16])[0]
    num_ccs = struct.unpack("<f",results[16:20])[0]
    sqrt_input_pixels = struct.unpack("<f",results[20:24])[0]
    print(f"X dim: {x_dim}, Y dim: {y_dim}, Num pixels: {num_pixels}, Num histogram points: {num_histogram_points}, Num ccs: {num_ccs}, Sqrt input pixels: {sqrt_input_pixels}")
    mip = get_np_arrays(results,24,0,x_dim,y_dim,num_pixels)
    psi = get_np_arrays(results,24,1,x_dim,y_dim,num_pixels)
    get_np_arrays(results,24,2,x_dim,y_dim,num_pixels)
    get_np_arrays(results,24,3,x_dim,y_dim,num_pixels)
    get_np_arrays(results,24,4,x_dim,y_dim,num_pixels)
    get_np_arrays(results,24,5,x_dim,y_dim,num_pixels)
    sum = get_np_arrays(results,24,6,x_dim,y_dim,num_pixels)
    sum = sum / num_ccs
    sum_squares = get_np_arrays(results,24,7,x_dim,y_dim,num_pixels)
    sum_squares = np.sqrt(sum_squares/num_ccs - sum**2)
    scaled_mip = np.divide(mip - sum, sum_squares, out=np.zeros_like(mip), where=sum_squares!=0)
    print("Creating MRC file")
    par = parameters[result_number]

    mrcfile.write(par.scaled_mip_output_file, scaled_mip.astype(np.float32), overwrite=True)
    print("Getting peak coordinates")
    peak_coordinates = peak_local_max(scaled_mip, min_distance=int(par.min_peak_radius), exclude_border=100, threshold_abs=7.0)
    result = pd.DataFrame({
        "X": peak_coordinates[:,1],
        "Y": peak_coordinates[:,0],
        "Psi": psi[tuple(peak_coordinates.T)],
        "Score": scaled_mip[tuple(peak_coordinates.T)]
    })
    return(result)

async def handle_job_result_queue(reader, writer, logger):
    #logger.info("Handling results")
    #await reader.read(4)
    length = await reader.read(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    results = await reader.read(number_of_bytes*4)
    return(results)



def run(parameters: Union[MatchTemplateParameters,list[MatchTemplateParameters]],**kwargs):

    if not isinstance(parameters, list):
        parameters = [parameters]

    signal_handlers = {
        socket_program_defined_result : partial(handle_results, parameters = parameters),
        socket_job_result_queue : handle_job_result_queue
    }
    for i, par in enumerate(parameters):
        par.image_number_for_gui = i
        global_euler_search = EulerSearch()
        parameter_map = ParameterMap()
        parameter_map.SetAllTrue( )
        global_euler_search.InitGrid(par.my_symmetry,par.angular_step, 0.0, 0.0, 360.0, par.in_plane_angular_step, 0.0, 1.0 / 2.0, parameter_map, 10)
        if par.my_symmetry.startswith("C") and global_euler_search.test_mirror:
            global_euler_search.theta_max = 180.0
        global_euler_search.CalculateGridSearchPositions(False)
        par.first_search_position = 0
        par.last_search_position = global_euler_search.number_of_search_positions - 1

    results = asyncio.run(cistem_program.run("match_template", parameters, signal_handlers=signal_handlers,num_threads=parameters[0].max_threads,**kwargs))
    
    return(results)
