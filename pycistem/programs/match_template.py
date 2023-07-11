import asyncio
import sqlite3
import struct
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import List, Tuple, Union, Optional

import mrcfile
import numpy as np
import pandas as pd
from skimage.feature import peak_local_max
import datetime

from pycistem.core import EulerSearch, ParameterMap
from pycistem.database import datetime_to_msdos, ensure_template_is_a_volume_asset, get_image_info_from_db, create_peak_lists, get_max_match_template_job_id
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

# TODO
# 1. Write correct threshold into db
# 2. Get correct border_exclude value
# 3. Maybe do projection?

def get_np_arrays(bytes,o,i,x,y,numpix):
    array = np.frombuffer(bytes,offset=o+i*numpix*4, count=numpix,dtype=np.float32).copy()
    array = array.reshape((y,-1))
    array = array[:,:x]
    return array

def parameters_from_database(database, template_filename: str, match_template_job_id: Optional[int] = None,**kwargs):
    image_info = get_image_info_from_db(database,get_ctf=True)
    if image_info is None:
        return []
    if match_template_job_id is None:
        match_template_job_id = get_max_match_template_job_id(database) + 1
    ProjectDirectory = Path(database).parent
    par = [MatchTemplateParameters(
        input_search_images_filename = image["FILENAME"],
        input_reconstruction_filename = template_filename,
        pixel_size = image["image_pixel_size"],
        defocus1=image["DEFOCUS1"],
        defocus2=image["DEFOCUS2"],
        defocus_angle=image["DEFOCUS_ANGLE"],
        scaled_mip_output_file=(ProjectDirectory / "Assets" / "TemplateMatching" / f"{Path(image['FILENAME']).stem}_auto_{match_template_job_id}_scaled_mip.mrc").as_posix(),
        output_histogram_file=(ProjectDirectory / "Assets" / "TemplateMatching" / f"{Path(image['FILENAME']).stem}_auto_{match_template_job_id}_histogram.txt").as_posix(),
    ) for i,image in image_info.iterrows()]
    image_info["MATCH_TEMPLATE_JOB_ID"] = match_template_job_id
    image_info["PARAMETERS"] = par
    image_info["DATABASE"] = database
    image_info["THRESHOLD"] = 0.0
    return(image_info)

