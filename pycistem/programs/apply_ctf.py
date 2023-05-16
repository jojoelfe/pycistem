import asyncio
from dataclasses import dataclass
from typing import Union

from pycistem.database import get_image_info_from_db
from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_send_next_job


@dataclass
class ApplyCtfParameters:
    input_filename: str
    output_filename: str
    pixel_size: float = 1.0
    acceleration_voltage: float = 300.0
    spherical_aberration: float = 2.7
    amplitude_contrast: float = 0.07
    defocus_1: float = 20000
    defocus_2: float = 20000
    astigmatism_angle: float = 0.0
    additional_phase_shift: float = 0.0
    input_ctf_values_from_text_file: bool = False
    text_filename: str = ""
    phase_flip_only: bool = False
    apply_wiener_filter: bool = False
    wiener_filter_falloff_frequency: float = 100.0
    wiener_filter_falloff_fudge_factor: float = 1.0
    wiener_filter_scale_fudge_factor: float = 1.0
    wiener_filter_high_pass_radius: float = 200.0
    maintain_image_contrast: bool = True

def parameters_from_database(database, image_asset_id, output_filename, **kwargs):
    image_info = get_image_info_from_db(database, image_asset=image_asset_id)
    par = ApplyCtfParameters(input_filename=image_info["FILENAME"],
                             output_filename=output_filename,
                             pixel_size=image_info["image_pixel_size"],
                             acceleration_voltage=image_info["VOLTAGE"],
                             spherical_aberration=image_info["SPHERICAL_ABERRATION"],
                             amplitude_contrast=image_info["AMPLITUDE_CONTRAST"],
                             defocus_1=image_info["DEFOCUS1"],
                             defocus_2=image_info["DEFOCUS2"],
                             astigmatism_angle=image_info["DEFOCUS_ANGLE"],
                             **kwargs)
    return(par)

def run(parameters: Union[ApplyCtfParameters,list[ApplyCtfParameters]]):
    if not isinstance(parameters, list):
        parameters = [parameters]


    asyncio.run(cistem_program.run("applyctf",parameters))
