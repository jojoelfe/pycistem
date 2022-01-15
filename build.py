from typing import Any, Dict
# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup
from setuptools.command.build_ext import build_ext


# This code pulls come key compile info out of the config.log file
__version__ = "0.0.1"
__compiler__ = "g++"
__WX_FLAGS__ = ""
__CPP_FLAGS__ = ""
__WX_LIBS_BASE__ = ""

with open("config.log","r") as config_log:
    configs = config_log.readlines()

for line in configs:
    if line.startswith("#define CISTEM_VERSION_TEXT"):
        __version__ = line.split(" ")[-1][1:-2]
    if line.startswith("CXX="):
        __compiler__ = line[5:-2]
    if line.startswith("WX_CPPFLAGS_BASE="):
        __WX_FLAGS__ = line[18:-2]
    if line.startswith("CPPFLAGS="):
        __CPP_FLAGS__ = line[10:-2]
    if line.startswith("WX_LIBS_BASE="):
        __WX_LIBS_BASE__ = line[14:-2]
        

# Overwrite default compiler flags. It's kind of a hack to add the import flgs to the compiler string, but I think its the only way.
class custom_build_ext(build_ext):
    def build_extensions(self):
        # Override the compiler executables. Importantly, this
        # removes the "default" compiler flags that would
        # otherwise get passed on to to the compiler, i.e.,
        # distutils.sysconfig.get_var("CFLAGS").
        self.compiler.set_executable("compiler_so", __compiler__ + " " + __WX_FLAGS__ + " " + __CPP_FLAGS__ +" -fPIC -DMKL -static-intel -qopenmp-link=static")
        self.compiler.set_executable("compiler_cxx", __compiler__ + " " + __WX_FLAGS__ + " " + __CPP_FLAGS__)
        self.compiler.set_executable("linker_so", __compiler__  + " " + __CPP_FLAGS__ +" -shared -DMKL -static-intel -qopenmp-link=static")
        build_ext.build_extensions(self)

ext_modules = [
    Pybind11Extension("pycistem",
        ["src/main.cpp"],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
        extra_objects = [ "src/libcore.a"],
        extra_link_args = __WX_LIBS_BASE__.split(' ') + ['-fopenmp']
        ),
]

def build(setup_kwargs: Dict[str, Any]) -> None:
    setup_kwargs.update(
        {
            "ext_modules": ext_modules,
            "cmdclass": dict(build_ext=ExtensionBuilder),
            "zip_safe": False,
        }
    )

setup(
    name="pycistem",
    version=__version__,
    author="Johannes Elferich",
    author_email="jojotux123@hotmail.com",
    url="https://github.com/jojoelfe/cisTEM",
    description="Python binding for the cisTEM core library",
    long_description="",
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": custom_build_ext},
    zip_safe=False,
    python_requires=">=3.8",
)

