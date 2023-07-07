import asyncio
import datetime
import sqlite3
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

import mrcfile
import pandas as pd

from pycistem.database import datetime_to_msdos, get_movie_info_from_db
from pycistem.programs import cistem_program
from pycistem.programs._cistem_constants import socket_job_result, socket_send_next_job


@dataclass
class UnblurPatchParameters:
    input_filename: str
    output_filename: str = "unblurred.mrc"
    pixel_size: float = 1.0
    minimum_shift_in_angstroms: float = 2.00
    maximum_shift_in_angstroms: float = 40.0
    should_dose_filter: bool = True
    should_restore_power: bool = True
    termination_threshold_in_angstroms: float = 1.0
    max_iterations: int = 10
    bfactor_in_angstroms: float = 1500
    should_mask_central_cross: bool = True
    horizontal_mask_size: int = 1
    vertical_mask_size: int = 1
    acceleration_voltage: float = 300.0
    exposure_per_frame: float = 0.0
    pre_exposure_amount: float = 0.0
    movie_is_gain_corrected: bool = False
    gain_filename: str = "gain.mrc"
    movie_is_dark_corrected: bool = True
    dark_filename: str = "dark.mrc"
    output_binning_factor: float = 2.0
    correct_mag_distortion: bool = False
    mag_distortion_angle: float = 0.0
    mag_distortion_major_scale: float = 1.0
    mag_distortion_minor_scale: float = 1.0
    write_out_amplitude_spectrum: bool = True
    amplitude_spectrum_filename: str = "amplitude_spectrum.mrc"
    write_out_small_sum_image: bool = True
    small_sum_image_filename: str = "scaled_sum.mrc"
    first_frame: int = 1
    last_frame: int = 0
    number_of_frames_for_running_average: int = 1
    max_threads: int = 1
    save_aligned_frames: bool = False
    aligned_frames_filename: str = "aligned_frames.mrc"
    output_shift_text_file: str = "shifts.txt"
    eer_frames_per_image: int = 0
    eer_super_res_factor: int = 1
    outputpath: str = "/tmp"
    patchcorrection: bool = False
    patch_num_x: int = 6
    patch_num_y: int = 4
    distortion_model: int = 2

def parameters_from_database(database, decolace=False, **kwargs):
    movie_info = get_movie_info_from_db(database)
    ProjectDirectory = Path(database).parent
    par = [UnblurPatchParameters(
        input_filename = movie["FILENAME"],
        output_filename= (ProjectDirectory / "Assets" / "Images" / f"{Path(movie['FILENAME']).stem}_{movie['MOVIE_ASSET_ID']}_auto.mrc").as_posix(),
        pixel_size = movie["PIXEL_SIZE"],
        gain_filename=movie["GAIN_FILENAME"],
        output_binning_factor=movie["OUTPUT_BINNING_FACTOR"],
        exposure_per_frame=movie["DOSE_PER_FRAME"],
        amplitude_spectrum_filename=(ProjectDirectory / "Assets" / "Images" / "Spectra" / f"{Path(movie['FILENAME']).stem}_{movie['MOVIE_ASSET_ID']}_auto.mrc").as_posix(),
        small_sum_image_filename=(ProjectDirectory / "Assets" / "Images" / "Scaled" / f"{Path(movie['FILENAME']).stem}_{movie['MOVIE_ASSET_ID']}_auto.mrc").as_posix(),
        align_on_cropped_area=decolace,
        replace_dark_areas_with_gaussian_noise=decolace
    ) for i,movie in movie_info.iterrows()]
    return(par)

