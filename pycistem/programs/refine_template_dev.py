from dataclasses import dataclass
import asyncio
import pycistem.programs.cistem_program as cistem_program
from typing import Union

@dataclass
class RefineTemplateDevParameters:
    input_starfile: str = "input.star"
    output_starfile: str = "output.star"
    input_template: str = "input.mrc"
    start_position:int = 0
    end_position:int = -1
    num_threads:int = 1

def run(parameters: Union[RefineTemplateDevParameters,list[RefineTemplateDevParameters]],write_directly_to_db=True,**kwargs):

    if not isinstance(parameters, list):
        parameters = [parameters]

    signal_handlers = {
       
    }
    
    results = asyncio.run(cistem_program.run("refine_template_dev", parameters, signal_handlers=signal_handlers,num_threads=parameters[0].num_threads,**kwargs))

    return(results)