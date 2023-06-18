#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "core/core_headers.h"



#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

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

void init_run_profiles(py::module &m) {
     py::class_<RunCommand> runcommand(m, "RunCommand");
    runcommand
      .def(py::init<>())
      .def_readonly("command_to_run", &RunCommand::command_to_run)
      .def_readonly("number_of_copies", &RunCommand::number_of_copies)
      .def("SetCommand", &RunCommand::SetCommand);
    
    py::class_<RunProfile> runprofile(m, "RunProfile");
    runprofile
      .def(py::init<>())
      .def("AddCommand", (void (RunProfile::*)(::RunCommand))&RunProfile::AddCommand)
      .def("AddCommand", (void (RunProfile::*)(wxString,int,int,bool,int,int))&RunProfile::AddCommand)
      .def("RemoveCommand", &RunProfile::RemoveCommand)
      .def("RemoveAll", &RunProfile::RemoveAll)
      .def("ReturnTotalJobs", &RunProfile::ReturnTotalJobs)
      .def("SubstituteExecutableName", &RunProfile::SubstituteExecutableName)      
      .def("CheckNumberAndGrow", &RunProfile::CheckNumberAndGrow)
      .def_property("name",
        [](const RunProfile &m) { return py::str(m.name.ToStdString()); },
        [](RunProfile &m, wxString &name) { m.name = name; })
      .def_property("manager_command", 
        [](RunProfile &m) { return py::str(m.manager_command.ToStdString()); }, 
        [](RunProfile &m, wxString &s) { m.manager_command = s; })
      .def_property_readonly("run_commands", [](RunProfile const& e) { 
        std::vector<RunCommand*> v;
        for (int i = 0; i < e.number_of_run_commands; i++) {
          v.push_back(&e.run_commands[i]);
        }
        return v; });
    
    py::class_<RunProfileManager> runprofilemanager(m, "RunProfileManager");
    runprofilemanager
      .def("AddProfile", &RunProfileManager::AddProfile)
      .def("AddBlankProfile", &RunProfileManager::AddBlankProfile)
      .def("AddDefaultLocalProfile", &RunProfileManager::AddDefaultLocalProfile)
      .def("RemoveProfile", &RunProfileManager::RemoveProfile)
      .def("RemoveAllProfiles", &RunProfileManager::RemoveAllProfiles)
      .def("ReturnLastProfilePointer", &RunProfileManager::ReturnLastProfilePointer)
      .def("ReturnProfilePointer", &RunProfileManager::ReturnProfilePointer)
      .def("ReturnProfileName", &RunProfileManager::ReturnProfileName)
      .def("ReturnProfileID", &RunProfileManager::ReturnProfileID)
      .def("ReturnTotalJobs", &RunProfileManager::ReturnTotalJobs)
      .def("WriteRunProfilesToDisk", [](RunProfileManager &e, wxString const &filename, std::vector<int> const &profile_ids) {
          wxArrayInt profile_ids_array;
          for (auto &i : profile_ids) {
              profile_ids_array.Add(i);
          }
          e.WriteRunProfilesToDisk(filename, profile_ids_array);
      })
      .def("ImportRunProfilesFromDisk", &RunProfileManager::ImportRunProfilesFromDisk)
      .def_readonly("number_of_run_profiles", &RunProfileManager::number_of_run_profiles)
      .def_property_readonly("run_profiles", [](RunProfileManager const& e) { 
        std::vector<RunProfile*> v;
        for (int i = 0; i < e.number_of_run_profiles; i++) {
          v.push_back(&e.run_profiles[i]);
        }
        return v; })
      .def(py::init<>());   
}
