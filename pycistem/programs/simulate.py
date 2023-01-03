from pathlib import Path
from concurrent.futures import ThreadPoolExecutor 
from subprocess import Popen, PIPE
from dataclasses import dataclass
from typing import Union
from ..config import config


@dataclass
class SimulateParameters:
    output_filename: str = "out.mrc"
    make_3d: str = "yes"
    output_size: int = 320
    n_threads: int = 1
    input_pdb_file: str = "input.pdb"
    para1: str = "no"
    pixel_size: float = 1.0
    linear_scaling_of_PDB_bfactors: float = 1.0
    per_atom_bfactor: float = 4.0
    exposure_per_frame: float = 1.0
    n_frames: int = 30
    expert_options: str = "yes"
    para4: int = 1
    para5: float = 0.0
    KV: float = 300.0
    CS: float = 2.7
    OA: float = 100.0
    para6: float = 0.0
    pre_exposure: float = 0.0
    para7: int = 32
    para8: int = 10
    para9: int = 2048
    para10: float = 0.0
    para11: float = 2.0
    para12: float = 0.1
    para13: float = 0.0001
    para14: float = 0.0
    para15: float = 0.0
    para16: float = 0.0
    para17: float = 0.0
    para18: float = 0.0

def run(parameters: Union[SimulateParameters,list[SimulateParameters]],num_procs:int=1):
    if isinstance(parameters,SimulateParameters):
        parameters = [parameters]
    for p in parameters:
        assert isinstance(p,SimulateParameters)

    cmd = Path(config["CISTEM_PATH"]) / "simulate"
    cmd = str(cmd) + " --only-modify-signal-3d=2 --wgt=0.225 --water-shell-only"

    # Execute cmd in parallel for each parameter set
    def _run(p):
        proc = Popen(cmd, shell=True, stdin=PIPE)
        proc.communicate(input=str.encode('\n'.join(map(str,list(p.__dict__.values())))))

    executor = ThreadPoolExecutor(max_workers=10)
    for p in parameters:
        a = executor.submit(_run,p)
    executor.shutdown(wait=True)
    
