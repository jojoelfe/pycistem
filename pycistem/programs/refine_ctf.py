import asyncio
from dataclasses import dataclass
from typing import Union
import numpy as np
import struct
import mrcfile
from functools import partial


from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_program_defined_result, socket_job_result_queue, socket_i_have_an_error
from pycistem.core import Image

@dataclass
class RefineCtfParameters:
    input_particle_images: str 
    input_star_filename: str
    input_reconstruction: str
    input_reconstruction_statistics: str = "my_statistics.txt"
    use_statistics: bool = False
    ouput_star_filename: str = "/dev/null"
    ouput_shift_filename: str = "/dev/null"
    ouput_phase_difference_image: str = "/dev/null"
    ouput_beamtilt_image: str = "/dev/null"
    ouput_difference_image: str = "/dev/null"
    first_particle: int = 0
    last_particle: int = 0
    pixel_size: float = 1.0
    molecular_mass_kDa: float = 300.0
    inner_mask_radius: float = 0.0
    outer_mask_radius: float = 150.0
    low_resolution_limit: float = 300.0
    high_resolution_limit: float = 3.0
    defocus_search_range: float = 500.0
    defocus_step: float = 50.0
    padding: float = 1.0
    ctf_refinement: bool = False
    beamtilt_refinement: bool = False
    normalize_particles: bool = True
    invert_contrast: bool = False
    exclude_blank_edges: bool = True
    normalize_input_3d: bool = True
    threshold_input_3d: bool = False
    job_number_from_gui: int = 0 
    expected_number_of_results_from_gui: int = 0
    max_threads: int = 1

def get_np_arrays(bytes,o,i,x,y,numpix):
    array = np.frombuffer(bytes,offset=o+i*numpix*4, count=numpix,dtype=np.float32).copy()
    array = array.reshape((y,-1))
    array = array[:,:x]
    return array

async def handle_results(reader, writer, logger, parameters):
    #logger.info("Handling results")
    size_of_array= await reader.readexactly(4)
    result_number= await reader.readexactly(4)
    number_of_expected_results= await reader.readexactly(4)
    number_of_floats = int.from_bytes(size_of_array, byteorder="little")
    result_number = int.from_bytes(result_number, byteorder="little")
    number_of_expected_results = int.from_bytes(number_of_expected_results, byteorder="little")
    results = await reader.readexactly(number_of_floats*4)
    x_dim = int(struct.unpack("<f",results[0:4])[0])
    y_dim = int(struct.unpack("<f",results[4:8])[0])
    num_pixels = int(struct.unpack("<f",results[8:12])[0])
    images_to_process = int(struct.unpack("<f",results[12:16])[0])
    voltage_kV = struct.unpack("<f",results[16:20])[0]
    spherical_aberration_mm = struct.unpack("<f",results[20:24])[0]
    phase_difference_image = get_np_arrays(results,24,0,x_dim,y_dim,num_pixels)
    phase_difference_image_cistem = Image()

    phase_difference_image_cistem.Allocate(x_dim,y_dim,1,False,True)
    np.copyto(phase_difference_image_cistem.real_values , phase_difference_image)
    phase_difference_image_cistem.DivideByConstant(images_to_process)
    phase_difference_image_cistem.CosineMask(0.45, parameters[result_number].pixel_size / 20.0, False, False, 0.0)
    phase_difference_image_cistem.QuickAndDirtyWriteSlice(parameters[result_number].ouput_phase_difference_image,1,True,0.0)
    #mrcfile.write("test.mrc", phase_difference_image.astype(np.float32), overwrite=True)
    return(results)

async def handle_job_result_queue(reader, writer, logger):

    length = await reader.readexactly(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    results = await reader.readexactly(number_of_bytes)
    return(results)

async def handle_i_have_an_error(reader, writer, logger):
    print("I have an error")
    #number_of_bytes = int.from_bytes(length, byteorder="little")
    number_of_bytes = 40
    results = await reader.read(number_of_bytes)
    print(results)
    return(results)

def run(parameters: Union[RefineCtfParameters,list[RefineCtfParameters]],**kwargs):

    if not isinstance(parameters, list):
        parameters = [parameters]
    for i, par in enumerate(parameters):
        par.image_number_for_gui = i
    signal_handlers = {
        socket_program_defined_result : partial(handle_results,parameters=parameters),
        socket_job_result_queue : handle_job_result_queue,
        socket_i_have_an_error: handle_i_have_an_error
    }   
    byte_results = asyncio.run(cistem_program.run("refine_ctf", parameters, signal_handlers=signal_handlers,**kwargs))