def write_results_to_database(database,  parameters: list[MatchTemplateParameters], results: list[tuple[int, pd.DataFrame]], image_info):
    # Ensure Volume assets
    template_vol_ids = {}
    for par in parameters:
        template_vol_ids[par.input_reconstruction_filename] = -1
    for template in template_vol_ids.keys():
        template_vol_ids[template] = ensure_template_is_a_volume_asset(database, template, parameters[0].pixel_size)

    conn = sqlite3.connect(database, isolation_level=None)
    cur = conn.cursor()
    results = sorted(results, key=lambda x: x[0])
    # Add results to TEMPLATE_MATCH_LIST
    template_match_result_list = []

    max_template_match_id = cur.execute("SELECT MAX(TEMPLATE_MATCH_ID) FROM TEMPLATE_MATCH_LIST").fetchone()[0]
    if max_template_match_id is None:
        max_template_match_id = 0
    template_match_id = max_template_match_id + 1
    #template_match_job_id = cur.execute("SELECT MAX(TEMPLATE_MATCH_JOB_ID) FROM TEMPLATE_MATCH_LIST").fetchone()[0]
    #if template_match_job_id is None:
    #    template_match_job_id = 1
    #else:
    #    template_match_job_id += 1

    for result in results:
        template_match_job_id = image_info.iloc[result[0]]["MATCH_TEMPLATE_JOB_ID"]
        # CHeck if THRESHOLD column exists in image_info
        if "THRESHOLD" in image_info.columns:
            threshold = image_info.iloc[result[0]]["THRESHOLD"]
        else:
            threshold = 7.0
        template_match_result_list.append({
            "TEMPLATE_MATCH_ID": template_match_id,
            "JOB_NAME": f"auto_{template_match_job_id}_{Path(parameters[result[0]].input_reconstruction_filename).stem}",
            "DATETIME_OF_RUN": datetime_to_msdos(datetime.datetime.now()),
            "TEMPLATE_MATCH_JOB_ID": template_match_job_id,
            "JOB_TYPE_CODE": 0,
            "INPUT_TEMPLATE_MATCH_ID": 0,
            "IMAGE_ASSET_ID": image_info.iloc[result[0]]["IMAGE_ASSET_ID"],
            "REFERENCE_VOLUME_ASSET_ID": template_vol_ids[parameters[result[0]].input_reconstruction_filename],
            "IS_ACTIVE": 1,
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
            "HIGH_RESOLUTION_LIMIT": parameters[result[0]].high_resolution_limit_search,
            "OUT_OF_PLANE_ANGULAR_STEP": parameters[result[0]].angular_step,
            "IN_PLANE_ANGULAR_STEP": parameters[result[0]].in_plane_angular_step,
            "DEFOCUS_SEARCH_RANGE": parameters[result[0]].defocus_search_range,
            "DEFOCUS_STEP": parameters[result[0]].defocus_step,
            "PIXEL_SIZE_SEARCH_RANGE": parameters[result[0]].pixel_size_search_range,
            "PIXEL_SIZE_STEP": parameters[result[0]].pixel_size_step,
            "REFINEMENT_THRESHOLD": 0.0,
            "USED_THRESHOLD": threshold,
            "REF_BOX_SIZE_IN_ANGSTROMS": 0,
            "MASK_RADIUS": 0.0,
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
        create_peak_lists(conn, template_match_id)
        result[1].to_sql(f"TEMPLATE_MATCH_PEAK_LIST_{template_match_id}", conn, if_exists="append", index=False)
        conn.commit()
        result[1]['ORIGINAL_PEAK_NUMBER'] = 0
        result[1]['NEW_PEAK_NUMBER'] = 0
        print(result[1])
        result[1].to_sql(f"TEMPLATE_MATCH_PEAK_CHANGE_LIST_{template_match_id}", conn, if_exists="append", index=False)
        template_match_id += 1
    template_match_result_list = pd.DataFrame(template_match_result_list)
    template_match_result_list.to_sql("TEMPLATE_MATCH_LIST", conn, if_exists="append", index=False)

 
    conn.close()


async def handle_results(reader, writer, logger, parameters, write_directly_to_db, image_info):
    logger.debug("Handling results")
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
    struct.unpack("<f",results[20:24])[0]
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
    histogram = np.frombuffer(results,offset=24+8*num_pixels*4, count=num_histogram_points,dtype=np.int64).copy()
    survival_histogram = np.zeros(num_histogram_points, dtype=np.float32)
    survival_histogram[-1] = histogram[-1]
    for line_counter in range(num_histogram_points - 2, -1, -1):
        survival_histogram[line_counter] = survival_histogram[line_counter + 1] + histogram[line_counter]
    
   
    # Calculate expected threshold
    from scipy.special import erfcinv,erfc
    expected_threshold = np.sqrt(2.0) * erfcinv(2.0/(x_dim*y_dim*num_ccs)) * 1

    histogram_min              = -12.5
    histogram_max              = 22.5
    histogram_step        = (histogram_max - histogram_min) / num_histogram_points
    temp_float = histogram_min + (histogram_step / 2.0)

    expected_survival_histogram = np.zeros(num_histogram_points, dtype=np.float32)
    for line_counter in range(num_histogram_points):
        expected_survival_histogram[line_counter] = (erfc((temp_float + histogram_step * float(line_counter)) / np.sqrt(2.0)) / 2.0) * (x_dim*y_dim*num_ccs)
    
    survival_histogram_float  = survival_histogram * (expected_survival_histogram.sum() / survival_histogram.sum())
    with open(par.output_histogram_file, 'w') as f:
        f.write(f"# Expected threshold = {expected_threshold:.2f}\n")
        f.write("#  histogram, expected histogram, survival histogram, expected survival histogram\n")
        for line_counter in range(num_histogram_points):
            temp_double_array = [
                temp_float + histogram_step * float(line_counter),
                histogram[line_counter],
                survival_histogram[line_counter],
                expected_survival_histogram[line_counter]
            ]
            f.write(" ".join(str(x) for x in temp_double_array) + "\n")
    mrcfile.write(par.scaled_mip_output_file, scaled_mip.astype(np.float32), overwrite=True)
    peak_coordinates = peak_local_max(scaled_mip, min_distance=int(par.min_peak_radius), exclude_border=50, threshold_abs=expected_threshold)
    result = pd.DataFrame({
        "X_POSITION": peak_coordinates[:,1] * par.pixel_size,
        "Y_POSITION": peak_coordinates[:,0] * par.pixel_size,
        "PSI": psi[tuple(peak_coordinates.T)],
        "THETA": theta[tuple(peak_coordinates.T)],
        "PHI": phi[tuple(peak_coordinates.T)],
        "DEFOCUS": defocus[tuple(peak_coordinates.T)],
        "PEAK_HEIGHT": scaled_mip[tuple(peak_coordinates.T)]
    })
    if(write_directly_to_db):
        image_info["THRESHOLD"].iat[result_number] = expected_threshold
        write_results_to_database(image_info.iloc[result_number]["DATABASE"], parameters, [(result_number, result)], image_info)
        print("Wrote results to database")
    print(f"{par.input_search_images_filename}: {len(result)} peaks found. Median {result['PEAK_HEIGHT'].median()} Max {result['PEAK_HEIGHT'].max()} Threshold {expected_threshold}")
    return(result)

async def handle_job_result_queue(reader, writer, logger):
    #logger.info("Handling results")
    #await reader.read(4)
    length = await reader.readexactly(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    results = await reader.readexactly(number_of_bytes)
    number_of_jobs = int.from_bytes(results[0:4], byteorder="little")
    # print(f"Number of bytes: {number_of_bytes} Number of jobs: {number_of_jobs}")
    #for i in range(number_of_jobs):
    #    job_number = int.from_bytes(results[4+i*4:8+i*4], byteorder="little")
    #    result_size = int.from_bytes(results[8+i*4:12+i*4], byteorder="little")
        
    #    logger.info(f"Job {job_number} finished with result {result_number}")
    return(results)



def run(parameters: Union[MatchTemplateParameters,list[MatchTemplateParameters],pd.DataFrame],write_directly_to_db=False,image_info=None,**kwargs):

    if isinstance(parameters, pd.DataFrame):
        image_info = parameters
        parameters = image_info["PARAMETERS"].tolist()
    if not isinstance(parameters, list):
        parameters = [parameters]

    signal_handlers = {
        socket_program_defined_result : partial(handle_results, parameters = parameters, write_directly_to_db=write_directly_to_db,image_info=image_info),
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
