import pandas as pd
from typing import Union
import sqlite3
import typer
from pathlib import Path
from typing_extensions import Annotated
import matplotlib.pyplot as plt
import matplotlib.animation as animation

app = typer.Typer()

def return_fsc(db,refinement,classid):
    fsc = pd.read_sql_query(f"SELECT * FROM REFINEMENT_RESOLUTION_STATISTICS_{refinement}_{classid}", db)
    return(fsc)




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

    fscs = []
    for i in range(refinements.iloc[0]['NUMBER_OF_CLASSES']):
        dat = return_fsc(db,refinements.iloc[0]['REFINEMENT_ID'],i+1)
        dat["CLASS"] = i+1
        fscs.append(dat)
    dat = pd.concat(fscs)



    fig, ax = plt.subplots()
    linplts = {}
    for key, grp in dat[dat['RESOLUTION'] > 4.0].groupby(['CLASS']):
        linplts[key] = plt.plot(grp['SHELL'], grp['PART_FSC'],label=key)[0]
    print(linplts)
    plt.ylim(0,1.05)


    def update(frame):
        fscs = []
        for i in range(refinements.iloc[frame]['NUMBER_OF_CLASSES']):
            dat = return_fsc(db,refinements.iloc[frame]['REFINEMENT_ID'],i+1)
            dat["CLASS"] = i+1
            fscs.append(dat)
        dat = pd.concat(fscs)
        for key, grp in dat[dat['RESOLUTION'] > 4.0].groupby(['CLASS']):
            print(key)
            linplts[key].set_xdata(grp['SHELL'])
            linplts[key].set_ydata(grp['PART_FSC'])



    
        return linplts.values()


    ani = animation.FuncAnimation(fig=fig, func=update, frames=len(refinements), interval=300)
    plt.show()
    
    return()

    
    
    
    av_occs = refinements.apply(return_class_occupancies, axis=1, result_type='expand', args=(db,))
    av_occs.plot(x=0)
    plt.savefig("average_occupancies.png")
    plt.figure()
    occ_0_5 = refinements.apply(return_num_part_with_occ_higher_than, axis=1, result_type='expand', args=(db, 0.5))
    occ_0_5.plot(x=0)
    plt.savefig("occupancies_0_5.png")
    plt.figure()
    occ_0_9 = refinements.apply(return_num_part_with_occ_higher_than, axis=1, result_type='expand', args=(db, 0.9))
    occ_0_9.plot(x=0)
    plt.savefig("occupancies_0_9.png")

        
            

if __name__ == "__main__":
    app()
