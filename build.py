from typing import Any, Dict
# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup
from setuptools.command.build_ext import build_ext


# This code pulls come key compile info out of the config.log file
__version__ = "0.0.1"
__compiler__ = "g++"
__WX_FLAGS__ = "-DEXPERIMENTAL -I/usr/local/lib/wx/include/gtk2-unicode-static-3.0 -I/usr/local/include/wx-3.0 -D_FILE_OFFSET_BITS=64 -D__WXGTK__"
__CPP_FLAGS__ = ""
__WX_LIBS_BASE__ = "-L/usr/local/lib -pthread /usr/local/lib/libwx_gtk2u_xrc-3.0.a /usr/local/lib/libwx_gtk2u_qa-3.0.a /usr/local/lib/libwx_baseu_net-3.0.a /usr/local/lib/libwx_gtk2u_html-3.0.a /usr/local/lib/libwx_gtk2u_adv-3.0.a /usr/local/lib/libwx_gtk2u_core-3.0.a /usr/local/lib/libwx_baseu_xml-3.0.a /usr/local/lib/libwx_baseu-3.0.a -lgtk-x11-2.0 -lgdk-x11-2.0 -lpangocairo-1.0 -latk-1.0 -lcairo -lgdk_pixbuf-2.0 -lgio-2.0 -lpangoft2-1.0 -lpango-1.0 -lgobject-2.0 -lharfbuzz -lfontconfig -lfreetype -lgthread-2.0 -pthread -lglib-2.0 -lX11 -lSM -lwxregexu-3.0 -lwxexpat-3.0 -lwxtiff-3.0 -lwxjpeg-3.0 -lwxpng-3.0 -lwxzlib-3.0 -ldl -lm"


# Overwrite default compiler flags. It's kind of a hack to add the import flgs to the compiler string, but I think its the only way.
class custom_build_ext(build_ext):
    def build_extensions(self):
        # Override the compiler executables. Importantly, this
        # removes the "default" compiler flags that would
        # otherwise get passed on to to the compiler, i.e.,
        # distutils.sysconfig.get_var("CFLAGS").
        self.compiler.set_executable("compiler_so", __compiler__ + " " + __WX_FLAGS__ + " " + __CPP_FLAGS__ )
        self.compiler.set_executable("compiler_cxx", __compiler__ + " " + __WX_FLAGS__ + " " + __CPP_FLAGS__)
        self.compiler.set_executable("linker_so", __compiler__  + " " + __CPP_FLAGS__ )
        build_ext.build_extensions(self)

ext_modules = [
    Pybind11Extension("pycistem",
        ["pycistem/core/core.cpp"],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
        include_dirs=["../cisTEM/src/"],
        extra_objects = [ "../libcore.a"],
        extra_link_args = __WX_LIBS_BASE__.split(' ') + ['-fopenmp']
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