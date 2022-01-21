from dataclasses import dataclass
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
    maintain_image_contrast: bool = False
    