from dataclasses import dataclass
from pickle import FALSE

from pycistem.programs import cistem_program

import asyncio

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
    best_psi_output_file: str = "/dev/null"
    best_theta_output_file: str = "/dev/null"
    best_phi_output_file: str = "/dev/null"
    best_defocus_output_file: str = "/dev/null"
    best_pixel_size_output_file: str = "/dev/null"
    mip_output_file: str = "/dev/null"
    scaled_mip_output_file: str = "/dev/null"
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
    directory_for_results: str = "/dev/null"
    threshold_for_result_plotting: float = 0.0
    filename_for_gui_result_image: str = "/dev/null"
    xyz_coords_filename: str ="/tmp/test.txt"
    read_coordinates: bool = False

def run(parameters: RefineTemplateParameters):
    asyncio.run(cistem_program.run("refine_template", parameters))