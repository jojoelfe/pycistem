import asyncio
import datetime
import sqlite3
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

import mrcfile
import pandas as pd

from pycistem.database import datetime_to_msdos, get_image_info_from_db
from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_send_next_job


@dataclass
class CtffindParameters:
    input_filename : str
    input_is_a_movie: bool = True
    number_of_frames_to_average : int = 3
    output_diagnostic_filename : str = "diagnostic.mrc"
    pixel_size_of_input_image : float = 1.0
    acceleration_voltage : float = 300.0
    spherical_aberration : float = 2.7
    amplitude_contrast: float = 0.07
    box_size: int = 512
    minimum_resolution: float = 30.0
    maximum_resolution: float = 5.0
    minimum_defocus: float = 3000.0
    maximum_defocus: float = 30000.0
    defocus_search_step: float = 100.0
    slower_search: bool = False
    astigmatism_tolerance: float = -100.0
    find_additional_phase_shift: bool = False
    minimum_additional_phase_shift: float = 0.0
    maximum_additional_phase_shift: float = 0.0
    additional_phase_shift_search_step: float = 0.0
    astigmatism_is_known: bool = False
    known_astigmatism: float = 0.0
    known_astigmatism_angle: float = 0.0
    resample_if_pixel_too_small: bool = True
    movie_is_gain_corrected: bool = False
    gain_filename: str = "gain.mrc"
    movie_is_dark_corrected: bool = True
    dark_filename: str = "dark.mrc"
    correct_movie_mag_distortion: bool = False
    movie_mag_distortion_angle: float = 0.0
    movie_mag_distortion_major_scale: float = 1.0
    movie_mag_distortion_minor_scale: float = 1.0
    defocus_is_known: bool = False
    known_defocus_1: float = 0.0
    known_defocus_2: float = 0.0
    known_phase_shift: float = 0.0
    determine_tilt: bool = False
    desired_number_of_threads: int = 1
    eer_frames_per_image: int = 0
    eer_super_res_factor: int = 1
    fit_nodes: bool = False
    fit_nodes_1D_brute_force: bool = True
    fit_nodes_2D_refine: bool = True
    fit_nodes_low_resolution_limit: float = 30.0
    fit_nodes_high_resolution_limit: float = 4.0
    target_pixel_size_after_resampling: float = 1.4
    fit_nodes_use_rounded_square: bool = False
    fit_nodes_downweight_nodes: bool = False

def parameters_from_database(database, decolace=False, **kwargs):
    image_info = get_image_info_from_db(database,get_ctf=False)
    ProjectDirectory = Path(database).parent
    par = [CtffindParameters(
        input_filename = image["movie_filename"],
        pixel_size_of_input_image = image["movie_pixel_size"],
        gain_filename=image["GAIN_FILENAME"],
        output_diagnostic_filename=(ProjectDirectory / "Assets" / "CTF" / f"{Path(image['FILENAME']).stem}_{image['MOVIE_ASSET_ID']}_auto.mrc").as_posix(),
        fit_nodes=True
    ) for i,image in image_info.iterrows()]
    return((par, image_info))


def write_results_to_database(database,  parameters: list[CtffindParameters], results, image_info):
    conn = sqlite3.connect(database, isolation_level=None)
    cur = conn.cursor()
    results = sorted(results, key=lambda x: x["parameter_index"])
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
            "IMAGE_ASSET_ID": image_info.loc[result["parameter_index"]]["IMAGE_ASSET_ID"],
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
    
    cur = conn.cursor()
    cur.executemany("UPDATE IMAGE_ASSETS SET CTF_ESTIMATION_ID = ? WHERE IMAGE_ASSET_ID = ?",[
        (row["CTF_ESTIMATION_ID"], row["IMAGE_ASSET_ID"])
        for i, row in ESTIMATED_CTF_PARAMETERS_LIST.iterrows()
    ])
    conn.commit()
    # Update CTF_ESTIMATION_ID in IMAGE_ASSETS table

    conn.close()

