import pandas as pd
from typing import Union
import sqlite3
import typer
from pathlib import Path
from typing_extensions import Annotated
import matplotlib.pyplot as plt

app = typer.Typer()

def return_class_occupancies(row, db):
    class_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_DETAILS_{row['REFINEMENT_ID']}", db)
    return [row['REFINEMENT_ID']] + class_info['AVERAGE_OCCUPANCY'].to_list()

def return_num_part_with_occ_higher_than(row, db, min_occ):
    class_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_DETAILS_{row['REFINEMENT_ID']}", db)
    result = [row['REFINEMENT_ID']]
    for class_id in class_info['CLASS_NUMBER']:
        particle_info = pd.read_sql_query(f"SELECT OCCUPANCY FROM REFINEMENT_RESULT_{row['REFINEMENT_ID']}_{class_id}", db)
        result.append(len(particle_info[particle_info['OCCUPANCY'] > min_occ]))
    print(result)
    return result

@app.command()
def plot(database: Annotated[Path, typer.Argument(...,help="The database file to use")],
        start_refinement: Annotated[int, typer.Argument(...,help="The refinement to start from")]):
    db = sqlite3.connect(database)
    refinements = []
    refinment_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_LIST WHERE REFINEMENT_ID = {start_refinement}", db)
    while len(refinment_info) == 1:
        reference_refinement_id = refinment_info["REFINEMENT_ID"].values[0]
        refinements.append(refinment_info)
        refinment_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_LIST WHERE STARTING_REFINEMENT_ID = {reference_refinement_id}", db)
    refinements = pd.concat(refinements)
    av_occs = refinements.apply(return_class_occupancies, axis=1, result_type='expand', args=(db,))
    av_occs.plot(x=0)
    plt.savefig("average_occupancies.png")
    plt.figure()
    occ_0_5 = refinements.apply(return_num_part_with_occ_higher_than, axis=1, result_type='expand', args=(db, 50))
    occ_0_5.plot(x=0)
    plt.savefig("occupancies_0_5.png")
    plt.figure()
    occ_0_9 = refinements.apply(return_num_part_with_occ_higher_than, axis=1, result_type='expand', args=(db, 90))
    occ_0_9.plot(x=0)
    plt.savefig("occupancies_0_9.png")

        
            

if __name__ == "__main__":
    app()
