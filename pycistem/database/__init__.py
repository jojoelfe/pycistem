import contextlib
import sqlite3
from pathlib import Path
from selectors import EpollSelector
from pycistem.core import Project
from datetime import datetime

import mrcfile
import pandas as pd
import starfile
import mdocfile

from typing import Union, List, Optional

def create_project(
        project_name: str,
        output_dir: Path):
    Path(output_dir, project_name).mkdir(parents=True, exist_ok=True)
    project = Project()
    success = project.CreateNewProject(
        Path(output_dir, project_name, f"{project_name}.db").as_posix(),
        Path(output_dir, project_name).as_posix(),
        project_name,
    )
    return Path(output_dir, project_name, f"{project_name}.db")
    
def import_movies(project_path: Union[str, Path], movies: Union[str, Path, List[Union[str, Path]]], pixelsize: float, exposure_dose: float, pattern="*.tif", gain: Union[bool, str, Path] = True, import_metadata: bool = True, bin_to_pixelsize: float = 1.0):
    if isinstance(project_path, Path):
        project_path = project_path.as_posix()
    project = Project()
    project.OpenProjectFromFile(project_path)
    num_movies = project.database.ReturnSingleLongFromSelectCommand(
        "SELECT COUNT(*) FROM MOVIE_ASSETS;"
    )
    if isinstance(movies, str) or isinstance(movies, Path):
        movies = Path(movies)
        if movies.is_dir():
            movies = list(movies.glob(pattern))
        else:
            movies = [movies]
    movies = [Path(m).as_posix() for m in movies]
    
    movie_filenames = sorted(
        movies
    )
    if isinstance(gain, bool) and gain:
        gain_filenames = [list(Path(movie).parent.glob("*.dm4"))[0] for movie in movie_filenames]
    metadata_entries = []
    for i, movie in enumerate(movie_filenames):
        metadata = mdocfile.read(movie + ".mdoc")
        metadata_entries.append(metadata.iloc[0])
        # Insert data in MOVIE_ASSETS_METADATA using sqlite3
        project.database.ExecuteSQL(
            f"INSERT INTO MOVIE_ASSETS_METADATA "
            f"(MOVIE_ASSET_ID,"
            f"METADATA_SOURCE,"
            f"CONTENT_JSON,"
            f"TILT_ANGLE,"
            f"STAGE_POSITION_X,"
            f"STAGE_POSITION_Y,"
            f"STAGE_POSITION_Z,"
            f"IMAGE_SHIFT_X,"
            f"IMAGE_SHIFT_Y,"
            f"EXPOSURE_DOSE,"
            f"ACQUISITION_TIME)"
            f"VALUES ({i+1},"
            f"'serialem_frames_mdoc',"
            f"'{metadata.iloc[0].to_json(default_handler=str)}',"
            f" {metadata.loc[0,'TiltAngle']},"
            f" {metadata.loc[0,'StagePosition'][0]},"
            f" {metadata.loc[0,'StagePosition'][1]},"
            f" {metadata.loc[0,'StageZ']},"
            f" {metadata.loc[0,'ImageShift'][0]},"
            f" {metadata.loc[0,'ImageShift'][1]},"
            f" {metadata.loc[0,'ExposureDose']},"
            f" {datetime_to_msdos(datetime.strptime(metadata.loc[0,'DateTime'],'%d-%b-%Y %H:%M:%S'))});"
        )
    project.database.BeginMovieAssetInsert()
    for i, movie in enumerate(movie_filenames):
        project.database.AddNextMovieAsset(
            i + 1,
            Path(movie).name,
            movie,
            0,
            11520,
            8184,
            34,
            300,
            pixelsize,
            exposure_dose,
            2.7,
            gain_filenames[i].as_posix(),
            "",
            bin_to_pixelsize / pixelsize,
            0,
            0,
            1.0,
            1.0,
            0,
            25,
            1,
        )
    project.database.EndMovieAssetInsert()

    project.database.Close(True)
    return(len(movie_filenames))




