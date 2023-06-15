import asyncio
import struct
from dataclasses import dataclass
from functools import partial
from typing import List, Union, Tuple
import sqlite3

import mrcfile
import numpy as np
import pandas as pd
from skimage.feature import peak_local_max
from pathlib import Path


from pycistem.core import EulerSearch, ParameterMap
from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_job_result_queue, socket_program_defined_result
from pycistem.database import datetime_to_msdos, get_image_info_from_db, ensure_template_is_a_volume_asset


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
    angular_step: float = 3.0 #10
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
    in_plane_angular_step: float = 2.0
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

def parameters_from_database(database, template_filename: str, template_id: int,**kwargs):
    image_info = get_image_info_from_db(database,get_ctf=True)
    ProjectDirectory = Path(database).parent
    par = [MatchTemplateParameters(
        input_search_images_filename = image["FILENAME"],
        input_reconstruction_filename = template_filename,
        pixel_size = image["image_pixel_size"],
        defocus1=image["DEFOCUS1"],
        defocus2=image["DEFOCUS2"],
        defocus_angle=image["DEFOCUS_ANGLE"],
        scaled_mip_output_file=(ProjectDirectory / "Assets" / "TemplateMatching" / f"{Path(image['FILENAME']).stem}_auto_{template_id}_scaled_mip.mrc").as_posix(),
        output_histogram_file=(ProjectDirectory / "Assets" / "TemplateMatching" / f"{Path(image['FILENAME']).stem}_auto_{template_id}_histogram.txt").as_posix(),
    ) for i,image in image_info.iterrows()]
    return((par, image_info))

