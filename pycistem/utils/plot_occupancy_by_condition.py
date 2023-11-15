import pandas as pd
from typing import Union
import sqlite3
import starfile
import typer
from pathlib import Path
from typing_extensions import Annotated
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
app = typer.Typer()


def return_num_part_per_cond_with_occ_higher_than(row, db, min_occ, tmp):
    class_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_DETAILS_{row['REFINEMENT_ID']}", db)
    all_particle_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_PACKAGE_CONTAINED_PARTICLES_{row['REFINEMENT_PACKAGE_ASSET_ID']}", db)
    
    result = []
    for class_id in class_info['CLASS_NUMBER']:
        particle_info = pd.read_sql_query(f"SELECT POSITION_IN_STACK,PSI,OCCUPANCY FROM REFINEMENT_RESULT_{row['REFINEMENT_ID']}_{class_id}", db)
        particle_info = particle_info.merge(all_particle_info, on="POSITION_IN_STACK")
        particle_info = particle_info.merge(tmp,  left_on='ORIGINAL_PARTICLE_POSITION_ASSET_ID', right_index=True)
        particle_info['experimental_condition'] = particle_info['cisTEMOriginalImageFilename'].str.split("/").str[-4]
        particle_info = particle_info[particle_info['OCCUPANCY'] > min_occ]
        result.append(particle_info['experimental_condition'].value_counts())
    return result

@app.command()
def plot(database: Annotated[Path, typer.Argument(...,help="The database file to use")],
        start_refinement: Annotated[int, typer.Argument(...,help="The refinement to start from")],
        starfile_filename: Annotated[Path, typer.Argument(...,help="The starfile to use")]):
    db = sqlite3.connect(database)
    tmp = starfile.read(starfile_filename)
    counts_in_cond = defaultdict(defaultdict[lambda: 0])
    refinment_info = pd.read_sql_query(f"SELECT * FROM REFINEMENT_LIST WHERE REFINEMENT_ID = {start_refinement}", db)
    number_per_class = return_num_part_per_cond_with_occ_higher_than(refinment_info.iloc[0], db, 0.9, tmp)
    for class_id, class_counts in enumerate(number_per_class):
        for cond, count in class_counts.items():
            exp = cond
            if class_id not in counts_in_cond[exp]:
                counts_in_cond[exp][class_id] = count
            else:
                counts_in_cond[exp][class_id] += count
    condition_list = sorted(list(counts_in_cond.keys()))
    ucs = {}
    for i, condition in enumerate(condition_list):
        exp = condition.split("_")[2]
        ucs[exp] = 1
    
    #create a categorical colormap using ListedColormap
    cmap = mcolors.ListedColormap(mcolors.TABLEAU_COLORS.values())

    # get the number of colors in the colormap
    num_colors = cmap.N

    # create a dictionary mapping each label to a color index
    color_indices = {label: i for i, label in enumerate(ucs.keys())}

    cond_position = {'24hbr': 3, '48hbr': 4, 'C': 2}
    states_this= {
        'A/P/eEF1a' : [15,19,8,4,18,3],
        'eEF2a': [11,14,10,20,9,12],
        'pA/P' : [5,2],
        'pA/P/eEF2': [6],

    }
    states_pivot = { v:k for k in states_this for v in states_this[k]}

    datas = defaultdict(list)
    state_count = {}
    for cond in cond_position.keys():
        state_count[cond] =  defaultdict(lambda: 0)

    for i, condition in enumerate(condition_list):
        #if condition.split("_")[0] != "20230317":
        #    continue
        exp = condition.split("_")[2]

        counts = np.zeros(20)
        for i in range(20):
            if i in counts_in_cond[condition]:
                counts[i] = counts_in_cond[condition][i]
        
        if np.sum(counts) < 1000:
            continue
        #make colorkei for exp
        for classid, frac in enumerate(counts):
            if classid+1 in states_pivot:
                state_count[exp][states_pivot[classid+1]] += frac
            datas[classid * 5 + cond_position[exp]].append(frac/np.sum(counts))
        #plt.plot(np.arange(len(counts))+1+i*0.1,counts/np.sum(counts), 'o', color=cmap(color_indices[exp]))
    

    pos = list(datas.keys())
    data = list(datas.values())
    state_percent = {}
    for cond in state_count.keys():
        state_percent[cond] = {}
        par_sum = np.sum(list(state_count[cond].values()))
        for state in state_count[cond].keys():
            state_percent[cond][state] = state_count[cond][state]/par_sum
    print(state_percent)
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(13, 6))

    bplot = ax.boxplot(data, positions=pos,  widths=0.7, patch_artist=True,)
    
    colors = ["red","green","green","yellow","orange"]
    for i,patch in enumerate(bplot['boxes']):
        print(i)
        patch.set_facecolor(colors[pos[i]%5])
    ax.set_title('Class occupancies grouped by condition', fontsize=10)
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='green', label='Control',
                          markerfacecolor='green', markersize=10),
                          Line2D([0], [0], marker='o', color='yellow', label='24h brequinar',
                          markerfacecolor='yellow', markersize=10),
                          Line2D([0], [0], marker='o', color='orange', label='48h brequinar',
                          markerfacecolor='orange', markersize=10)]
    ax.legend(handles=legend_elements, loc='upper left')
    plt.xticks(ticks = np.arange(20)*5 +3 , labels = np.arange(20)+1)
    plt.savefig("condition.png")
        

        
            

if __name__ == "__main__":
    app()
