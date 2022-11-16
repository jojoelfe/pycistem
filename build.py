from typing import Any, Dict
# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup
from setuptools.command.build_ext import build_ext
import subprocess
import os

# CHeck if /opt/WX/intel-static/bin/wx-config exists
# If it does, use it to build the extension
# If it doesn't, use the system wx-config
if os.path.exists("/opt/WX/intel-static/bin/wx-config"):
    wx_config = "/opt/WX/intel-static/bin/wx-config"
else:
    wx_config = "wx-config"

wxflags = subprocess.run([wx_config, '--cxxflags'], stdout=subprocess.PIPE).stdout.decode('utf-8')
# Strip the newline from the wxflags
wxflags = wxflags.strip()

wxlibflags = subprocess.run([wx_config, '--libs'], stdout=subprocess.PIPE).stdout.decode('utf-8')
# Strip the newline from the wxlibflags
wxlibflags = wxlibflags.strip()

# This code pulls come key compile info out of the config.log file
__version__ = "0.1.4"
__compiler__ = "icpc"
__WX_FLAGS__ = wxflags + "  -DwxUSE_GUI=0 -IcisTEM/build/icpc"
__CPP_FLAGS__ = "-fPIC -O3 -no-prec-div -no-prec-sqrt -w2 -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -DEXPERIMENTAL -DMKL -mkl=sequential -fopenmp"
__WX_LIBS_BASE__ = wxlibflags

# Overwrite default compiler flags. It's kind of a hack to add the import flgs to the compiler string, but I think its the only way.
class custom_build_ext(build_ext):
    def build_extensions(self):
        # Override the compiler executables. Importantly, this
        # removes the "default" compiler flags that would
        # otherwise get passed on to to the compiler, i.e.,
        # distutils.sysconfig.get_var("CFLAGS").
        self.compiler.set_executable("compiler_so", __compiler__ + " " + __WX_FLAGS__ + " " + __CPP_FLAGS__ )
        self.compiler.set_executable("compiler_cxx", __compiler__ + " -fPIC " + __WX_FLAGS__ + " " + __CPP_FLAGS__)
        self.compiler.set_executable("linker_so", __compiler__  + " " + __CPP_FLAGS__ +" -shared -static-intel -qopenmp-link=static -wd10237 ")
        build_ext.build_extensions(self)

ext_modules = [
    Pybind11Extension("pycistem/core/core",
        ["pycistem/core/core.cpp",
         "pycistem/core/database.cpp",
         "pycistem/core/run_profiles.cpp",],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
        include_dirs=["cisTEM/src/"],
        extra_objects = [ "cisTEM/build/icpc/src/libcore.a"],
        extra_link_args = __WX_LIBS_BASE__.split(' ') 
        ),
]

def build(setup_kwargs: Dict[str, Any]) -> None:
    setup_kwargs.update(
        {
            "ext_modules": ext_modules,
            "cmdclass": dict(build_ext=custom_build_ext),
            "zip_safe": False,
        }
    )
