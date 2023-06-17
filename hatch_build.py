import os
import subprocess
from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup
from setuptools.command.build_ext import build_ext


# Overwrite default compiler flags. It's kind of a hack to add the import flgs to the compiler string, but I think its the only way.
class custom_build_ext(build_ext):
    def build_extensions(self):
        # Override the compiler executables. Importantly, this
        # removes the "default" compiler flags that would
        # otherwise get passed on to to the compiler, i.e.,
        # distutils.sysconfig.get_var("CFLAGS").
        __compiler__ = "g++"
        wx_config = "wx-config"

        wxflags = subprocess.run([wx_config, "--cxxflags"], stdout=subprocess.PIPE).stdout.decode("utf-8")
        # Strip the newline from the wxflags
        wxflags = wxflags.strip()

        wxlibflags = subprocess.run([wx_config, "--libs"], stdout=subprocess.PIPE).stdout.decode("utf-8")
        # Strip the newline from the wxlibflags
        wxlibflags = wxlibflags.strip()
        __WX_FLAGS__ = wxflags + "  -DwxUSE_GUI=0 -IcisTEM/build/gcc"
        __CPP_FLAGS__ = "-fPIC -O3 -D_FILE_OFFSET_BITS=64 -std=c++17 -D_LARGEFILE_SOURCE -DEXPERIMENTAL -fopenmp"
        self.compiler.set_executable("compiler_so", __compiler__ + " " + __WX_FLAGS__ + " " + __CPP_FLAGS__ )
        self.compiler.set_executable("compiler_cxx", __compiler__ + " -fPIC " + __WX_FLAGS__ + " " + __CPP_FLAGS__)
        self.compiler.set_executable("linker_so", __compiler__  + " " + __CPP_FLAGS__ +" -shared ")
        build_ext.build_extensions(self)



def build(setup_kwargs: Dict[str, Any]) -> None:
    # CHeck if /opt/WX/intel-static/bin/wx-config exists
    # If it does, use it to build the extension
    # If it doesn't, use the system wx-config
    wx_config = "wx-config"

    wxflags = subprocess.run([wx_config, "--cxxflags"], stdout=subprocess.PIPE).stdout.decode("utf-8")
    # Strip the newline from the wxflags
    wxflags = wxflags.strip()

    wxlibflags = subprocess.run([wx_config, "--libs"], stdout=subprocess.PIPE).stdout.decode("utf-8")
    # Strip the newline from the wxlibflags
    wxlibflags = wxlibflags.strip()

    # This code pulls come key compile info out of the config.log file
    __version__ = "0.1.4"
    wxflags + "-DwxUSE_GUI=0 -IcisTEM/build/gcc"
    __WX_LIBS_BASE__ = wxlibflags
    link_args = __WX_LIBS_BASE__.split()
    link_args.append("-lffi")
    #link_args.append("-Wl,-Bstatic")
    link_args.append("-l:libfftw3f.a")
    ext_modules = [
        Pybind11Extension("pycistem/core/core",
            ["pycistem/core/core.cpp",
            "pycistem/core/database.cpp",
            "pycistem/core/run_profiles.cpp",
            "pycistem/core/euler_search.cpp",
             ],
            # Example: passing in the version to the compiled code
            define_macros = [("VERSION_INFO", __version__)],
            include_dirs=["cisTEM/src/"],
            extra_objects = [ "cisTEM/build/gcc/src/libcore.a"],
            extra_link_args = link_args,
            ),
    ]
    setup_kwargs.update(
        {
            "ext_modules": ext_modules,
            "cmdclass": {"build_ext": custom_build_ext},
            "zip_safe": False
        }
    )

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if version == "editable":
            return
        t = {"packages": ["pycistem"]}
        build(t)
        d = setup(**t,script_args=["build_ext"])
        ext_path = d.get_command_obj("build_ext").get_ext_fullpath("pycistem.core.core")
        int_path = d.get_command_obj("build_ext").get_ext_filename("pycistem.core.core")
        build_data["pure_python"] = False
        build_data["infer_tag"] = True
        build_data["force_include"][ext_path] = int_path

if __name__ == "__main__":
    t = {"packages": ["pycistem"]}
    build(t)
    print(t)
    #sys.argv.append("build_ext")
    d = setup(**t,script_args=["build_ext"])
