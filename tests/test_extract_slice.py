from pycistem.core import Image, AnglesAndShifts, CTF
import matplotlib.pyplot as plt

box_size = 384
pixel_size = 1.5
phi = 0.0 # In degrees
theta = 0.0
psi = 0.0
defocus1 = 8000.0
defocus2= 8000.0
defocus_angle = 35.0



volume = Image()

volume.QuickAndDirtyReadSlices("/groups/elferich/mammalian_ribosome_structures/6swa_simulate_bfsca1_5.mrc",1,box_size)

volume.ForwardFFT(True)
volume.ZeroCentralPixel()
volume.SwapRealSpaceQuadrants()
angles = AnglesAndShifts()
angles.Init(phi,theta,psi,0.0,0.0)
projection = Image()
projection.Allocate(box_size,box_size,False)

volume.ExtractSlice(projection,angles,1.0,False)

projection.SwapRealSpaceQuadrants( )
projection.BackwardFFT()

plt.imshow(projection.real_values,cmap="Greys_r")
plt.show()

projection.ForwardFFT(True)
ctf = CTF(kV=300.0,cs=2.7,ac=0.07,defocus1=defocus1,defocus2=defocus2,astig_angle=defocus_angle,pixel_size=pixel_size)
projection.ApplyCTF(ctf,False,False,False)
projection.BackwardFFT()


plt.imshow(projection.real_values,cmap="Greys_r")
plt.show()

projection.QuickAndDirtyWriteSlice("projectionCTF.mrc",1,True,pixel_size)
