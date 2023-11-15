import pandas as pd
from typing import Union
import sqlite3
import typer
from pathlib import Path
from typing_extensions import Annotated
import matplotlib.pyplot as plt

app = typer.Typer()


@app.command()
def plot(database: Annotated[Path, typer.Argument(...,help="The database file to use")],
        start_refinement: Annotated[int, typer.Argument(...,help="The refinement to start from")]):
    db = sqlite3.connect(database)
    refinment_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_LIST WHERE REFINEMENT_ID = {start_refinement}", db)
    class_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_DETAILS_{refinment_info['REFINEMENT_ID'].values[0]}", db)
    class_info.sort_values(by="AVERAGE_OCCUPANCY", inplace=True)
    # print as a table the CLASS_NUMBER and AVERAGE_OCCUPANCY
    print(class_info[['CLASS_NUMBER', 'AVERAGE_OCCUPANCY']])

        
            

if __name__ == "__main__":
    app()
