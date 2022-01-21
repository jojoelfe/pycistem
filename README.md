# pycistem
Python scripts inteacting with the cisTEM package


# Usage

```python
import asyncio
from pycistem.programs.refine\_template import RefineTemplateParameters, run

params = RefineTemplateParameters(input\_file="test.mrc",template="ribo.mrc")

results = asyncio.run(run(params))
```

```python
from pycistem.core import *
import matplotlib.pyplot as plt

im = Image()
spectrum = Image()

im.QuickAndDirtyReadSlice("test.mrc",1)
spectrum.AllocateSameAs(im)

im.ForwardFFT(True)
im.AmplitudeSpectrumFull2D(spectrum)
plt.imshow(spectrum)
```