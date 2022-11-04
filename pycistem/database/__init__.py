import contextlib
from selectors import EpollSelector
import pandas as pd
import sqlite3
import starfile

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

def write_match_template_to_starfile(project, filename,overwrite=True, switch_phi_psi=False):

    result_peaks = pd.DataFrame({
        'image_filename': pd.Series(dtype='object'),
        'template_filename': pd.Series(dtype='object'),
        'energy': pd.Series(dtype='float'),
        'Cs': pd.Series(dtype='float'),
        'amplitude_contrast': pd.Series(dtype='float'),
        'phase_shift': pd.Series(dtype='float'),
        'defocus1': pd.Series(dtype='float'),
        'defocus2': pd.Series(dtype='float'),
        'defocus_angle': pd.Series(dtype='float'),
        'peak_number': pd.Series(dtype='int'),
        'x': pd.Series(dtype='float'),
        'y': pd.Series(dtype='float'),
        'psi': pd.Series(dtype='float'),
        'theta': pd.Series(dtype='float'),
        'phi': pd.Series(dtype='float'),
        'defocus': pd.Series(dtype='float'),
        'pixel_size': pd.Series(dtype='float'),
        'peak_value': pd.Series(dtype='float')
        })

    with contextlib.closing(sqlite3.connect(project)) as con:
        df1 = pd.read_sql_query(f"SELECT * FROM TEMPLATE_MATCH_LIST",con)
        for i, tmres in df1.iterrows():
            image =  pd.read_sql_query(f"SELECT FILENAME FROM IMAGE_ASSETS WHERE IMAGE_ASSET_ID = {tmres['IMAGE_ASSET_ID']}",con)
            volume = pd.read_sql_query(f"SELECT FILENAME FROM VOLUME_ASSETS WHERE VOLUME_ASSET_ID = {tmres['REFERENCE_VOLUME_ASSET_ID']}",con)
            df2 = pd.read_sql_query(f"SELECT * FROM TEMPLATE_MATCH_PEAK_LIST_{tmres['TEMPLATE_MATCH_ID']}",con)
            for j, peakres in df2.iterrows():
                new_peak_series = pd.Series([
                    image['FILENAME'].iloc[0],
                    volume['FILENAME'].iloc[0],
                    tmres['USED_VOLTAGE'],
                    tmres['USED_SPHERICAL_ABERRATION'],
                    tmres['USED_AMPLITUDE_CONTRAST'],
                    tmres['USED_PHASE_SHIFT'],
                    tmres['USED_DEFOCUS1'],
                    tmres['USED_DEFOCUS2'],
                    tmres['USED_DEFOCUS_ANGLE'],
                    peakres['PEAK_NUMBER'],
                    peakres['X_POSITION'],
                    peakres['Y_POSITION'],
                    peakres['PSI'],
                    peakres['THETA'],
                    peakres['PHI'],
                    peakres['DEFOCUS'],
                    peakres['PIXEL_SIZE'],
                    peakres['PEAK_HEIGHT']               
                    ], index = result_peaks.columns)
                result_peaks.loc[len(result_peaks.index)] = new_peak_series

    # Due to a bug in cisTEM in earlier matches phi and psi are switched in the
    # database
    if(switch_phi_psi):
        temp = result_peaks['phi']
        result_peaks['phi'] = result_peaks['psi']
        result_peaks['psi'] = temp
    starfile.write(result_peaks, filename=filename, overwrite=overwrite)