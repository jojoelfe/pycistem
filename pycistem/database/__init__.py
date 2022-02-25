import contextlib
from selectors import EpollSelector
import pandas as pd
import sqlite3

def get_image_info_from_db(project,image_asset=None):
    with contextlib.closing(sqlite3.connect(project)) as con:
        if image_asset is None:
            df1 = pd.read_sql_query(f"SELECT IMAGE_ASSET_ID,MOVIE_ASSET_ID,IMAGE_ASSETS.FILENAME, MOVIE_ASSETS.FILENAME as movie_filename, CTF_ESTIMATION_ID , ALIGNMENT_ID, IMAGE_ASSETS.PIXEL_SIZE as image_pixel_size, IMAGE_ASSETS.VOLTAGE, IMAGE_ASSETS.SPHERICAL_ABERRATION, MOVIE_ASSETS.PIXEL_SIZE as movie_pixel_size, IMAGE_ASSETS.X_SIZE, IMAGE_ASSETS.Y_SIZE FROM IMAGE_ASSETS LEFT OUTER JOIN MOVIE_ASSETS ON MOVIE_ASSETS.MOVIE_ASSET_ID == IMAGE_ASSETS.PARENT_MOVIE_ID", con)
        else:
            df1 = pd.read_sql_query(f"SELECT IMAGE_ASSET_ID,MOVIE_ASSET_ID,IMAGE_ASSETS.FILENAME, MOVIE_ASSETS.FILENAME as movie_filename, CTF_ESTIMATION_ID , ALIGNMENT_ID, IMAGE_ASSETS.PIXEL_SIZE as image_pixel_size, IMAGE_ASSETS.VOLTAGE, IMAGE_ASSETS.SPHERICAL_ABERRATION, MOVIE_ASSETS.PIXEL_SIZE as movie_pixel_size, IMAGE_ASSETS.X_SIZE, IMAGE_ASSETS.Y_SIZE FROM IMAGE_ASSETS LEFT OUTER JOIN MOVIE_ASSETS ON MOVIE_ASSETS.MOVIE_ASSET_ID == IMAGE_ASSETS.PARENT_MOVIE_ID WHERE IMAGE_ASSETS.IMAGE_ASSET_ID = {image_asset} ", con)

        df2 = pd.read_sql_query("SELECT CTF_ESTIMATION_ID,DEFOCUS1,DEFOCUS2,DEFOCUS_ANGLE,OUTPUT_DIAGNOSTIC_FILE,SCORE, DETECTED_RING_RESOLUTION, AMPLITUDE_CONTRAST FROM ESTIMATED_CTF_PARAMETERS",con)
        selected_micrographs = pd.merge(df1,df2,on="CTF_ESTIMATION_ID")
    if image_asset is None:
        return(selected_micrographs)
    else:
        if selected_micrographs.shape[0] > 0:
            return(selected_micrographs.iloc[0])
        else:
            return(None)

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

