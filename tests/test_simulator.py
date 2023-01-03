from pycistem.programs.simulate import *

pa = SimulateParameters(output_filename="out.mrc",
                        make_3d="yes",
                        output_size=320,
                        input_pdb_file="6swa.pdb",
                        pixel_size=1.0,)
run(pa)