async def handle_results(reader, writer, logger):
    #logger.info("Handling results")
    await reader.read(4)
    length = await reader.read(4)
    number_of_bytes = int.from_bytes(length, byteorder="little")
    results = await reader.read(number_of_bytes*4)
    return(results)

signal_handlers = {
    socket_send_next_job : handle_results
}

def run(parameters: Union[CtffindParameters,list[CtffindParameters]],**kwargs):

    if not isinstance(parameters, list):
        parameters = [parameters]

    byte_results = asyncio.run(cistem_program.run("ctffind", parameters, signal_handlers=signal_handlers,**kwargs))
    result_ctf = []

    for parameter_index,byte_result in byte_results:
        defocus1 = struct.unpack("<f",byte_result[0:4])[0]
        defocus2 = struct.unpack("<f",byte_result[4:8])[0]
        astigmatism_angle = struct.unpack("<f",byte_result[8:12])[0]
        phase_shift = struct.unpack("<f",byte_result[12:16])[0]
        score = struct.unpack("<f",byte_result[16:20])[0]
        fit_resolution = struct.unpack("<f",byte_result[20:24])[0]
        aliasing_resolution = struct.unpack("<f",byte_result[24:28])[0]
        iciness = struct.unpack("<f",byte_result[28:32])[0]
        tilt_angle = struct.unpack("<f",byte_result[32:36])[0]
        tilt_axis = struct.unpack("<f",byte_result[36:40])[0]
        sample_thickness = struct.unpack("<f",byte_result[40:44])[0]

        result_ctf.append({
            "parameter_index" : parameter_index,
            "defocus1" : defocus1,
            "defocus2" : defocus2,
            "astigmatism_angle" : astigmatism_angle,
            "phase_shift" : phase_shift,
            "score" : score,
            "fit_resolution" : fit_resolution,
            "aliasing_resolution" : aliasing_resolution,
            "iciness" : iciness,
            "tilt_angle" : tilt_angle,
            "tilt_axis" : tilt_axis,
            "sample_thickness" : sample_thickness
        })


    return(result_ctf)

async def run_async(parameters: Union[CtffindParameters,list[CtffindParameters]],**kwargs):

    if not isinstance(parameters, list):
        parameters = [parameters]

    byte_results = await cistem_program.run("ctffind", parameters, signal_handlers=signal_handlers,**kwargs)
    result_ctf = []

    for parameter_index,byte_result in byte_results:
        defocus1 = struct.unpack("<f",byte_result[0:4])[0]
        defocus2 = struct.unpack("<f",byte_result[4:8])[0]
        astigmatism_angle = struct.unpack("<f",byte_result[8:12])[0]
        phase_shift = struct.unpack("<f",byte_result[12:16])[0]
        score = struct.unpack("<f",byte_result[16:20])[0]
        fit_resolution = struct.unpack("<f",byte_result[20:24])[0]
        aliasing_resolution = struct.unpack("<f",byte_result[24:28])[0]
        iciness = struct.unpack("<f",byte_result[28:32])[0]
        tilt_angle = struct.unpack("<f",byte_result[32:36])[0]
        tilt_axis = struct.unpack("<f",byte_result[36:40])[0]
        sample_thickness = struct.unpack("<f",byte_result[40:44])[0]

        result_ctf.append({
            "parameter_index" : parameter_index,
            "defocus1" : defocus1,
            "defocus2" : defocus2,
            "astigmatism_angle" : astigmatism_angle,
            "phase_shift" : phase_shift,
            "score" : score,
            "fit_resolution" : fit_resolution,
            "aliasing_resolution" : aliasing_resolution,
            "iciness" : iciness,
            "tilt_angle" : tilt_angle,
            "tilt_axis" : tilt_axis,
            "sample_thickness" : sample_thickness
        })


    return(result_ctf)