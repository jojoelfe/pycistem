import asyncio

from dataclasses import dataclass
from typing import Union, List


from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_i_have_info, socket_job_result_queue, socket_send_next_job

@dataclass
class Reconstruct3dParameters:
    input_particle_stack: str 
    input_star_filename: str           
    input_reconstruction: str         = "/dev/null"
    output_reconstruction_1: str =  "my_reconstruction1.mrc"
    output_reconstruction_2: str = "my_reconstruction2.mrc"
    output_reconstruction_filtered: str = "my_reconstruction_filtered.mrc"
    output_resolution_statistics: str = "my_resolution_statistics.txt"
    my_symmetry: str = "C1"
    first_particle: int = 1
    last_particle: int = 0
    pixel_size: float = 1.0
    molecular_mass_kDa: float = 300.0
    inner_mask_radius: float = 0.0
    outer_mask_radius: float = 150.0
    resolution_limit_rec: float = 0.0
    resolution_limit_ref: float = 0.0
    score_weight_conversion: float = 5.0
    score_threshold: float = 1.0
    smoothing_factor: float = 1.0
    padding : float = 1.0
    normalize_particles: bool = True
    adjust_scores: bool = True
    invert_contrast: bool = False
    exclude_blank_edges: bool = False
    crop_images: bool = False
    split_even_odd: bool = True
    center_mass: bool = False
    use_input_reconstruction: bool = False
    threshold_input_3d: bool = True
    dump_arrays: bool = False
    dump_file_1: str = "my_dump_file1.dat"
    dump_file_2: str = "my_dump_file2.dat"
    correct_ewald_sphere: int = 0
    max_threads: int = 1


async def handle_job_result_queue(reader, writer, logger):

    length = await reader.readexactly(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    results = await reader.readexactly(number_of_bytes)
    return(results)

async def handle_socket_i_have_info(reader, writer, logger):
    data = await reader.readexactly(4)
    length = int.from_bytes(data, byteorder="little")
    data = await reader.readexactly(length)
    print(f"Info: {data.decode('utf-8')}")

async def handle_results(reader, writer, logger):
    #logger.info("Handling results")
    await reader.readexactly(4)
    length = await reader.readexactly(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    data = await reader.readexactly(number_of_bytes*4)

def run(parameters: Union[Reconstruct3dParameters,list[Reconstruct3dParameters]],**kwargs):

    if not isinstance(parameters, list):
        parameters = [parameters]
    signal_handlers = {
        socket_job_result_queue : handle_job_result_queue,
        socket_i_have_info: handle_socket_i_have_info,
        socket_send_next_job: handle_results
    }   
    asyncio.run(cistem_program.run("reconstruct3d", parameters, signal_handlers=signal_handlers,**kwargs))
    
        