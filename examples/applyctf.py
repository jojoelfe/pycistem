import sqlite3

db = sqlite3.connect("database.db")
cur = db.cursor()

cur.execute("select image_assets.filename, estimated_ctf_parameters.defocus1, estimated_ctf_parameters.defocus2, estimated_ctf_parameters.defocus_angle, estimated_ctf_parameters.additional_phase_shift from image_assets where image_assets.filename like '%niceview_00182%'")
print(cur.fetchall())




import os
from subprocess import Popen, PIPE
from collections import namedtuple

ApplyCtfParameters = namedtuple("input",[
    "output",
    "pixelsize",
    "kV",
    "cs",
    "ac",
    "file",
    "defocus1",
    "defocus2",
    "astigmatism_angle",
    "phase_shift",
    "flip_only",
    "contrast"
    
],defaults = [
    "in.mrc",
    "out.mrc",
    40.0,
    300.0,
    2.7,
    0.07,
    "NO",
    100000,
    100000,
    0.0,
    0.0,
    "YES",
    "YES",
    
])

para = ApplyCtfParameters(input = "in.mrc"
                            output="out.mrc",
                          defocus1 = 300000,
                          defocus2 = 300000,
                          astigmatism_angle=0.0)

if True:
    proc = Popen("applyctf", shell=True, stdin=PIPE)
    proc.communicate(input=str.encode('\n'.join(map(str,list(para)))))