def get_image_info_from_db(project,image_asset=None, get_ctf=True):
    with contextlib.closing(sqlite3.connect(project)) as con:
        if image_asset is None:
            df1 = pd.read_sql_query("SELECT IMAGE_ASSET_ID,MOVIE_ASSET_ID,IMAGE_ASSETS.FILENAME, MOVIE_ASSETS.FILENAME as movie_filename, MOVIE_ASSETS.GAIN_FILENAME, CTF_ESTIMATION_ID , ALIGNMENT_ID, IMAGE_ASSETS.PIXEL_SIZE as image_pixel_size, IMAGE_ASSETS.VOLTAGE, IMAGE_ASSETS.SPHERICAL_ABERRATION, MOVIE_ASSETS.PIXEL_SIZE as movie_pixel_size, IMAGE_ASSETS.X_SIZE, IMAGE_ASSETS.Y_SIZE FROM IMAGE_ASSETS LEFT OUTER JOIN MOVIE_ASSETS ON MOVIE_ASSETS.MOVIE_ASSET_ID == IMAGE_ASSETS.PARENT_MOVIE_ID", con)
        else:
            df1 = pd.read_sql_query(f"SELECT IMAGE_ASSET_ID,MOVIE_ASSET_ID,IMAGE_ASSETS.FILENAME, MOVIE_ASSETS.FILENAME as movie_filename, CTF_ESTIMATION_ID , ALIGNMENT_ID, IMAGE_ASSETS.PIXEL_SIZE as image_pixel_size, IMAGE_ASSETS.VOLTAGE, IMAGE_ASSETS.SPHERICAL_ABERRATION, MOVIE_ASSETS.PIXEL_SIZE as movie_pixel_size, IMAGE_ASSETS.X_SIZE, IMAGE_ASSETS.Y_SIZE FROM IMAGE_ASSETS LEFT OUTER JOIN MOVIE_ASSETS ON MOVIE_ASSETS.MOVIE_ASSET_ID == IMAGE_ASSETS.PARENT_MOVIE_ID WHERE IMAGE_ASSETS.IMAGE_ASSET_ID = {image_asset} ", con)
        if not get_ctf:
            return(df1)
        df2 = pd.read_sql_query("SELECT CTF_ESTIMATION_ID,DEFOCUS1,DEFOCUS2,DEFOCUS_ANGLE,OUTPUT_DIAGNOSTIC_FILE,SCORE, DETECTED_RING_RESOLUTION, AMPLITUDE_CONTRAST FROM ESTIMATED_CTF_PARAMETERS",con)
        selected_micrographs = pd.merge(df1,df2,on="CTF_ESTIMATION_ID")
    if image_asset is None:
        return(selected_micrographs)
    else:
        if selected_micrographs.shape[0] > 0:
            return(selected_micrographs.iloc[0])
        else:
            return(None)

def get_movie_info_from_db(project):
    with contextlib.closing(sqlite3.connect(project)) as con:
        df1 = pd.read_sql_query("SELECT * FROM MOVIE_ASSETS", con)

    return(df1)


def get_tm_info_from_db(project,image_asset,tm_id=None):
    with contextlib.closing(sqlite3.connect(project)) as con:
        if tm_id is None:
            df1 = pd.read_sql_query(f"SELECT * FROM TEMPLATE_MATCH_LIST WHERE IMAGE_ASSET_ID={image_asset}",con)
        else:
            df1 = pd.read_sql_query(f"SELECT * FROM TEMPLATE_MATCH_LIST WHERE IMAGE_ASSET_ID={image_asset} AND TEMPLATE_MATCH_JOB_ID={tm_id}",con)

    if tm_id is None:
        return(df1)
    else:
        if df1.shape[0] > 0:
            return(df1.iloc[0])
        else:
            return(None)



def ensure_template_is_a_volume_asset(project: str, template_filename: str, pixel_size: float) -> int:
    with contextlib.closing(sqlite3.connect(project)) as con:
        df1 = pd.read_sql_query(f"SELECT * FROM VOLUME_ASSETS WHERE FILENAME='{template_filename}'",con)
        if df1.shape[0] > 0:
            return(df1.iloc[0]["VOLUME_ASSET_ID"])
        else:
            # Open using mrcfile and get dimensions
            with mrcfile.open(template_filename) as mrc:
                x_size = mrc.header.nx
                y_size = mrc.header.ny
                z_size = mrc.header.nz
            #Get highest VOLUME_ASSET_ID
            df2 = pd.read_sql_query("SELECT MAX(VOLUME_ASSET_ID) as max_id FROM VOLUME_ASSETS",con)
            max_id = df2.iloc[0]["max_id"]
            if max_id is None:
                vol_id = 1
            else:
                vol_id = max_id + 1
            con.execute(f"INSERT INTO VOLUME_ASSETS (VOLUME_ASSET_ID,NAME,FILENAME,PIXEL_SIZE,X_SIZE,Y_SIZE,Z_SIZE) VALUES ('{vol_id}','{Path(template_filename).stem}','{template_filename}','{pixel_size}','{x_size}','{y_size}','{z_size}')")
            con.commit()
            return(vol_id)


