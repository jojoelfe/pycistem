import pytest

from pycistem.core import CTF, AnglesAndShifts, Image, RunProfile, RunProfileManager


@pytest.fixture
def volume():
    box_size = 384
    volume = Image()
    volume.Allocate(box_size,box_size,box_size,True,True)
    volume.ForwardFFT(True)
    volume.ZeroCentralPixel()
    volume.SwapRealSpaceQuadrants()
    return volume

@pytest.fixture
def projection():
    box_size = 384
    projection = Image()
    projection.Allocate(box_size,box_size,False)
    return projection

def test_extract_slice(volume, projection):
    phi = 0.0 # In degrees
    theta = 0.0
    psi = 0.0
    defocus1 = 8000.0
    defocus2= 8000.0
    defocus_angle = 35.0
    pixel_size = 1.5

    angles = AnglesAndShifts()
    angles.Init(phi,theta,psi,0.0,0.0)

    volume.ExtractSlice(projection,angles,1.0,False)

    projection.SwapRealSpaceQuadrants( )
    projection.BackwardFFT()

    projection.ForwardFFT(True)
    ctf = CTF(kV=300.0,cs=2.7,ac=0.07,defocus1=defocus1,defocus2=defocus2,astig_angle=defocus_angle,pixel_size=pixel_size)
    projection.ApplyCTF(ctf,False,False,False)
    projection.BackwardFFT()



def test_run_profiles():
    hosts= [
        "host1",
        "host2",
        "host3",
        #"host4",
        #"host5",
        #"host6",
        #"host7",
        #"host8",
    ]

    manager_command = "/software/CISTEM/$command"
    program_command = "/software/CISTEM/$command"
    num_threads =2
    delay=100
    rpm = RunProfileManager()
    rpm.AddBlankProfile()

    rpm.run_profiles[0].name = "64GPUs"

    rpm.run_profiles[0].manager_command = manager_command
    rpm.run_profiles[0].RemoveAll()
    for host in hosts:
        for igpu in range(0,8):
            pass
            rpm.run_profiles[0].AddCommand(f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && {program_command}"',1,num_threads,False,0,delay)


    assert rpm.run_profiles[0].name == "64GPUs"
    assert rpm.run_profiles[0].manager_command == "/software/CISTEM/$command"
    assert len(rpm.run_profiles[0].run_commands) == 24
    # TODO: This triggers a segault in pytest. Probably because we maintain pointers in the vector
    #assert rpm.run_profiles[0].run_commands[0].command_to_run == 'ssh -f host1 "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES=0 && /software/CISTEM/$command"'
    #assert rpm.run_profiles[0].run_commands[23].command_to_run == 'ssh -f host3 "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES=7 && /software/CISTEM/$command"'
