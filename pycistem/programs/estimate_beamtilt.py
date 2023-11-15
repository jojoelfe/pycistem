import asyncio
from dataclasses import dataclass
from typing import Union
import numpy as np
import struct
import mrcfile
from functools import partial
import pandas as pd


from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_send_next_job, socket_job_result_queue
from pycistem.core import Image

@dataclass
class EstimateBeamtiltParameters:
    input_phase_difference_image: str
    pixel_size: float = 1.0
    voltage_kV: float = 300.0      
    spherical_aberration_mm: float  = 2.7
    first_position_to_search: int = 0  
    last_position_to_search: int = 0

async def handle_results(reader, writer, logger):
    #logger.info("Handling results")
    await reader.read(4)
    length = await reader.read(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    results = await reader.read(number_of_bytes*4)
    score = struct.unpack("<f",results[0:4])[0]
    beam_tilt_x = struct.unpack("<f",results[4:8])[0]
    beam_tilt_y = struct.unpack("<f",results[8:12])[0]
    particle_shift_x = struct.unpack("<f",results[12:16])[0]
    particle_shift_y = struct.unpack("<f",results[16:20])[0]
    return(score,beam_tilt_x,beam_tilt_y,particle_shift_x,particle_shift_y)

async def handle_job_result_queue(reader, writer, logger):

    length = await reader.readexactly(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    results = await reader.readexactly(number_of_bytes)
    return(results)

def run(parameters: Union[EstimateBeamtiltParameters,list[EstimateBeamtiltParameters]],**kwargs) -> pd.DataFrame:

    if not isinstance(parameters, list):
        parameters = [parameters]
    signal_handlers = {
        socket_send_next_job : handle_results,
        socket_job_result_queue : handle_job_result_queue,

    }   
    result = asyncio.run(cistem_program.run("estimate_beamtilt", parameters, signal_handlers=signal_handlers,**kwargs))
    result = pd.DataFrame([a[1] for a in result],
                            index = [a[0] for a in result],
                            columns=["score","beam_tilt_x","beam_tilt_y","particle_shift_x","particle_shift_y"])
    return(result)
        
        
        