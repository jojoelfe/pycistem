import pandas as pd
from typing import Union
import sqlite3
import typer
from pathlib import Path
from typing_extensions import Annotated
import starfile

app = typer.Typer()


@app.command()
def plot(database: Annotated[Path, typer.Argument(...,help="The database file to use")],
        refinement_id: Annotated[int, typer.Argument(...,help="The refinement to use")],
        class_id: Annotated[int, typer.Argument(...,help="The class to cus")],
        input_star_file: Annotated[Path, typer.Argument(...,help="The starfile to use")],
        output_star_file: Annotated[Path, typer.Argument(...,help="The starfile to write to")],
        ):
    db = sqlite3.connect(database)
    refinements = []
    refinment_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_LIST WHERE REFINEMENT_ID = {refinement_id}", db).iloc[0]
    refinment_result = pd.read_sql_query(f"SELECT * FROM REFINEMENT_RESULT_{refinement_id}_{class_id}", db)
    refinment_package_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_PACKAGE_CONTAINED_PARTICLES_{refinment_info['REFINEMENT_PACKAGE_ASSET_ID']}", db)
    
    starfile_info = starfile.read(input_star_file)

    original_ids = refinment_package_info["ORIGINAL_PARTICLE_POSITION_ASSET_ID"].to_list()
    subset_starfile_info = starfile_info.iloc[original_ids].copy()
    subset_starfile_info["cisTEMOccupancy"] = refinment_result["OCCUPANCY"].to_list()
    subset_starfile_info["cisTEMScore"] = refinment_result["SCORE"].to_list()
    starfile.write(subset_starfile_info, output_star_file)

if __name__ == "__main__":
    app()
