from pathlib import Path

def extract_particles(starfile_filename: Path, stack_filename: Path, box_size: int = 256):
    """Extract particles from a star file and save them as individual images.

    Args:
        starfile_filename (str): The filename of the star file.
        box_size (int, optional): The size of the extracted particles. Defaults to 256.
    """
    import starfile
    import mrcfile
    import numpy as np
    from itertools import groupby
    particle_info = starfile.read(starfile_filename)
    mrc = mrcfile.new_mmap(stack_filename, (len(particle_info), box_size, box_size), mrc_mode=2, overwrite=True)
    # Iterate over groupby cisTEMOriginalImageFilename

    for micrograph_filename, subparticles in groupby(particle_info.itertuples(), lambda x: x.cisTEMOriginalImageFilename):
        micrograph = mrcfile.open(micrograph_filename)
        if micrograph.data.ndim == 3:
            micrograph_data  = micrograph.data[0].copy()
        else:
            micrograph_data = micrograph.data.copy()
        for particle in subparticles:
            x = round(particle.cisTEMOriginalXPosition/particle.cisTEMPixelSize)
            y = round(particle.cisTEMOriginalYPosition/particle.cisTEMPixelSize)
            particle_image = micrograph_data.take(range(y-box_size//2, y+box_size//2), mode='clip', axis=0).take(range(x-box_size//2, x+box_size//2), mode='clip', axis=1)
            if particle_image.shape != (box_size, box_size):
                raise ValueError(f"Particle at {x},{y} from micrograph {micrograph_filename} {micrograph_data.shape} is out of bounds {particle_image.shape}.")
            
            particle_image -= particle_image.mean()
            particle_image /= particle_image.std()
            mrc.data[particle.cisTEMPositionInStack-1] = particle_image
            yield
    mrc.close()
    return