def write_results_to_database(database,  parameters: List[MatchTemplateParameters], results: Tuple[int, pd.DataFrame], image_info):
    # Ensure Volume assets
    template_vol_ids = {}
    for par in parameters:
        template_vol_ids[par.input_reconstruction_filename] = -1
    for template in template_vol_ids:
        template_vol_ids[template] = ensure_template_is_a_volume_asset(database, template)
    
    conn = sqlite3.connect(database, isolation_level=None)
    cur = conn.cursor()
    results = sorted(results, key=lambda x: x["parameter_index"])
    # Add results to TEMPLATE_MATCH_LIST
    template_match_result_list = []

    max_template_match_id = cur.execute("SELECT MAX(TEMPLATE_MATCH_ID) FROM TEMPLATE_MATCH_LIST").fetchone()[0]
    if max_template_match_id is None:
        max_template_match_id = 0
    template_match_id = max_template_match_id + 1
    template_match_job_id = cur.execute("SELECT MAX(TEMPLATE_MATCH_JOB_ID) FROM TEMPLATE_MATCH_LIST").fetchone()[0]
    if template_match_job_id is None:
        template_match_job_id = 1
    else:
        template_match_job_id += 1
    
    for result in results:
        template_match_result_list.append({
            "TEMPLATE_MATCH_ID": template_match_id,
            "JOB_NAME": f"auto_{template_match_job_id}_{Path(parameters[result[0].input_reconstruction_filename]).stem}",
            "DATETIME_OF_RUN": datetime_to_msdos(datetime.datetime.now()),
            "TEMPLATE_MATCH_JOB_ID": template_match_job_id,
            "JOB_TYPE_CODE": 0,
            "INPUT_TEMPLATE_MATCH_ID": 0,
            "IMAGE_ASSET_ID": image_info.loc[result[0]]["IMAGE_ASSET_ID"],
            "REFERENCE_VOLUME_ASSET_ID": template_vol_ids[parameters[result[0]].input_reconstruction_filename],
            "IS_ACTIVE": False,
            "USED_SYMMETRY": parameters[result[0]].my_symmetry,
            "USED_PIXEL_SIZE": parameters[result[0]].pixel_size,
            "USED_VOLTAGE": parameters[result[0]].voltage_kV,
            "USED_SPHERICAL_ABERRATION": parameters[result[0]].spherical_aberration_mm,
            "USED_AMPLITUDE_CONTRAST": parameters[result[0]].amplitude_contrast,
            "USED_DEFOCUS1": parameters[result[0]].defocus1,
            "USED_DEFOCUS2": parameters[result[0]].defocus2,
            "USED_DEFOCUS_ANGLE": parameters[result[0]].defocus_angle,
            "USED_PHASE_SHIFT": parameters[result[0]].phase_shift,
            "LOW_RESOLUTION_LIMIT": parameters[result[0]].low_resolution_limit,
            "HIGH_RESOLUTION_LIMIT": parameters[result[0]].high_resolution_limit,
            "OUT_OF_PLANE_ANGULAR_STEP": parameters[result[0]].angular_step,
            "IN_PLANE_ANGULAR_STEP": parameters[result[0]].in_plane_angular_step,
            "DEFOCUS_SEARCH_RANGE": parameters[result[0]].defocus_search_range,
            "DEFOCUS_STEP": parameters[result[0]].defocus_step,
            "PIXEL_SIZE_SEARCH_RANGE": parameters[result[0]].pixel_size_search_range,
            "PIXEL_SIZE_STEP": parameters[result[0]].pixel_size_step,
            "REFINEMENT_THRESHOLD": 0.0,
            "USED_THRESHOLD": 7.0,
            "REF_BOX_SIZE_IN_ANGSTROMS": 0,
            "MASK_RADIUS": parameters[result[0]].mask_radius,
            "MIN_PEAK_RADIUS": parameters[result[0]].min_peak_radius,
            "XY_CHANGE_THRESHOLD": 0.0,
            "EXCLUDE_ABOVE_XY_THRESHOLD": False,
            "MIP_OUTPUT_FILE": "/dev/null",
            "SCALED_MIP_OUTPUT_FILE": parameters[result[0]].scaled_mip_output_file,
            "AVG_OUTPUT_FILE": "/dev/null",
            "STD_OUTPUT_FILE": "/dev/null",
            "PSI_OUTPUT_FILE": "/dev/null",
            "THETA_OUTPUT_FILE": "/dev/null",
            "PHI_OUTPUT_FILE": "/dev/null",
            "DEFOCUS_OUTPUT_FILE": "/dev/null",
            "PIXEL_SIZE_OUTPUT_FILE": "/dev/null",
            "HISTOGRAM_OUTPUT_FILE": parameters[result[0]].output_histogram_file,   
            "PROJECTION_RESULT_OUTPUT_FILE": parameters[result[0]].scaled_mip_output_file,
        })

    # Create TEMPLATE_MATCH_PEAK_LIST_{i}

    # TEMPLATE_MATCH_PEAK_CHANGE_LIST_{i}
    
    
    ESTIMATED_CTF_PARAMETERS_LIST = []

    max_ctf_estimation_id= cur.execute("SELECT MAX(CTF_ESTIMATION_ID) FROM ESTIMATED_CTF_PARAMETERS").fetchone()[0]
    if max_ctf_estimation_id is None:
        max_ctf_estimation_id = 0
    ctf_estimation_job_id= cur.execute("SELECT MAX(CTF_ESTIMATION_JOB_ID) FROM ESTIMATED_CTF_PARAMETERS").fetchone()[0]
    if ctf_estimation_job_id is None:
        ctf_estimation_job_id = 1
    else:
        ctf_estimation_job_id += 1

    for result in results:
        ESTIMATED_CTF_PARAMETERS_LIST.append({
            "CTF_ESTIMATION_ID": max_ctf_estimation_id + 1,
            "CTF_ESTIMATION_JOB_ID": ctf_estimation_job_id,
            "DATETIME_OF_RUN": datetime_to_msdos(datetime.datetime.now()),
            "IMAGE_ASSET_ID": image_info.loc[result[0]]["IMAGE_ASSET_ID"],
            "ESTIMATED_ON_MOVIE_FRAMES": True,
            "VOLTAGE": parameters[result["parameter_index"]].acceleration_voltage,
            "SPHERICAL_ABERRATION": parameters[result["parameter_index"]].spherical_aberration,
            "PIXEL_SIZE": parameters[result["parameter_index"]].pixel_size_of_input_image,
            "AMPLITUDE_CONTRAST": parameters[result["parameter_index"]].amplitude_contrast,
            "BOX_SIZE": parameters[result["parameter_index"]].box_size,
            "MIN_RESOLUTION": parameters[result["parameter_index"]].minimum_resolution,
            "MAX_RESOLUTION": parameters[result["parameter_index"]].maximum_resolution,
            "MIN_DEFOCUS": parameters[result["parameter_index"]].minimum_defocus,
            "MAX_DEFOCUS": parameters[result["parameter_index"]].maximum_defocus,
            "DEFOCUS_STEP": parameters[result["parameter_index"]].defocus_search_step,
            "RESTRAIN_ASTIGMATISM": parameters[result["parameter_index"]].astigmatism_tolerance > 0,
            "TOLERATED_ASTIGMATISM": parameters[result["parameter_index"]].astigmatism_tolerance,
            "FIND_ADDITIONAL_PHASE_SHIFT": parameters[result["parameter_index"]].find_additional_phase_shift,
            "MIN_PHASE_SHIFT": parameters[result["parameter_index"]].minimum_additional_phase_shift,
            "MAX_PHASE_SHIFT": parameters[result["parameter_index"]].maximum_additional_phase_shift,
            "PHASE_SHIFT_STEP": parameters[result["parameter_index"]].additional_phase_shift_search_step,
            "DEFOCUS1": result["defocus1"],
            "DEFOCUS2": result["defocus2"],
            "DEFOCUS_ANGLE": result["astigmatism_angle"],
            "ADDITIONAL_PHASE_SHIFT": result["phase_shift"],
            "SCORE": result["score"],
            "DETECTED_RING_RESOLUTION": result["fit_resolution"],
            "DETECTED_ALIAS_RESOLUTION": result["aliasing_resolution"],
            "OUTPUT_DIAGNOSTIC_FILE": parameters[result["parameter_index"]].output_diagnostic_filename,
            "NUMBER_OF_FRAMES_AVERAGED": parameters[result["parameter_index"]].number_of_frames_to_average,
            "LARGE_ASTIGMATISM_EXPECTED": parameters[result["parameter_index"]].slower_search,
            "ICINESS": result["iciness"],
            "TILT_ANGLE": result["tilt_angle"],
            "TILT_AXIS": result["tilt_axis"],
            "SAMPLE_THICKNESS": result["sample_thickness"],
            "SAMPLE_THICKNESS_JSON": "",
            "DETERMINE_TILT": parameters[result["parameter_index"]].determine_tilt,
            "FIT_NODES": parameters[result["parameter_index"]].fit_nodes,
            "FIT_NODES_1D": parameters[result["parameter_index"]].fit_nodes_1D_brute_force,
            "FIT_NODES_2D": parameters[result["parameter_index"]].fit_nodes_2D_refine,
            "FIT_NODES_LOW_LIMIT": parameters[result["parameter_index"]].fit_nodes_low_resolution_limit,
            "FIT_NODES_HIGH_LIMIT": parameters[result["parameter_index"]].fit_nodes_high_resolution_limit,
             "FIT_NODES_ROUNDED_SQUARE": parameters[result["parameter_index"]].fit_nodes_use_rounded_square,
             "FIT_NODES_DOWNWEIGHT_NODES": parameters[result["parameter_index"]].fit_nodes_downweight_nodes,
             "RESAMPLE_IF_NESCESSARY": parameters[result["parameter_index"]].resample_if_pixel_too_small,
             "TARGET_PIXEL_SIZE": parameters[result["parameter_index"]].target_pixel_size_after_resampling
        })
        #print("UPDATE IMAGE_ASSETS SET CTF_ESTIMATION_ID = ? WHERE IMAGE_ASSET_ID = ?",  (max_ctf_estimation_id + 1, image_info.loc[result["parameter_index"]]["IMAGE_ASSET_ID"]))
        #cur.execute("UPDATE IMAGE_ASSETS SET CTF_ESTIMATION_ID = ? WHERE IMAGE_ASSET_ID = ?",  (max_ctf_estimation_id + 1, image_info.loc[result["parameter_index"]]["IMAGE_ASSET_ID"]))
        max_ctf_estimation_id += 1

    ESTIMATED_CTF_PARAMETERS_LIST = pd.DataFrame(ESTIMATED_CTF_PARAMETERS_LIST)
    ESTIMATED_CTF_PARAMETERS_LIST.to_sql("ESTIMATED_CTF_PARAMETERS", conn, if_exists="append", index=False)
    print([
        (row["CTF_ESTIMATION_ID"], row["IMAGE_ASSET_ID"])
        for i, row in ESTIMATED_CTF_PARAMETERS_LIST.iterrows()
    ])
    cur = conn.cursor()
    cur.executemany("UPDATE IMAGE_ASSETS SET CTF_ESTIMATION_ID = ? WHERE IMAGE_ASSET_ID = ?",[
        (row["CTF_ESTIMATION_ID"], row["IMAGE_ASSET_ID"])
        for i, row in ESTIMATED_CTF_PARAMETERS_LIST.iterrows()
    ])
    conn.commit()
    # Update CTF_ESTIMATION_ID in IMAGE_ASSETS table

    conn.close()