def write_match_template_to_starfile(project, filename,overwrite=True, switch_phi_psi=False):

    result_peaks = pd.DataFrame({
        "image_filename": pd.Series(dtype="object"),
        "template_filename": pd.Series(dtype="object"),
        "energy": pd.Series(dtype="float"),
        "Cs": pd.Series(dtype="float"),
        "amplitude_contrast": pd.Series(dtype="float"),
        "phase_shift": pd.Series(dtype="float"),
        "defocus1": pd.Series(dtype="float"),
        "defocus2": pd.Series(dtype="float"),
        "defocus_angle": pd.Series(dtype="float"),
        "peak_number": pd.Series(dtype="int"),
        "x": pd.Series(dtype="float"),
        "y": pd.Series(dtype="float"),
        "psi": pd.Series(dtype="float"),
        "theta": pd.Series(dtype="float"),
        "phi": pd.Series(dtype="float"),
        "defocus": pd.Series(dtype="float"),
        "pixel_size": pd.Series(dtype="float"),
        "peak_value": pd.Series(dtype="float")
        })

    with contextlib.closing(sqlite3.connect(project)) as con:
        df1 = pd.read_sql_query("SELECT * FROM TEMPLATE_MATCH_LIST",con)
        for _i, tmres in df1.iterrows():
            image =  pd.read_sql_query(f"SELECT FILENAME FROM IMAGE_ASSETS WHERE IMAGE_ASSET_ID = {tmres['IMAGE_ASSET_ID']}",con)
            volume = pd.read_sql_query(f"SELECT FILENAME FROM VOLUME_ASSETS WHERE VOLUME_ASSET_ID = {tmres['REFERENCE_VOLUME_ASSET_ID']}",con)
            df2 = pd.read_sql_query(f"SELECT * FROM TEMPLATE_MATCH_PEAK_LIST_{tmres['TEMPLATE_MATCH_ID']}",con)
            for _j, peakres in df2.iterrows():
                new_peak_series = pd.Series([
                    image["FILENAME"].iloc[0],
                    volume["FILENAME"].iloc[0],
                    tmres["USED_VOLTAGE"],
                    tmres["USED_SPHERICAL_ABERRATION"],
                    tmres["USED_AMPLITUDE_CONTRAST"],
                    tmres["USED_PHASE_SHIFT"],
                    tmres["USED_DEFOCUS1"],
                    tmres["USED_DEFOCUS2"],
                    tmres["USED_DEFOCUS_ANGLE"],
                    peakres["PEAK_NUMBER"],
                    peakres["X_POSITION"],
                    peakres["Y_POSITION"],
                    peakres["PSI"],
                    peakres["THETA"],
                    peakres["PHI"],
                    peakres["DEFOCUS"],
                    peakres["PIXEL_SIZE"],
                    peakres["PEAK_HEIGHT"]
                    ], index = result_peaks.columns)
                result_peaks.loc[len(result_peaks.index)] = new_peak_series

    # Due to a bug in cisTEM in earlier matches phi and psi are switched in the
    # database
    if(switch_phi_psi):
        temp = result_peaks["phi"]
        result_peaks["phi"] = result_peaks["psi"]
        result_peaks["psi"] = temp
    starfile.write(result_peaks, filename=filename, overwrite=overwrite)


def datetime_to_msdos(now):
    msdos_date = ((now.year - 1980) << 9) | (now.month << 5) | now.day
    msdos_time = (now.hour << 11) | (now.minute << 5) | (now.second // 2)

    msdos_datetime = (msdos_date << 16) | msdos_time

    return msdos_datetime

def create_peak_lists(con, id: int):
    cur = con.cursor()
    cur.execute(f"CREATE TABLE TEMPLATE_MATCH_PEAK_LIST_{id} (PEAK_NUMBER INTEGER PRIMARY KEY AUTOINCREMENT, X_POSITION REAL, Y_POSITION REAL, PSI REAL, THETA REAL, PHI REAL, DEFOCUS REAL, PIXEL_SIZE REAL, PEAK_HEIGHT REAL)")
    con.commit()
    cur.execute(f"CREATE TABLE TEMPLATE_MATCH_PEAK_CHANGE_LIST_{id} (PEAK_NUMBER INTEGER PRIMARY KEY AUTOINCREMENT, X_POSITION REAL, Y_POSITION REAL, PSI REAL, THETA REAL, PHI REAL, DEFOCUS REAL, PIXEL_SIZE REAL, PEAK_HEIGHT REAL, ORIGINAL_PEAK_NUMBER REAL, NEW_PEAK_NUMBER REAL)")
    con.commit()

def get_max_match_template_job_id(database):
    with contextlib.closing(sqlite3.connect(database)) as con:
        cur = con.cursor()
        cur.execute("SELECT MAX(TEMPLATE_MATCH_JOB_ID) FROM TEMPLATE_MATCH_LIST")
        max_match_template_job_id = cur.fetchone()[0]
    return(max_match_template_job_id)

def get_already_processed_images(database, match_template_job_id):
    with contextlib.closing(sqlite3.connect(database)) as con:
        already_processed_images = pd.read_sql_query(f"SELECT IMAGE_ASSET_ID FROM TEMPLATE_MATCH_LIST WHERE TEMPLATE_MATCH_JOB_ID = {match_template_job_id}",con)
    return(already_processed_images)

def get_num_images(database):
    with contextlib.closing(sqlite3.connect(database)) as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM IMAGE_ASSETS")
        num_images = cur.fetchone()[0]
    return(num_images)

def get_num_movies(database):
    with contextlib.closing(sqlite3.connect(database)) as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM MOVIE_ASSETS")
        num_movies = cur.fetchone()[0]
    return(num_movies)