def write_results_to_database(database,  parameters, results):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    results = sorted(results, key=lambda x: x["parameter_index"])
    MOVIE_ALIGNMENT_LIST = []

    max_alignment_id= cur.execute("SELECT MAX(ALIGNMENT_ID) FROM MOVIE_ALIGNMENT_LIST").fetchone()[0]
    if max_alignment_id is None:
        max_alignment_id = 0
    alignment_job_id= cur.execute("SELECT MAX(ALIGNMENT_JOB_ID) FROM MOVIE_ALIGNMENT_LIST").fetchone()[0]
    if alignment_job_id is None:
        alignment_job_id = 1
    else:
        alignment_job_id += 1

    max_image_asset_id= cur.execute("SELECT MAX(IMAGE_ASSET_ID) FROM IMAGE_ASSETS").fetchone()[0]
    if max_image_asset_id is None:
        max_image_asset_id = 0
    for result in results:
        movie_info = cur.execute("SELECT X_SIZE, Y_SIZE, MOVIE_ASSET_ID, NAME, PROTEIN_IS_WHITE, SPHERICAL_ABERRATION FROM MOVIE_ASSETS WHERE FILENAME = ?", (parameters[result["parameter_index"]].input_filename,)).fetchone()
        x_bin_factor       = movie_info[0] / result["orig_x"]
        y_bin_factor       = movie_info[1] / result["orig_y"]
        average_bin_factor = (x_bin_factor + y_bin_factor) / 2.0
        actual_pixel_size = parameters[result["parameter_index"]].pixel_size * average_bin_factor
        MOVIE_ALIGNMENT_LIST.append({
                    "ALIGNMENT_ID" : max_alignment_id + 1,
                    "DATETIME_OF_RUN" : datetime_to_msdos(datetime.datetime.now()),
                    "ALIGNMENT_JOB_ID": alignment_job_id,
                    "MOVIE_ASSET_ID": movie_info[2],
                    "OUTPUT_FILE": parameters[result["parameter_index"]].output_filename,
                    "VOLTAGE": parameters[result["parameter_index"]].acceleration_voltage,
                    "PIXEL_SIZE": actual_pixel_size,
                    "EXPOSURE_PER_FRAME": parameters[result["parameter_index"]].exposure_per_frame,
                    "PRE_EXPOSURE_AMOUNT": parameters[result["parameter_index"]].pre_exposure_amount,
                    "MIN_SHIFT": parameters[result["parameter_index"]].minimum_shift_in_angstroms,
                    "MAX_SHIFT": parameters[result["parameter_index"]].maximum_shift_in_angstroms,
                    "SHOULD_DOSE_FILTER": parameters[result["parameter_index"]].should_dose_filter,
                    "SHOULD_RESTORE_POWER": parameters[result["parameter_index"]].should_restore_power,
                    "TERMINATION_THRESHOLD": parameters[result["parameter_index"]].termination_threshold_in_angstroms,
                    "MAX_ITERATIONS": parameters[result["parameter_index"]].max_iterations ,
                    "BFACTOR": parameters[result["parameter_index"]].bfactor_in_angstroms,
                    "SHOULD_MASK_CENTRAL_CROSS": parameters[result["parameter_index"]].should_mask_central_cross,
                    "HORIZONTAL_MASK": parameters[result["parameter_index"]].horizontal_mask_size,
                    "VERTICAL_MASK": parameters[result["parameter_index"]].vertical_mask_size,
                    "SHOULD_INCLUDE_ALL_FRAMES_IN_SUM": True,
                    "FIRST_FRAME_TO_SUM": parameters[result["parameter_index"]].first_frame,
                    "LAST_FRAME_TO_SUM": parameters[result["parameter_index"]].last_frame,
                    "ORIGINAL_X_SIZE": result["orig_x"],
                    "ORIGINAL_Y_SIZE": result["orig_y"],
                    "CROP_CENTER_X": result["crop_x"],
                    "CROP_CENTER_Y": result["crop_y"],
                    })
        # Check if there is existing image asset

        existing_image_asset = cur.execute("SELECT IMAGE_ASSET_ID FROM IMAGE_ASSETS WHERE PARENT_MOVIE_ID = ?",(movie_info[2],)).fetchone()
        if existing_image_asset is None:
            max_image_asset_id += 1
            image_asset_id = max_image_asset_id
        else:
            image_asset_id = existing_image_asset[0]

        mrc = mrcfile.open(parameters[result["parameter_index"]].output_filename)
        xsize = mrc.header.nx
        ysize = mrc.header.ny
        cur.execute("REPLACE INTO IMAGE_ASSETS (IMAGE_ASSET_ID, NAME, FILENAME, POSITION_IN_STACK, PARENT_MOVIE_ID, ALIGNMENT_ID, CTF_ESTIMATION_ID, X_SIZE, Y_SIZE, PIXEL_SIZE, VOLTAGE, SPHERICAL_ABERRATION, PROTEIN_IS_WHITE, ORIGINAL_X_SIZE, ORIGINAL_Y_SIZE, CROP_CENTER_X, CROP_CENTER_Y) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (image_asset_id, movie_info[3], parameters[result["parameter_index"]].output_filename, 1,movie_info[2],max_alignment_id+1, -1, int(xsize), int(ysize), actual_pixel_size, parameters[result["parameter_index"]].acceleration_voltage, movie_info[5], movie_info[4],result["orig_x"],result["orig_y"],result["crop_x"],result["crop_y"]))
        MOVIE_ALIGNMENT_PARAMETERS = {
            "FRAME_NUMBER": range(1,len(result["x_shifts"])+1),
            "X_SHIFT": result["x_shifts"],
            "Y_SHIFT": result["y_shifts"],
        }
        conn.commit()
        MOVIE_ALIGNMENT_PARAMETERS = pd.DataFrame(MOVIE_ALIGNMENT_PARAMETERS)
        MOVIE_ALIGNMENT_PARAMETERS.to_sql(f"MOVIE_ALIGNMENT_PARAMETERS_{max_alignment_id+1}", conn, if_exists="fail", index=False)
        max_alignment_id += 1
    MOVIE_ALIGNMENT_LIST = pd.DataFrame(MOVIE_ALIGNMENT_LIST)
    MOVIE_ALIGNMENT_LIST.to_sql("MOVIE_ALIGNMENT_LIST", conn, if_exists="append", index=False)
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

def run(parameters: Union[UnblurPatchParameters,list[UnblurPatchParameters]],**kwargs):

    if not isinstance(parameters, list):
        parameters = [parameters]

    byte_results = asyncio.run(cistem_program.run("unblur", parameters, signal_handlers=signal_handlers,**kwargs))
    result_shifts = []

    for parameter_index,byte_result in byte_results:
        number_of_images = int(((len(byte_result) /4 ) - 4 ) /2)
        x_shifts = []
        for offset in range(number_of_images):
            x_shifts.append(struct.unpack_from("<f",byte_result,offset=offset*4)[0])
        y_shifts = []
        for offset in range(number_of_images):
            y_shifts.append(struct.unpack_from("<f",byte_result,offset=offset*4+number_of_images*4)[0])
        orig_x = int(struct.unpack_from("<f",byte_result,offset=2*4*number_of_images)[0])
        orig_y = int(struct.unpack_from("<f",byte_result,offset=2*4*number_of_images+4)[0])
        crop_x = int(struct.unpack_from("<f",byte_result,offset=2*4*number_of_images+8)[0])
        crop_y = int(struct.unpack_from("<f",byte_result,offset=2*4*number_of_images+12)[0])
        result_shifts.append({
            "parameter_index": parameter_index,
            "x_shifts": x_shifts,
            "y_shifts": y_shifts,
            "orig_x": orig_x,
            "orig_y": orig_y,
            "crop_x": crop_x,
            "crop_y": crop_y
        })


    return(result_shifts)