async def handle_results(reader, writer, logger, parameters):
    logger.info("Handling results")
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
    num_histogram_points = int(struct.unpack("<f",results[12:16])[0])
    num_ccs = struct.unpack("<f",results[16:20])[0]
    sqrt_input_pixels = struct.unpack("<f",results[20:24])[0]
    mip = get_np_arrays(results,24,0,x_dim,y_dim,num_pixels)
    psi = get_np_arrays(results,24,1,x_dim,y_dim,num_pixels)
    theta = get_np_arrays(results,24,2,x_dim,y_dim,num_pixels)
    phi = get_np_arrays(results,24,3,x_dim,y_dim,num_pixels)
    defocus = get_np_arrays(results,24,4,x_dim,y_dim,num_pixels)
    get_np_arrays(results,24,5,x_dim,y_dim,num_pixels)
    sum = get_np_arrays(results,24,6,x_dim,y_dim,num_pixels)

    sum = sum / num_ccs
    sum_squares = get_np_arrays(results,24,7,x_dim,y_dim,num_pixels)
    sum_squares = np.sqrt(sum_squares/num_ccs - sum**2)
    scaled_mip = np.divide(mip - sum, sum_squares, out=np.zeros_like(mip), where=sum_squares!=0)
    par = parameters[result_number]
    histogram = np.frombuffer(results,offset=24+8*num_pixels*4, count=num_histogram_points,dtype=np.float32).copy()

    # Calculate expected threshold
    from scipy.special import erfcinv
    expected_threshold = np.sqrt(2.0) * erfcinv(2.0/(x_dim*y_dim*num_ccs)) * 1.0
    print(f"Expected threshold: {expected_threshold}")

    mrcfile.write(par.scaled_mip_output_file, scaled_mip.astype(np.float32), overwrite=True)
    peak_coordinates = peak_local_max(scaled_mip, min_distance=int(par.min_peak_radius), exclude_border=100, threshold_abs=7.0)
    result = pd.DataFrame({
        "X": peak_coordinates[:,1],
        "Y": peak_coordinates[:,0],
        "Psi": psi[tuple(peak_coordinates.T)],
        "Theta": theta[tuple(peak_coordinates.T)],
        "Phi": phi[tuple(peak_coordinates.T)],
        "Defocus": defocus[tuple(peak_coordinates.T)],
        "Score": scaled_mip[tuple(peak_coordinates.T)]
    })
    return(result)

async def handle_job_result_queue(reader, writer, logger):
    #logger.info("Handling results")
    #await reader.read(4)
    length = await reader.readexactly(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    results = await reader.readexactly(number_of_bytes)
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
