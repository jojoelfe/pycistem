#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "core/core_headers.h"

namespace py = pybind11;

namespace PYBIND11_NAMESPACE { namespace detail {
    template <> struct type_caster<wxString> {
    public:
        /**
         * This macro establishes the name 'inty' in
         * function signatures and declares a local variable
         * 'value' of type inty
         */
        PYBIND11_TYPE_CASTER(wxString, const_name("wxString"));

        /**
         * Conversion part 1 (Python->C++): convert a PyObject into a inty
         * instance or return false upon failure. The second argument
         * indicates whether implicit conversions should be applied.
         */
        bool load(handle src, bool) {
            /* Extract PyObject from handle */
            PyObject *source = src.ptr();
            /* Try converting into a Python string */
            PyObject *tmp = PyObject_Str(source);
            if (!tmp)
                return false;
            /* Now try to convert into a wxString */
            value.Append(PyUnicode_AsUTF8(tmp));
            Py_DECREF(tmp);
            /* Ensure return code was OK (to avoid out-of-range errors etc) */
            return !PyErr_Occurred();
        }

        /**
         * Conversion part 2 (C++ -> Python): convert an inty instance into
         * a Python object. The second and third arguments are used to
         * indicate the return value policy and parent object (for
         * ``return_value_policy::reference_internal``) and are generally
         * ignored by implicit casters.
         */
        static handle cast(wxString src, return_value_policy /* policy */, handle /* parent */) {
            return py::str(src.ToStdString());
        }
    };
}} // namespace PYBIND11_NAMESPACE::detail

void init_euler(py::module &m) {
    py::class_<EulerSearch>(m, "EulerSearch")
        .def(py::init<>())
        .def("Init", &EulerSearch::Init)
        .def("InitGrid", &EulerSearch::InitGrid)
        .def("InitRandom", &EulerSearch::InitRandom)
        .def("Run", &EulerSearch::Run)
        .def_readwrite("theta_max", &EulerSearch::theta_max)
        .def_readwrite("number_of_search_positions", &EulerSearch::number_of_search_positions)
        .def_readwrite("test_mirror", &EulerSearch::test_mirror)
        .def("CalculateGridSearchPositions", &EulerSearch::CalculateGridSearchPositions)
        .def("CalculateRandomSearchPositions", &EulerSearch::CalculateRandomSearchPositions)
        .def("SetSymmetryLimits", &EulerSearch::SetSymmetryLimits);

    py::class_<ParameterMap>(m, "ParameterMap")
        .def(py::init<>())
        .def("SetAllTrue", &ParameterMap::SetAllTrue)
        .def_readwrite("phi", &ParameterMap::phi)
        .def_readwrite("theta", &ParameterMap::theta)
        .def_readwrite("psi", &ParameterMap::psi)
        .def_readwrite("x_shift", &ParameterMap::x_shift)
        .def_readwrite("y_shift", &ParameterMap::y_shift);
}
