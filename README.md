# pycistem
Python scripts inteacting with the cisTEM package


# Usage

from pycistem.programs.refine\_template import RefineTemplateParameters, refine\_template

params = RefineTemplateParameters(input\_file="test.mrc",template="ribo.mrc")

results = await refine\_template(params,on="bern")
