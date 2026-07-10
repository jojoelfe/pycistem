import pytest

from pycistem.pycore import EulerSearch as PyEulerSearch
from pycistem.pycore import ParameterMap as PyParameterMap

core = pytest.importorskip("pycistem.core.core")
from pycistem.core import EulerSearch as CoreEulerSearch  # noqa: E402
from pycistem.core import ParameterMap as CoreParameterMap  # noqa: E402


def test_parameter_map_default():
    py_map = PyParameterMap()
    core_map = CoreParameterMap()
    for attr in ("phi", "theta", "psi", "x_shift", "y_shift"):
        assert getattr(py_map, attr) == getattr(core_map, attr)


def test_parameter_map_set_all_true():
    py_map = PyParameterMap()
    core_map = CoreParameterMap()
    py_map.SetAllTrue()
    core_map.SetAllTrue()
    for attr in ("phi", "theta", "psi", "x_shift", "y_shift"):
        assert getattr(py_map, attr) == getattr(core_map, attr) == True  # noqa: E712


@pytest.mark.parametrize(
    "symmetry,angular_step,in_plane_step",
    [
        ("C1", 3.0, 2.0),
        ("C1", 2.5, 1.5),
        ("C4", 5.0, 3.0),
        ("D2", 5.0, 3.0),
        ("O", 5.0, 3.0),
        ("I", 10.0, 5.0),
        ("T", 7.0, 4.0),
    ],
)
def test_init_grid_matches_compiled_core(symmetry, angular_step, in_plane_step):
    """Mirrors the exact call pattern in pycistem/programs/match_template.py::run."""

    def build(euler_search_cls, parameter_map_cls):
        search = euler_search_cls()
        parameter_map = parameter_map_cls()
        parameter_map.SetAllTrue()
        search.InitGrid(symmetry, angular_step, 0.0, 0.0, 360.0, in_plane_step, 0.0, 0.5, parameter_map, 10)
        if symmetry.startswith("C") and search.test_mirror:
            search.theta_max = 180.0
        search.CalculateGridSearchPositions(False)
        return search

    py_search = build(PyEulerSearch, PyParameterMap)
    core_search = build(CoreEulerSearch, CoreParameterMap)

    assert py_search.number_of_search_positions == core_search.number_of_search_positions
    assert py_search.test_mirror == core_search.test_mirror
    assert py_search.theta_max == pytest.approx(core_search.theta_max)
    # phi_max isn't bound by pycistem.core's pybind11 wrapper, so it can
    # only be checked indirectly via number_of_search_positions above.


def test_list_of_search_parameters_internally_consistent():
    # pycistem.core doesn't bind list_of_search_parameters (it's a raw
    # float** in C++), so this can only be checked against pycore itself:
    # the list length must match number_of_search_positions, and count-only
    # parity against the compiled core is covered by
    # test_init_grid_matches_compiled_core above.
    search = PyEulerSearch()
    parameter_map = PyParameterMap()
    parameter_map.SetAllTrue()
    search.InitGrid("C1", 3.0, 0.0, 0.0, 360.0, 2.0, 0.0, 0.5, parameter_map, 10)
    search.CalculateGridSearchPositions(False)

    assert len(search.list_of_search_parameters) == search.number_of_search_positions
    for phi, theta in search.list_of_search_parameters:
        assert 0.0 <= phi < search.phi_max + 1e-3
        assert 0.0 <= theta <= search.theta_max + 1e-3
