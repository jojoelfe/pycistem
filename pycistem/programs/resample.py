import asyncio

from dataclasses import dataclass
from typing import Union, List


from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_send_next_job

@dataclass
class ResampleParameters:
    input_filename: str 
    output_filename: str 
    is_a_volume: bool = False  
    new_x_size: int = 64
    new_y_size: int = 64
    new_z_size: int = 1    
  




def run(parameters: Union[ResampleParameters,list[ResampleParameters]],**kwargs):

    if not isinstance(parameters, list):
        parameters = [parameters]
   
    asyncio.run(cistem_program.run("resample", parameters, **kwargs))
    
        