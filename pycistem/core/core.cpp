#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "core/core_headers.h"



#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

void init_database(py::module &);
void init_run_profiles(py::module &);
void init_euler(py::module &);

PYBIND11_MODULE(core, m)
{
  m.doc() = R"pbdoc(
        CisTEM core library
        -----------------------

        .. currentmodule:: core

        .. autosummary::
           :toctree: _generate

           Image
    )pbdoc";

  // Global Functions

  m.def(
      "GetMRCDetails", [](const char *filename)
      {
        int x_size;
        int y_size;
        int number_of_images;
        auto __ret = GetMRCDetails(filename, x_size, y_size, number_of_images);
        return std::make_tuple(__ret, x_size, y_size, number_of_images);
      },
      "A function which details an mrc?");

  // Angles and Shifts

   py::class_<AnglesAndShifts> anglesandshifts(m, "AnglesAndShifts");
    anglesandshifts
      .def(py::init<>())
      .def(py::init<float,float,float,float,float>())
      .def("GenerateEulerMatrices", &AnglesAndShifts::GenerateEulerMatrices)
      .def("GenerateRotationMatrix2D", &AnglesAndShifts::GenerateRotationMatrix2D)
      .def("Init", &AnglesAndShifts::Init)
      .def("ReturnPhiAngle", &AnglesAndShifts::ReturnPhiAngle)
      .def("ReturnThetaAngle", &AnglesAndShifts::ReturnThetaAngle)
      .def("ReturnPsiAngle", &AnglesAndShifts::ReturnPsiAngle)
      .def("ReturnShiftX", &AnglesAndShifts::ReturnShiftX)
      .def("ReturnShiftY", &AnglesAndShifts::ReturnShiftY);

  // Asset classes

  py::class_<Asset> asset(m, "Asset");
  asset
      .def(py::init<>())
      .def("ReturnFullPathString", &Asset::ReturnFullPathString)
      .def("ReturnShortNameString", &Asset::ReturnShortNameString);

  py::class_<MovieAsset> movieasset(m, "MovieAsset");
  movieasset
      .def(py::init<>())
      .def(py::init<wxString>())
      .def("Update", &MovieAsset::Update)
      .def("CopyFrom", &MovieAsset::CopyFrom);

  py::class_<MovieMetadataAsset> moviemetadataasset(m, "MovieMetadataAsset");
  moviemetadataasset
      .def(py::init<>());

  py::class_<ImageAsset> imageasset(m, "ImageAsset");
  imageasset
      .def(py::init<>())
      .def(py::init<wxString>())
      .def("Update", &ImageAsset::Update)
      .def("CopyFrom", &ImageAsset::CopyFrom);

  py::class_<ParticlePositionAsset> particlepositionasset(m, "ParticlePositionAsset");
  particlepositionasset
      .def(py::init<>())
      .def(py::init<float, float>())
      .def("Reset", &ParticlePositionAsset::Reset)
      .def("CopyFrom", &ParticlePositionAsset::CopyFrom);

  py::class_<VolumeAsset> volumeasset(m, "VolumeAsset");
  volumeasset
      .def(py::init<>())
      .def(py::init<wxString>())
      .def("Update", &VolumeAsset::Update)
      .def("CopyFrom", &VolumeAsset::CopyFrom);

  py::class_<AtomicCoordinatesAsset> atomiccoordinatesasset(m, "AtomicCoordinatesAsset");
  atomiccoordinatesasset
      .def(py::init<>())
      .def(py::init<wxString>())
      .def("Update", &AtomicCoordinatesAsset::Update)
      .def("CopyFrom", &AtomicCoordinatesAsset::CopyFrom);

  py::class_<MovieAssetList> movieassetlist(m, "MovieAssetList");
  movieassetlist
      .def(py::init<>())
      .def("ReturnAssetPointer", &MovieAssetList::ReturnAssetPointer)
      .def("ReturnMovieAssetPointer", &MovieAssetList::ReturnMovieAssetPointer)
      .def("ReturnAssetID", &MovieAssetList::ReturnAssetID)
      .def("ReturnParentAssetID", &MovieAssetList::ReturnParentAssetID)
      .def("ReturnAssetName", &MovieAssetList::ReturnAssetName)
      .def("ReturnArrayPositionFromID", &MovieAssetList::ReturnArrayPositionFromID)
      .def("ReturnArrayPositionFromParentID", &MovieAssetList::ReturnArrayPositionFromParentID)
      .def("ReturnAssetFullFilename", &MovieAssetList::ReturnAssetFullFilename)
      .def("AddAsset", &MovieAssetList::AddAsset)
      .def("RemoveAsset", &MovieAssetList::RemoveAsset)
      .def("RemoveAll", &MovieAssetList::RemoveAll)
      .def("FindFile", &MovieAssetList::FindFile)
      .def("CheckMemory", &MovieAssetList::CheckMemory);

  py::class_<ImageAssetList> imageassetlist(m, "ImageAssetList");
  imageassetlist
      .def(py::init<>())
      .def("ReturnAssetPointer", &ImageAssetList::ReturnAssetPointer)
      .def("ReturnImageAssetPointer", &ImageAssetList::ReturnImageAssetPointer)
      .def("ReturnAssetID", &ImageAssetList::ReturnAssetID)
      .def("ReturnParentAssetID", &ImageAssetList::ReturnParentAssetID)
      .def("ReturnAssetName", &ImageAssetList::ReturnAssetName)
      .def("ReturnArrayPositionFromID", &ImageAssetList::ReturnArrayPositionFromID)
      .def("ReturnArrayPositionFromParentID", &ImageAssetList::ReturnArrayPositionFromParentID)
      .def("ReturnAssetFullFilename", &ImageAssetList::ReturnAssetFullFilename)
      .def("AddAsset", &ImageAssetList::AddAsset)
      .def("RemoveAsset", &ImageAssetList::RemoveAsset)
      .def("RemoveAll", &ImageAssetList::RemoveAll)
      .def("FindFile", &ImageAssetList::FindFile)
      .def("CheckMemory", &ImageAssetList::CheckMemory);

  py::class_<ParticlePositionAssetList> particlepositionassetlist(m, "ParticlePositionAssetList");
  particlepositionassetlist
      .def(py::init<>())
      .def("ReturnAssetPointer", &ParticlePositionAssetList::ReturnAssetPointer)
      .def("ReturnParticlePositionAssetPointer", &ParticlePositionAssetList::ReturnParticlePositionAssetPointer)
      .def("ReturnAssetID", &ParticlePositionAssetList::ReturnAssetID)
      .def("ReturnParentAssetID", &ParticlePositionAssetList::ReturnParentAssetID)
      .def("ReturnAssetName", &ParticlePositionAssetList::ReturnAssetName)
      .def("ReturnAssetFullFilename", &ParticlePositionAssetList::ReturnAssetFullFilename)
      .def("ReturnArrayPositionFromID", &ParticlePositionAssetList::ReturnArrayPositionFromID)
      .def("ReturnArrayPositionFromParentID", &ParticlePositionAssetList::ReturnArrayPositionFromParentID)
      .def("AddAsset", &ParticlePositionAssetList::AddAsset)
      .def("RemoveAsset", &ParticlePositionAssetList::RemoveAsset)
      .def("RemoveAssetsWithGivenParentImageID", &ParticlePositionAssetList::RemoveAssetsWithGivenParentImageID)
      .def("RemoveAll", &ParticlePositionAssetList::RemoveAll)
      .def("CheckMemory", &ParticlePositionAssetList::CheckMemory);

  py::class_<VolumeAssetList> volumeassetlist(m, "VolumeAssetList");
  volumeassetlist
      .def(py::init<>())
      .def("ReturnAssetPointer", &VolumeAssetList::ReturnAssetPointer)
      .def("ReturnVolumeAssetPointer", &VolumeAssetList::ReturnVolumeAssetPointer)
      .def("ReturnAssetID", &VolumeAssetList::ReturnAssetID)
      .def("ReturnParentAssetID", &VolumeAssetList::ReturnParentAssetID)
      .def("ReturnAssetName", &VolumeAssetList::ReturnAssetName)
      .def("ReturnArrayPositionFromID", &VolumeAssetList::ReturnArrayPositionFromID)
      .def("ReturnArrayPositionFromParentID", &VolumeAssetList::ReturnArrayPositionFromParentID)
      .def("ReturnAssetFullFilename", &VolumeAssetList::ReturnAssetFullFilename)
      .def("AddAsset", &VolumeAssetList::AddAsset)
      .def("RemoveAsset", &VolumeAssetList::RemoveAsset)
      .def("RemoveAll", &VolumeAssetList::RemoveAll)
      .def("FindFile", &VolumeAssetList::FindFile)
      .def("CheckMemory", &VolumeAssetList::CheckMemory);

  py::class_<AtomicCoordinatesAssetList> atomiccoordinatesassetlist(m, "AtomicCoordinatesAssetList");
  atomiccoordinatesassetlist
      .def(py::init<>())
      .def("ReturnAssetPointer", &AtomicCoordinatesAssetList::ReturnAssetPointer)
      .def("ReturnAtomicCoordinatesAssetPointer", &AtomicCoordinatesAssetList::ReturnAtomicCoordinatesAssetPointer)
      .def("ReturnAssetID", &AtomicCoordinatesAssetList::ReturnAssetID)
      .def("ReturnParentAssetID", &AtomicCoordinatesAssetList::ReturnParentAssetID)
      .def("ReturnAssetName", &AtomicCoordinatesAssetList::ReturnAssetName)
      .def("ReturnArrayPositionFromID", &AtomicCoordinatesAssetList::ReturnArrayPositionFromID)
      .def("ReturnArrayPositionFromParentID", &AtomicCoordinatesAssetList::ReturnArrayPositionFromParentID)
      .def("ReturnAssetFullFilename", &AtomicCoordinatesAssetList::ReturnAssetFullFilename)
      .def("AddAsset", &AtomicCoordinatesAssetList::AddAsset)
      .def("RemoveAsset", &AtomicCoordinatesAssetList::RemoveAsset)
      .def("RemoveAll", &AtomicCoordinatesAssetList::RemoveAll)
      .def("FindFile", &AtomicCoordinatesAssetList::FindFile)
      .def("CheckMemory", &AtomicCoordinatesAssetList::CheckMemory);

  // CTF

  py::class_<CTF> ctf(m, "CTF");
    ctf
      .def(py::init([](		float wanted_acceleration_voltage_in_kV, // keV
				float wanted_spherical_aberration_in_mm, // mm
				float wanted_amplitude_contrast,
				float wanted_defocus_1_in_angstroms, // A
				float wanted_defocus_2_in_angstroms, //A
				float wanted_astigmatism_azimuth_in_degrees, // degrees
				float wanted_lowest_frequency_for_fitting_in_reciprocal_angstroms, // 1/A
				float wanted_highest_frequency_for_fitting_in_reciprocal_angstroms, // 1/A
				float wanted_astigmatism_tolerance_in_angstroms, // A. Set to negative to indicate no restraint on astigmatism.
				float pixel_size_in_angstroms, // A
				float wanted_additional_phase_shift_in_radians, //rad
				float wanted_beam_tilt_x_in_radians, // rad
				float wanted_beam_tilt_y_in_radians, // rad
				float wanted_particle_shift_x_in_angstroms, // A
				float wanted_particle_shift_y_in_angstroms) // A
			  {
          CTF ctf = CTF();
          if (wanted_highest_frequency_for_fitting_in_reciprocal_angstroms <= 0.0f) {
            wanted_highest_frequency_for_fitting_in_reciprocal_angstroms = 1.0/(2.0*pixel_size_in_angstroms);
          }
          ctf.Init(wanted_acceleration_voltage_in_kV,
                   wanted_spherical_aberration_in_mm,
                   wanted_amplitude_contrast,
                   wanted_defocus_1_in_angstroms,
                   wanted_defocus_2_in_angstroms,
                   wanted_astigmatism_azimuth_in_degrees,
                   wanted_lowest_frequency_for_fitting_in_reciprocal_angstroms,
                   wanted_highest_frequency_for_fitting_in_reciprocal_angstroms,
                   wanted_astigmatism_tolerance_in_angstroms,
                   pixel_size_in_angstroms,
                   wanted_additional_phase_shift_in_radians,
                   wanted_beam_tilt_x_in_radians,
                   wanted_beam_tilt_y_in_radians,
                   wanted_particle_shift_x_in_angstroms,
                   wanted_particle_shift_y_in_angstroms);
          return ctf;
        }), py::arg("kV") = 300.0,
            py::arg("cs") = 2.7,
            py::arg("ac") = 0.07,
            py::arg("defocus1") = 0.0,
            py::arg("defocus2") = 0.0,
            py::arg("astig_angle") = 0.0,
            py::arg("low_freq") = 0.0,
            py::arg("high_freq") = 0.0,
            py::arg("astig_tol") = -10.0,
            py::arg("pixel_size") = 1.0,
            py::arg("phase_shift") = 0.0,
            py::arg("beam_tilt_x") = 0.0,
            py::arg("beam_tilt_y") = 0.0,
            py::arg("particle_shift_x") = 0.0,
            py::arg("particle_shift_y") = 0.0
            )
      //.def_readonly("thickness", &CTF::thickness)
      //.def(py::init<float,float,float,float,float,float,float,float,float,float,float,float,float,float,float>())
      //.def(py::init<float,float,float,float,float,float,float,float,float,float,float,float>())
      //.def("Init", (void (CTF::*)(float,float,float,float,float,float,float,float,float,float,float,float,float,float,float,float))&CTF::Init)
      //.def("Init", (void (CTF::*)(float,float,float,float,float,float,float,float,float))&CTF::Init)
      .def("SetDefocus", &CTF::SetDefocus)
      .def("SetAdditionalPhaseShift", &CTF::SetAdditionalPhaseShift)
      .def("SetEnvelope", &CTF::SetEnvelope)
      .def("SetBeamTilt", &CTF::SetBeamTilt)
      .def("SetHighestFrequencyForFitting", &CTF::SetHighestFrequencyForFitting)
      .def("SetLowResolutionContrast", &CTF::SetLowResolutionContrast)
      .def("SetHighestFrequencyWithGoodFit", &CTF::SetHighestFrequencyWithGoodFit)
      .def("EvaluateComplex", &CTF::EvaluateComplex)
      .def("Evaluate", &CTF::Evaluate)
      .def("SetSampleThickness", &CTF::SetSampleThickness)
      .def("EvaluatePowerspectrumWithThickness", &CTF::EvaluatePowerspectrumWithThickness)
      .def("IntegratedDefocusModulation", &CTF::IntegratedDefocusModulation)
      .def("EvaluateWithEnvelope", &CTF::EvaluateWithEnvelope)
      .def("PhaseShiftGivenSquaredSpatialFrequencyAndAzimuth", &CTF::PhaseShiftGivenSquaredSpatialFrequencyAndAzimuth)
      .def("EvaluateBeamTiltPhaseShift", &CTF::EvaluateBeamTiltPhaseShift)
      .def("PhaseShiftGivenBeamTiltAndShift", &CTF::PhaseShiftGivenBeamTiltAndShift)
      .def("PhaseShiftGivenSquaredSpatialFrequencyAndDefocus", &CTF::PhaseShiftGivenSquaredSpatialFrequencyAndDefocus)
      .def("DefocusGivenAzimuth", &CTF::DefocusGivenAzimuth)
      .def("BeamTiltGivenAzimuth", &CTF::BeamTiltGivenAzimuth)
      .def("ParticleShiftGivenAzimuth", &CTF::ParticleShiftGivenAzimuth)
      .def("WavelengthGivenAccelerationVoltage", &CTF::WavelengthGivenAccelerationVoltage)
      .def("GetLowestFrequencyForFitting", &CTF::GetLowestFrequencyForFitting)
      .def("GetHighestFrequencyForFitting", &CTF::GetHighestFrequencyForFitting)
      .def("GetHighestFrequencyWithGoodFit", &CTF::GetHighestFrequencyWithGoodFit)
      .def("GetAstigmatismTolerance", &CTF::GetAstigmatismTolerance)
      .def("GetAstigmatism", &CTF::GetAstigmatism)
      .def("IsAlmostEqualTo", &CTF::IsAlmostEqualTo)
      .def("BeamTiltIsAlmostEqualTo", &CTF::BeamTiltIsAlmostEqualTo)
      .def("EnforceConvention", &CTF::EnforceConvention)
      //.def("PrintInfo", &CTF::PrintInfo)
      .def("CopyFrom", &CTF::CopyFrom)
      .def("ChangePixelSize", &CTF::ChangePixelSize)
      .def("GetDefocus1", &CTF::GetDefocus1)
      .def("GetDefocus2", &CTF::GetDefocus2)
      .def("GetBeamTiltX", &CTF::GetBeamTiltX)
      .def("GetBeamTiltY", &CTF::GetBeamTiltY)
      .def("GetSphericalAberration", &CTF::GetSphericalAberration)
      .def("GetAmplitudeContrast", &CTF::GetAmplitudeContrast)
      .def("GetAstigmatismAzimuth", &CTF::GetAstigmatismAzimuth)
      .def("GetAdditionalPhaseShift", &CTF::GetAdditionalPhaseShift)
      .def("GetWavelength", &CTF::GetWavelength)
      .def("ReturnNumberOfExtremaBeforeSquaredSpatialFrequency", &CTF::ReturnNumberOfExtremaBeforeSquaredSpatialFrequency)
      .def("ReturnSquaredSpatialFrequencyGivenPhaseShiftAndAzimuth", &CTF::ReturnSquaredSpatialFrequencyGivenPhaseShiftAndAzimuth)
      .def("ReturnSquaredSpatialFrequencyOfAZero", &CTF::ReturnSquaredSpatialFrequencyOfAZero)
      .def("ReturnSquaredSpatialFrequencyOfPhaseShiftExtremumGivenAzimuth", &CTF::ReturnSquaredSpatialFrequencyOfPhaseShiftExtremumGivenAzimuth)
      .def("ReturnSquaredSpatialFrequencyOfPhaseShiftExtremumGivenDefocus", &CTF::ReturnSquaredSpatialFrequencyOfPhaseShiftExtremumGivenDefocus)
      .def("ReturnPhaseAberrationMaximum", &CTF::ReturnPhaseAberrationMaximum)
      .def("ReturnPhaseAberrationMaximumGivenDefocus", &CTF::ReturnPhaseAberrationMaximumGivenDefocus);
    

  // Curve

  py::class_<Curve> curve(m, "Curve");
    curve
      .def(py::init<>())
      .def(py::init<::Curve>())
      /*.def("operator=", [](Curve &__inst) {
        ::Curve other_curve;
        auto __ret = __inst.operator=(other_curve);
        return std::make_tuple(__ret, other_curve);
      })*/
      .def_readonly("number_of_points", &Curve::number_of_points)
      .def_property_readonly("data_x", [](Curve &__inst) {
            //return 5;
            py::capsule buffer_handle([](){});
            return py::array_t<float>(
              {__inst.number_of_points},
              {4},
              __inst.data_x,
              buffer_handle
              );
         }
      )
      .def_property_readonly("data_y", [](Curve &__inst) {
            //return 5;
            py::capsule buffer_handle([](){});
            return py::array_t<float>(
              {__inst.number_of_points},
              {4},
              __inst.data_y,
              buffer_handle
              );
         }
      )
      //.def("operator=", (Curve (Curve::*)(::Curve))&Curve::operator=)
      .def("ResampleCurve", &Curve::ResampleCurve)
      .def("ReturnLinearInterpolationFromI", &Curve::ReturnLinearInterpolationFromI)
      .def("ReturnLinearInterpolationFromX", &Curve::ReturnLinearInterpolationFromX)
      .def("ReturnValueAtXUsingLinearInterpolation", &Curve::ReturnValueAtXUsingLinearInterpolation)
      .def("AddValueAtXUsingLinearInterpolation", &Curve::AddValueAtXUsingLinearInterpolation)
      .def("AddValueAtXUsingNearestNeighborInterpolation", &Curve::AddValueAtXUsingNearestNeighborInterpolation)
      .def("ReturnIndexOfNearestPreviousBin", &Curve::ReturnIndexOfNearestPreviousBin)
      .def("PrintToStandardOut", &Curve::PrintToStandardOut)
      .def("WriteToFile", (void (Curve::*)(wxString))&Curve::WriteToFile)
      .def("WriteToFile", (void (Curve::*)(wxString,wxString))&Curve::WriteToFile)
      .def("CopyFrom", &Curve::CopyFrom)
      .def("CopyDataFromArrays", &Curve::CopyDataFromArrays)
      .def("CopyYValuesFromArray", &Curve::CopyYValuesFromArray)
      .def("ClearData", &Curve::ClearData)
      .def("MultiplyByConstant", &Curve::MultiplyByConstant)
      .def("MultiplyXByConstant", &Curve::MultiplyXByConstant)
      .def("AddPoint", &Curve::AddPoint)
      .def("FitPolynomialToData", &Curve::FitPolynomialToData)
      .def("FitGaussianToData", &Curve::FitGaussianToData)
      .def("FitSavitzkyGolayToData", &Curve::FitSavitzkyGolayToData)
      .def("ReturnSavitzkyGolayInterpolationFromX", &Curve::ReturnSavitzkyGolayInterpolationFromX)
      .def("ReturnIndexOfNearestPointFromX", &Curve::ReturnIndexOfNearestPointFromX)
      .def("DeleteSavitzkyGolayCoefficients", &Curve::DeleteSavitzkyGolayCoefficients)
      .def("AllocateSavitzkyGolayCoefficients", &Curve::AllocateSavitzkyGolayCoefficients)
      .def("CheckMemory", &Curve::CheckMemory)
      .def("AllocateMemory", &Curve::AllocateMemory)
      .def("AddWith", &Curve::AddWith)
      /*.def("DivideBy", (void (Curve::*)(::Curve))&Curve::DivideBy)
      .def("DivideBy", [](Curve &__inst) {
        ::Curve other_curve;
        __inst.DivideBy(other_curve);
        return other_curve;
      })*/
      .def("SetupXAxis", &Curve::SetupXAxis)
      .def("ReturnMaximumValue", &Curve::ReturnMaximumValue)
      .def("ReturnMode", &Curve::ReturnMode)
      .def("ComputeMaximumValueAndMode", [](Curve &__inst) {
        float maximum_value; float mode;
        __inst.ComputeMaximumValueAndMode(maximum_value, mode);
        return std::make_tuple(maximum_value, mode);
      })
      .def("ReturnFullWidthAtGivenValue", [](Curve &__inst) {
        float wanted_value;
        auto __ret = __inst.ReturnFullWidthAtGivenValue(wanted_value);
        return std::make_tuple(__ret, wanted_value);
      })
      .def("NormalizeMaximumValue", &Curve::NormalizeMaximumValue)
      .def("Logarithm", &Curve::Logarithm)
      .def("ZeroYData", &Curve::ZeroYData)
      .def("ApplyCTF", &Curve::ApplyCTF)
      .def("SquareRoot", &Curve::SquareRoot)
      .def("Reciprocal", &Curve::Reciprocal)
      .def("MultiplyBy", [](Curve &__inst) {
        ::Curve other_curve;
        __inst.MultiplyBy(other_curve);
        return other_curve;
      })
      .def("ZeroAfterIndex", &Curve::ZeroAfterIndex)
      .def("FlattenBeforeIndex", &Curve::FlattenBeforeIndex)
      .def("ReturnAverageValue", &Curve::ReturnAverageValue)
      .def("ApplyCosineMask", &Curve::ApplyCosineMask)
      .def("ApplyGaussianLowPassFilter", &Curve::ApplyGaussianLowPassFilter)
      .def("GetXMinMax", [](Curve &__inst) {
        float min_value; float max_value;
        __inst.GetXMinMax(min_value, max_value);
        return std::make_tuple(min_value, max_value);
      })
      .def("GetYMinMax", [](Curve &__inst) {
        float min_value; float max_value;
        __inst.GetYMinMax(min_value, max_value);
        return std::make_tuple(min_value, max_value);
      })
      .def("SetYToConstant", &Curve::SetYToConstant);
    

  // Database
  init_database(m); 
  //Run Profiles
  init_run_profiles(m);
  // Euler Search
  init_euler(m);
  // ElectronDose
   py::class_<ElectronDose> electrondose(m, "ElectronDose");
    electrondose
      .def(py::init<>())
      .def(py::init<float,float>())
      .def("Init", &ElectronDose::Init)
      .def("ReturnCriticalDose", &ElectronDose::ReturnCriticalDose)
      .def("ReturnDoseFilter", &ElectronDose::ReturnDoseFilter)
      .def("ReturnCummulativeDoseFilter", &ElectronDose::ReturnCummulativeDoseFilter)
      .def("CalculateCummulativeDoseFilterAs1DArray", [](ElectronDose &__inst, Image &ref_image, float dose_start, float dose_end)
        {
          float dose_filter[ref_image.real_memory_allocated / 2];

			    ZeroFloatArray(dose_filter, ref_image.real_memory_allocated / 2);
          __inst.CalculateCummulativeDoseFilterAs1DArray(&ref_image, dose_filter, dose_start, dose_end);
          py::capsule buffer_handle([](){});
            return py::array_t<float>(
              {ref_image.real_memory_allocated / 2},
              {4},
              dose_filter,
              buffer_handle
              ); 
        })
      .def("CalculateDoseFilterAs1DArray",  [](ElectronDose &__inst, Image &ref_image, float dose_start, float dose_end)
        {
          float dose_filter[ref_image.real_memory_allocated / 2];

			    ZeroFloatArray(dose_filter, ref_image.real_memory_allocated / 2);
          __inst.CalculateCummulativeDoseFilterAs1DArray(&ref_image, dose_filter, dose_start, dose_end);
          py::capsule buffer_handle([](){});
            return py::array_t<float>(
              {ref_image.real_memory_allocated / 2},
              {4},
              dose_filter,
              buffer_handle
              ); 
        });

  // Project

  py::class_<Project> project(m, "Project");
  project
      .def(py::init<>())
      .def_readonly("database", &Project::database)
      .def("Close", &Project::Close)
      .def("CreateNewProject", [](Project &__inst, std::string database_file, std::string project_directory, std::string project_name)
           {
             wxString wanted_database_file = database_file;
             return __inst.CreateNewProject(wanted_database_file, project_directory, project_name);
           })
      .def("OpenProjectFromFile", [](Project &__inst, std::string database_file)
           {
             wxString wanted_database_file = database_file;
             return __inst.OpenProjectFromFile(wanted_database_file);
           })
      .def("ReadMasterSettings", &Project::ReadMasterSettings)
      .def("WriteProjectStatisticsToDatabase", &Project::WriteProjectStatisticsToDatabase);

  // Image

  py::class_<Image> image(m, "Image");
  image
      .def(py::init<>())
      .def(py::init<::Image>())
      .def_readonly("logical_x_dimension", &Image::logical_x_dimension)
      .def_readonly("logical_y_dimension", &Image::logical_y_dimension)
      .def_readonly("logical_z_dimension", &Image::logical_z_dimension)
      .def_readonly("physical_upper_bound_complex_x", &Image::physical_upper_bound_complex_x)
      .def_readonly("physical_upper_bound_complex_y", &Image::physical_upper_bound_complex_y)
      .def_readonly("physical_upper_bound_complex_z", &Image::physical_upper_bound_complex_z)
      .def_readonly("is_in_real_space", &Image::is_in_real_space)
      .def_property_readonly("real_values", [](Image &__inst) {
            //return 5;
            py::capsule buffer_handle([](){});
            if (__inst.logical_z_dimension == 1) {
            return py::array_t<float>(
              {__inst.logical_y_dimension, __inst.logical_x_dimension},
              {sizeof(float) * (__inst.logical_x_dimension + __inst.padding_jump_value), /* Strides (in bytes) for each index */
                         sizeof(float)},
              __inst.real_values,
              buffer_handle
              );
            } else {
              return py::array_t<float>(
              {__inst.logical_z_dimension, __inst.logical_y_dimension, __inst.logical_x_dimension},
              {sizeof(float) * (__inst.logical_x_dimension + __inst.padding_jump_value) * (__inst.logical_y_dimension) ,sizeof(float) * (__inst.logical_x_dimension + __inst.padding_jump_value), sizeof(float)
                         },
              __inst.real_values,
              buffer_handle
              );
            }
         }
      )
      .def_property_readonly("complex_values", [](Image &__inst) {
            //return 5;
            py::capsule buffer_handle([](){});
            return py::array_t<std::complex<float>>(
              {__inst.physical_upper_bound_complex_y, __inst.physical_upper_bound_complex_x},
              {sizeof(std::complex<float>) * __inst.physical_upper_bound_complex_x , /* Strides (in bytes) for each index */
                         sizeof(std::complex<float>)},
              __inst.complex_values,
              buffer_handle
              );
         }
      )
      /* .def("operator=", [](Image &__inst) {
        ::Image t;
        auto __ret = __inst.operator=(t);
        return std::make_tuple(__ret, t);
      })
      .def("operator=", (Image (Image::*)(::Image))&Image::operator=) */
      .def("SetupInitialValues", &Image::SetupInitialValues)
      .def("Allocate", (void (Image::*)(int, int, int, bool, bool)) & Image::Allocate)
      .def("Allocate", (void (Image::*)(int, int, bool)) & Image::Allocate)
      //.def("Allocate", (void (Image::*)(::Image))&Image::Allocate)
      .def("AllocateAsPointingToSliceIn3D", &Image::AllocateAsPointingToSliceIn3D)
      .def("Deallocate", &Image::Deallocate)
      .def("ReturnSmallestLogicalDimension", &Image::ReturnSmallestLogicalDimension)
      .def("ReturnLargestLogicalDimension", &Image::ReturnLargestLogicalDimension)
      .def("SampleFFT", [](Image &__inst, int sample_rate)
           {
             ::Image sampled_image;
             __inst.SampleFFT(sampled_image, sample_rate);
             return sampled_image;
           })
      .def("ReturnSumOfSquares", &Image::ReturnSumOfSquares)
      .def("ReturnSumOfRealValues", &Image::ReturnSumOfRealValues)
      .def("ReturnSigmaNoise", (float (Image::*)()) & Image::ReturnSigmaNoise)
      .def("ReturnSigmaNoise", [](Image &__inst, float mask_radius)
           {
             ::Image matching_projection;
             auto __ret = __inst.ReturnSigmaNoise(matching_projection, mask_radius);
             return std::make_tuple(__ret, matching_projection);
           })
      .def("ReturnImageScale", [](Image &__inst, float mask_radius)
           {
             ::Image matching_projection;
             auto __ret = __inst.ReturnImageScale(matching_projection, mask_radius);
             return std::make_tuple(__ret, matching_projection);
           })
      .def("ReturnCorrelationCoefficientUnnormalized", [](Image &__inst, float wanted_mask_radius)
           {
             ::Image other_image;
             auto __ret = __inst.ReturnCorrelationCoefficientUnnormalized(other_image, wanted_mask_radius);
             return std::make_tuple(__ret, other_image);
           })
      .def("ReturnBeamTiltSignificanceScore", &Image::ReturnBeamTiltSignificanceScore)
      .def("ReturnPixelWiseProduct", [](Image &__inst)
           {
             ::Image other_image;
             auto __ret = __inst.ReturnPixelWiseProduct(other_image);
             return std::make_tuple(__ret, other_image);
           })
      .def("GetWeightedCorrelationWithImage", [](Image &__inst, int *bins, float signed_CC_limit)
           {
             ::Image projection_image;
             auto __ret = __inst.GetWeightedCorrelationWithImage(projection_image, bins, signed_CC_limit);
             return std::make_tuple(__ret, projection_image);
           })
      .def("PhaseFlipPixelWise", [](Image &__inst)
           {
             ::Image other_image;
             __inst.PhaseFlipPixelWise(other_image);
             return other_image;
           })
      .def("MultiplyPixelWiseReal", [](Image &__inst, bool absolute)
           {
             ::Image other_image;
             __inst.MultiplyPixelWiseReal(other_image, absolute);
             return other_image;
           })
      .def("MultiplyPixelWise", [](Image &__inst)
           {
             ::Image other_image;
             __inst.MultiplyPixelWise(other_image);
             return other_image;
           })
      .def("ConjugateMultiplyPixelWise", [](Image &__inst)
           {
             ::Image other_image;
             __inst.ConjugateMultiplyPixelWise(other_image);
             return other_image;
           })
      .def("ComputeFSCVectorized", &Image::ComputeFSCVectorized)
      .def("ComputeFSC", &Image::ComputeFSC)
      .def("DividePixelWise", [](Image &__inst)
           {
             ::Image other_image;
             __inst.DividePixelWise(other_image);
             return other_image;
           })
      .def("AddGaussianNoise", &Image::AddGaussianNoise)
      .def("ZeroFloat", &Image::ZeroFloat)
      .def("ZeroFloatAndNormalize", &Image::ZeroFloatAndNormalize)
      .def("Normalize", &Image::Normalize)
      //.def("NormalizeSumOfSquares", &Image::NormalizeSumOfSquares)
      .def("ZeroFloatOutside", &Image::ZeroFloatOutside)
      .def("ReplaceOutliersWithMean", &Image::ReplaceOutliersWithMean)
      .def("ReturnVarianceOfRealValues", &Image::ReturnVarianceOfRealValues)
      .def("ReturnDistributionOfRealValues", &Image::ReturnDistributionOfRealValues)
      .def("UpdateDistributionOfRealValues", &Image::UpdateDistributionOfRealValues)
      .def("ApplySqrtNFilter", &Image::ApplySqrtNFilter)
      .def("Whiten", &Image::Whiten)
      .def("OptimalFilterBySNRImage", [](Image &__inst, int include_reference_weighting)
           {
             ::Image SNR_image;
             __inst.OptimalFilterBySNRImage(SNR_image, include_reference_weighting);
             return SNR_image;
           })
      .def("MultiplyByWeightsCurve", [](Image &__inst, float scale_factor)
           {
             Curve weights;
             __inst.MultiplyByWeightsCurve(weights, scale_factor);
             return weights;
           })
      .def("WeightBySSNR", [](Image &__inst, float molecular_mass_kDa, float pixel_size, bool weight_particle_image, bool weight_projection_image)
           {
             ::Image ctf_image;
             Curve SSNR;
             ::Image projection_image;
             __inst.WeightBySSNR(ctf_image, molecular_mass_kDa, pixel_size, SSNR, projection_image, weight_particle_image, weight_projection_image);
             return std::make_tuple(ctf_image, SSNR, projection_image);
           })
      .def("OptimalFilterSSNR", [](Image &__inst)
           {
             Curve SSNR;
             __inst.OptimalFilterSSNR(SSNR);
             return SSNR;
           })
      .def("OptimalFilterFSC", [](Image &__inst)
           {
             Curve FSC;
             __inst.OptimalFilterFSC(FSC);
             return FSC;
           })
      .def("OptimalFilterWarp", &Image::OptimalFilterWarp)
      .def("CorrectSinc", &Image::CorrectSinc)
      .def("MirrorXFourier2D", [](Image &__inst)
           {
             ::Image mirrored_image;
             __inst.MirrorXFourier2D(mirrored_image);
             return mirrored_image;
           })
      .def("MirrorYFourier2D", [](Image &__inst)
           {
             ::Image mirrored_image;
             __inst.MirrorYFourier2D(mirrored_image);
             return mirrored_image;
           })
      .def("RotateQuadrants", [](Image &__inst, int quad_i)
           {
             ::Image rotated_image;
             __inst.RotateQuadrants(rotated_image, quad_i);
             return rotated_image;
           })
      .def("Rotate3DByRotationMatrixAndOrApplySymmetry", [](Image &__inst, float wanted_max_radius_in_pixels, wxString wanted_symmetry)
           {
             RotationMatrix wanted_matrix;
             __inst.Rotate3DByRotationMatrixAndOrApplySymmetry(wanted_matrix, wanted_max_radius_in_pixels, wanted_symmetry);
             return wanted_matrix;
           })
      .def("Rotate3DByRotationMatrixAndOrApplySymmetryThenShift", [](Image &__inst, float wanted_x_shift, float wanted_y_shift, float wanted_z_shift, float wanted_max_radius_in_pixels, wxString wanted_symmetry)
           {
             RotationMatrix wanted_matrix;
             __inst.Rotate3DByRotationMatrixAndOrApplySymmetryThenShift(wanted_matrix, wanted_x_shift, wanted_y_shift, wanted_z_shift, wanted_max_radius_in_pixels, wanted_symmetry);
             return wanted_matrix;
           })
      .def("Rotate3DThenShiftThenApplySymmetry", [](Image &__inst, float wanted_x_shift, float wanted_y_shift, float wanted_z_shift, float wanted_max_radius_in_pixels, wxString wanted_symmetry)
           {
             RotationMatrix wanted_matrix;
             __inst.Rotate3DThenShiftThenApplySymmetry(wanted_matrix, wanted_x_shift, wanted_y_shift, wanted_z_shift, wanted_max_radius_in_pixels, wanted_symmetry);
             return wanted_matrix;
           })
      .def("GenerateReferenceProjections", [](Image &__inst, Image *projections, float resolution)
           {
             EulerSearch parameters;
             __inst.GenerateReferenceProjections(projections, parameters, resolution);
             return parameters;
           })
      /* .def("RotateFourier2DGenerateIndex", [](Image &__inst, float psi_max, float psi_step, float psi_start, bool invert_angle) {
        Kernel2D kernel_index;
        __inst.RotateFourier2DGenerateIndex(kernel_index, psi_max, psi_step, psi_start, invert_angle);
        return kernel_index;
      })
      .def("RotateFourier2DDeleteIndex", [](Image &__inst, float psi_max, float psi_step) {
        Kernel2D kernel_index;
        __inst.RotateFourier2DDeleteIndex(kernel_index, psi_max, psi_step);
        return kernel_index;
      }) */
      .def("RotateFourier2DFromIndex", [](Image &__inst, Kernel2D *kernel_index)
           {
             ::Image rotated_image;
             __inst.RotateFourier2DFromIndex(rotated_image, kernel_index);
             return rotated_image;
           })
      .def("RotateFourier2DIndex", [](Image &__inst, Kernel2D *kernel_index, float resolution_limit, float padding_factor)
           {
             AnglesAndShifts rotation_angle;
             __inst.RotateFourier2DIndex(kernel_index, rotation_angle, resolution_limit, padding_factor);
             return rotation_angle;
           })
      .def("ReturnLinearInterpolatedFourierKernel2D", [](Image &__inst)
           {
             float x;
             float y;
             auto __ret = __inst.ReturnLinearInterpolatedFourierKernel2D(x, y);
             return std::make_tuple(__ret, x, y);
           })
      .def("RotateFourier2D", [](Image &__inst, float resolution_limit_in_reciprocal_pixels, bool use_nearest_neighbor)
           {
             ::Image rotated_image;
             AnglesAndShifts rotation_angle;
             __inst.RotateFourier2D(rotated_image, rotation_angle, resolution_limit_in_reciprocal_pixels, use_nearest_neighbor);
             return std::make_tuple(rotated_image, rotation_angle);
           })
      .def("Rotate2D", [](Image &__inst, float mask_radius_in_pixels)
           {
             ::Image rotated_image;
             AnglesAndShifts rotation_angle;
             __inst.Rotate2D(rotated_image, rotation_angle, mask_radius_in_pixels);
             return std::make_tuple(rotated_image, rotation_angle);
           })
      .def("Rotate2DInPlace", &Image::Rotate2DInPlace)
      .def("Rotate2DSample", [](Image &__inst, float mask_radius_in_pixels)
           {
             ::Image rotated_image;
             AnglesAndShifts rotation_angle;
             __inst.Rotate2DSample(rotated_image, rotation_angle, mask_radius_in_pixels);
             return std::make_tuple(rotated_image, rotation_angle);
           })
      .def("Skew2D", [](Image &__inst, float height_offset, float minimum_height, float skew_axis, float skew_angle, bool adjust_signal)
           {
             ::Image skewed_image;
             auto __ret = __inst.Skew2D(skewed_image, height_offset, minimum_height, skew_axis, skew_angle, adjust_signal);
             return std::make_tuple(__ret, skewed_image);
           })
      .def("ReturnLinearInterpolated2D", [](Image &__inst)
           {
             float wanted_physical_x_coordinate;
             float wanted_physical_y_coordinate;
             auto __ret = __inst.ReturnLinearInterpolated2D(wanted_physical_x_coordinate, wanted_physical_y_coordinate);
             return std::make_tuple(__ret, wanted_physical_x_coordinate, wanted_physical_y_coordinate);
           })
      .def("ReturnNearest2D", [](Image &__inst)
           {
             float wanted_physical_x_coordinate;
             float wanted_physical_y_coordinate;
             auto __ret = __inst.ReturnNearest2D(wanted_physical_x_coordinate, wanted_physical_y_coordinate);
             return std::make_tuple(__ret, wanted_physical_x_coordinate, wanted_physical_y_coordinate);
           })
      .def("ExtractSlice", [](Image &__inst, Image &image_to_extract, AnglesAndShifts &angles_and_shifts_of_image, float resolution_limit, bool apply_resolution_limit)
           {
             __inst.ExtractSlice(image_to_extract, angles_and_shifts_of_image, resolution_limit, apply_resolution_limit);
           })
      .def("ExtractSliceByRotMatrix", [](Image &__inst, float resolution_limit, bool apply_resolution_limit)
           {
             ::Image image_to_extract;
             RotationMatrix wanted_matrix;
             __inst.ExtractSliceByRotMatrix(image_to_extract, wanted_matrix, resolution_limit, apply_resolution_limit);
             return std::make_tuple(image_to_extract, wanted_matrix);
           })
      .def("ReturnNearestFourier2D", [](Image &__inst)
           {
             float x;
             float y;
             auto __ret = __inst.ReturnNearestFourier2D(x, y);
             return std::make_tuple(__ret, x, y);
           })
      .def("ReturnLinearInterpolatedFourier2D", [](Image &__inst)
           {
             float x;
             float y;
             auto __ret = __inst.ReturnLinearInterpolatedFourier2D(x, y);
             return std::make_tuple(__ret, x, y);
           })
      .def("ReturnLinearInterpolatedFourier", [](Image &__inst)
           {
             float x;
             float y;
             float z;
             auto __ret = __inst.ReturnLinearInterpolatedFourier(x, y, z);
             return std::make_tuple(__ret, x, y, z);
           })
      .def("AddByLinearInterpolationReal", [](Image &__inst)
           {
             float wanted_x_coordinate;
             float wanted_y_coordinate;
             float wanted_z_coordinate;
             float wanted_value;
             __inst.AddByLinearInterpolationReal(wanted_x_coordinate, wanted_y_coordinate, wanted_z_coordinate, wanted_value);
             return std::make_tuple(wanted_x_coordinate, wanted_y_coordinate, wanted_z_coordinate, wanted_value);
           })
      .def("AddByLinearInterpolationFourier2D", [](Image &__inst)
           {
             float wanted_x_coordinate;
             float wanted_y_coordinate;
             std::complex<float> wanted_value;
             __inst.AddByLinearInterpolationFourier2D(wanted_x_coordinate, wanted_y_coordinate, wanted_value);
             return std::make_tuple(wanted_x_coordinate, wanted_y_coordinate, wanted_value);
           })
      .def("CosineRingMask", &Image::CosineRingMask)
      .def("CosineMask", &Image::CosineMask)
      .def("CosineRectangularMask", &Image::CosineRectangularMask)
      .def("ConvertToAutoMask", &Image::ConvertToAutoMask)
      .def("LocalResSignificanceFilter", &Image::LocalResSignificanceFilter)
      .def("GaussianLowPassFilter", &Image::GaussianLowPassFilter)
      .def("GaussianHighPassFilter", &Image::GaussianHighPassFilter)
      .def("ApplyLocalResolutionFilter", [](Image &__inst, float pixel_size, int wanted_number_of_levels)
           {
             ::Image local_resolution_map;
             __inst.ApplyLocalResolutionFilter(local_resolution_map, pixel_size, wanted_number_of_levels);
             return local_resolution_map;
           })
      .def("CircleMask", &Image::CircleMask)
      .def("CircleMaskWithValue", &Image::CircleMaskWithValue)
      .def("SquareMaskWithValue", &Image::SquareMaskWithValue)
      .def("TriangleMask", &Image::TriangleMask)
      .def("CalculateCTFImage", [](Image &__inst, bool calculate_complex_ctf, bool apply_coherence_envelope)
           {
             CTF ctf_of_image;
             __inst.CalculateCTFImage(ctf_of_image, calculate_complex_ctf, apply_coherence_envelope);
             return ctf_of_image;
           })
      .def("CalculateBeamTiltImage", [](Image &__inst, bool output_phase_shifts)
           {
             CTF ctf_of_image;
             __inst.CalculateBeamTiltImage(ctf_of_image, output_phase_shifts);
             return ctf_of_image;
           })
      .def("ContainsBlankEdges", &Image::ContainsBlankEdges)
      .def("CorrectMagnificationDistortion", &Image::CorrectMagnificationDistortion)
      .def("ApplyMask", [](Image &__inst, float cosine_edge_width, float weight_outside_mask, float low_pass_filter_outside, float filter_cosine_edge_width, float outside_mask_value, bool use_outside_mask_value)
           {
             ::Image mask_file;
             auto __ret = __inst.ApplyMask(mask_file, cosine_edge_width, weight_outside_mask, low_pass_filter_outside, filter_cosine_edge_width, outside_mask_value, use_outside_mask_value);
             return std::make_tuple(__ret, mask_file);
           })
      .def("CenterOfMass", &Image::CenterOfMass)
      .def("StandardDeviationOfMass", &Image::StandardDeviationOfMass)
      .def("ReturnAverageOfMaxN", &Image::ReturnAverageOfMaxN)
      .def("ReturnAverageOfMinN", &Image::ReturnAverageOfMinN)
      .def("AddSlices", [](Image &__inst, int first_slice, int last_slice, bool calculate_average)
           {
             ::Image sum_of_slices;
             __inst.AddSlices(sum_of_slices, first_slice, last_slice, calculate_average);
             return sum_of_slices;
           })
      .def("FindBeamTilt", [](Image &__inst, float pixel_size, float phase_multiplier, bool progress_bar, int first_position_to_search, int last_position_to_search, MyApp *app_for_result)
           {
             CTF input_ctf;
             ::Image phase_error_output;
             ::Image beamtilt_output;
             ::Image difference_image;
             float beamtilt_x;
             float beamtilt_y;
             float particle_shift_x;
             float particle_shift_y;
             auto __ret = __inst.FindBeamTilt(input_ctf, pixel_size, phase_error_output, beamtilt_output, difference_image, beamtilt_x, beamtilt_y, particle_shift_x, particle_shift_y, phase_multiplier, progress_bar, first_position_to_search, last_position_to_search, app_for_result);
             return std::make_tuple(__ret, input_ctf, phase_error_output, beamtilt_output, difference_image, beamtilt_x, beamtilt_y, particle_shift_x, particle_shift_y);
           })
      .def("ReturnVolumeInRealSpace", &Image::ReturnVolumeInRealSpace)
      .def("ReturnReal1DAddressFromPhysicalCoord", &Image::ReturnReal1DAddressFromPhysicalCoord)
      .def("ReturnRealPixelFromPhysicalCoord", &Image::ReturnRealPixelFromPhysicalCoord)
      .def("ReturnFourier1DAddressFromPhysicalCoord", &Image::ReturnFourier1DAddressFromPhysicalCoord)
      .def("ReturnFourier1DAddressFromLogicalCoord", &Image::ReturnFourier1DAddressFromLogicalCoord)
      .def("ReturnComplexPixelFromLogicalCoord", &Image::ReturnComplexPixelFromLogicalCoord)
      .def("HasSameDimensionsAs", &Image::HasSameDimensionsAs)
      .def("IsCubic", &Image::IsCubic)
      .def("IsSquare", &Image::IsSquare)
      .def("ReturnCosineMaskBandpassResolution", [](Image &__inst, float pixel_size_in_angstrom)
           {
             float wanted_cutoff_in_angstrom;
             float wanted_falloff_in_number_of_fourier_space_voxels;
             __inst.ReturnCosineMaskBandpassResolution(pixel_size_in_angstrom, wanted_cutoff_in_angstrom, wanted_falloff_in_number_of_fourier_space_voxels);
             return std::make_tuple(wanted_cutoff_in_angstrom, wanted_falloff_in_number_of_fourier_space_voxels);
           })
      .def("IsBinary", &Image::IsBinary)
      .def("SetLogicalDimensions", &Image::SetLogicalDimensions)
      .def("UpdateLoopingAndAddressing", &Image::UpdateLoopingAndAddressing)
      .def("UpdatePhysicalAddressOfBoxCenter", &Image::UpdatePhysicalAddressOfBoxCenter)
      .def("ReturnFourierLogicalCoordGivenPhysicalCoord_X", &Image::ReturnFourierLogicalCoordGivenPhysicalCoord_X)
      .def("ReturnFourierLogicalCoordGivenPhysicalCoord_Y", &Image::ReturnFourierLogicalCoordGivenPhysicalCoord_Y)
      .def("ReturnFourierLogicalCoordGivenPhysicalCoord_Z", &Image::ReturnFourierLogicalCoordGivenPhysicalCoord_Z)
      .def("ReturnMaximumDiagonalRadius", &Image::ReturnMaximumDiagonalRadius)
      .def("FourierComponentHasExplicitHermitianMate", &Image::FourierComponentHasExplicitHermitianMate)
      .def("FourierComponentIsExplicitHermitianMate", &Image::FourierComponentIsExplicitHermitianMate)
      .def("NormalizeFT", &Image::NormalizeFT)
      .def("NormalizeFTAndInvertRealValues", &Image::NormalizeFTAndInvertRealValues)
      .def("DivideByConstant", &Image::DivideByConstant)
      .def("MultiplyByConstant", &Image::MultiplyByConstant)
      .def("InvertRealValues", &Image::InvertRealValues)
      .def("TakeReciprocalRealValues", &Image::TakeReciprocalRealValues)
      .def("AddConstant", &Image::AddConstant)
      .def("MultiplyAddConstant", &Image::MultiplyAddConstant)
      .def("AddMultiplyConstant", &Image::AddMultiplyConstant)
      .def("AddMultiplyAddConstant", &Image::AddMultiplyAddConstant)
      .def("SquareRealValues", &Image::SquareRealValues)
      .def("SquareRootRealValues", &Image::SquareRootRealValues)
      .def("ExponentiateRealValues", &Image::ExponentiateRealValues)
      .def("ReturnNumberofNonZeroPixels", &Image::ReturnNumberofNonZeroPixels)
      .def("ForwardFFT", &Image::ForwardFFT)
      .def("BackwardFFT", &Image::BackwardFFT)
      .def("AddFFTWPadding", &Image::AddFFTWPadding)
      .def("RemoveFFTWPadding", &Image::RemoveFFTWPadding)
      //.def("ReadSlice", (void (Image::*)(MRCFile,long))&Image::ReadSlice)
      /* .def("ReadSlice", (void (Image::*)(DMFile,long))&Image::ReadSlice)
      .def("ReadSlice", (void (Image::*)(EerFile,long))&Image::ReadSlice)
      .def("ReadSlice", (void (Image::*)(ImageFile,long))&Image::ReadSlice) */
      //.def("ReadSlices", (void (Image::*)(MRCFile,long,long))&Image::ReadSlices)
      /* .def("ReadSlices", (void (Image::*)(DMFile,long,long))&Image::ReadSlices)
      .def("ReadSlices", (void (Image::*)(EerFile,long,long))&Image::ReadSlices)
      .def("ReadSlices", (void (Image::*)(ImageFile,long,long))&Image::ReadSlices) */
      .def("WriteSlice", &Image::WriteSlice)
      .def("WriteSlices", &Image::WriteSlices)
      .def("WriteSlicesAndFillHeader", &Image::WriteSlicesAndFillHeader)
      .def("QuickAndDirtyWriteSlices", &Image::QuickAndDirtyWriteSlices)
      .def("QuickAndDirtyWriteSlice", &Image::QuickAndDirtyWriteSlice)
      .def("QuickAndDirtyReadSlice", &Image::QuickAndDirtyReadSlice)
      .def("QuickAndDirtyReadSlices", &Image::QuickAndDirtyReadSlices)
      .def("IsConstant", &Image::IsConstant)
      .def("HasNan", &Image::HasNan)
      .def("HasNegativeRealValue", &Image::HasNegativeRealValue)
      .def("SetToConstant", &Image::SetToConstant)
      .def("ClipIntoLargerRealSpace2D", &Image::ClipIntoLargerRealSpace2D)
      .def("ClipInto", &Image::ClipInto)
      .def("ChangePixelSize", &Image::ChangePixelSize)
      .def("InsertOtherImageAtSpecifiedPosition", &Image::InsertOtherImageAtSpecifiedPosition)
      .def("Resize", &Image::Resize)
      .def("RealSpaceBinning", &Image::RealSpaceBinning)
      .def("ReturnVarianceOfRealValuesTiled", &Image::ReturnVarianceOfRealValuesTiled)
      .def("CopyFrom", &Image::CopyFrom)
      .def("CopyLoopingAndAddressingFrom", &Image::CopyLoopingAndAddressingFrom)
      .def("Consume", &Image::Consume)
      .def("RealSpaceIntegerShift", &Image::RealSpaceIntegerShift)
      .def("DilateBinarizedMask", &Image::DilateBinarizedMask)
      .def("ErodeBinarizedMask", &Image::ErodeBinarizedMask)
      .def("PhaseShift", &Image::PhaseShift)
      .def("MakeAbsolute", &Image::MakeAbsolute)
      .def("AddImage", &Image::AddImage)
      .def("SubtractImage", &Image::SubtractImage)
      .def("SubtractSquaredImage", &Image::SubtractSquaredImage)
      .def("ApplyBFactor", &Image::ApplyBFactor)
      .def("ApplyBFactorAndWhiten", [](Image &__inst, float bfactor_low, float bfactor_high, float bfactor_res_limit)
           {
             Curve power_spectrum;
             __inst.ApplyBFactorAndWhiten(power_spectrum, bfactor_low, bfactor_high, bfactor_res_limit);
             return power_spectrum;
           })
      .def("CalculateDerivative", &Image::CalculateDerivative)
      .def("SharpenMap", &Image::SharpenMap)
      .def("InvertHandedness", &Image::InvertHandedness)
      .def("ApplyCTFPhaseFlip", &Image::ApplyCTFPhaseFlip)
      .def("ApplyCTF", &Image::ApplyCTF)
      .def("ApplyCurveFilter", &Image::ApplyCurveFilter)
      .def("ApplyCurveFilterUninterpolated", &Image::ApplyCurveFilterUninterpolated)
      .def("MaskCentralCross", &Image::MaskCentralCross)
      .def("ZeroCentralPixel", &Image::ZeroCentralPixel)
      .def("CalculateCrossCorrelationImageWith", &Image::CalculateCrossCorrelationImageWith)
      .def("SwapRealSpaceQuadrants", &Image::SwapRealSpaceQuadrants)
      .def("ComputeAmplitudeSpectrumFull2D", &Image::ComputeAmplitudeSpectrumFull2D)
      .def("ComputeFilteredAmplitudeSpectrumFull2D", [](Image &__inst, Image *average_spectrum_masked, Image *current_power_spectrum, float minimum_resolution, float maximum_resolution, float pixel_size_for_fitting)
           {
             float average;
             float sigma;
             __inst.ComputeFilteredAmplitudeSpectrumFull2D(average_spectrum_masked, current_power_spectrum, average, sigma, minimum_resolution, maximum_resolution, pixel_size_for_fitting);
             return std::make_tuple(average, sigma);
           })
      .def("ComputeAmplitudeSpectrum", &Image::ComputeAmplitudeSpectrum)
      .def("ComputeHistogramOfRealValuesCurve", &Image::ComputeHistogramOfRealValuesCurve)
      .def("Compute1DAmplitudeSpectrumCurve", &Image::Compute1DAmplitudeSpectrumCurve)
      .def("Compute1DPowerSpectrumCurve", &Image::Compute1DPowerSpectrumCurve)
      .def("Compute1DRotationalAverage", [](Image &__inst, bool fractional_radius_in_real_space, bool average_real_parts)
           {
             Curve average;
             Curve number_of_values;
             average.SetupXAxis(0.0, 0.5 * sqrtf(2.0), int((__inst.logical_x_dimension / 2.0 + 1.0) * sqrtf(2.0) + 1.0));
	           number_of_values.SetupXAxis(0.0, 0.5 * sqrtf(2.0), int((__inst.logical_x_dimension / 2.0 + 1.0) * sqrtf(2.0) + 1.0));

             __inst.Compute1DRotationalAverage(average, number_of_values, fractional_radius_in_real_space, average_real_parts);
             return std::make_tuple(average, number_of_values);
           })
      .def("ComputeSpatialFrequencyAtEveryVoxel", &Image::ComputeSpatialFrequencyAtEveryVoxel)
      .def("AverageRadially", &Image::AverageRadially)
      .def("ComputeLocalMeanAndVarianceMaps", &Image::ComputeLocalMeanAndVarianceMaps)
      .def("SpectrumBoxConvolution", &Image::SpectrumBoxConvolution)
      .def("TaperEdges", &Image::TaperEdges)
      .def("ReturnAverageOfRealValues", &Image::ReturnAverageOfRealValues)
      .def("ReturnMedianOfRealValues", &Image::ReturnMedianOfRealValues)
      .def("ReturnAverageOfRealValuesOnEdges", &Image::ReturnAverageOfRealValuesOnEdges)
      .def("ReturnAverageOfRealValuesAtRadius", &Image::ReturnAverageOfRealValuesAtRadius)
      .def("ReturnAverageOfRealValuesInRing", &Image::ReturnAverageOfRealValuesInRing)
      .def("ReturnSigmaOfFourierValuesOnEdges", &Image::ReturnSigmaOfFourierValuesOnEdges)
      .def("ReturnSigmaOfFourierValuesOnEdgesAndCorners", &Image::ReturnSigmaOfFourierValuesOnEdgesAndCorners)
      .def("ReturnMaximumValue", &Image::ReturnMaximumValue)
      .def("ReturnMinimumValue", &Image::ReturnMinimumValue)
      .def("SetMaximumValue", &Image::SetMaximumValue)
      .def("SetMinimumValue", &Image::SetMinimumValue)
      .def("SetMinimumAndMaximumValues", &Image::SetMinimumAndMaximumValues)
      .def("Binarise", &Image::Binarise)
      .def("BinariseInverse", &Image::BinariseInverse)
      .def("ComputeAverageAndSigmaOfValuesInSpectrum", [](Image &__inst, float minimum_radius, float maximum_radius, int cross_half_width)
           {
             float average;
             float sigma;
             __inst.ComputeAverageAndSigmaOfValuesInSpectrum(minimum_radius, maximum_radius, average, sigma, cross_half_width);
             return std::make_tuple(average, sigma);
           })
      .def("SetMaximumValueOnCentralCross", &Image::SetMaximumValueOnCentralCross)
      .def("ApplyMirrorAlongY", &Image::ApplyMirrorAlongY)
      .def("InvertPixelOrder", &Image::InvertPixelOrder)
      .def("GetMinMax", [](Image &__inst)
           {
             float min_value;
             float max_value;
             __inst.GetMinMax(min_value, max_value);
             return std::make_tuple(min_value, max_value);
           })
      .def("RandomisePhases", &Image::RandomisePhases)
      .def("ReturnCorrelationBetweenTwoHorizontalLines", &Image::ReturnCorrelationBetweenTwoHorizontalLines)
      .def("ReturnCorrelationBetweenTwoVerticalLines", &Image::ReturnCorrelationBetweenTwoVerticalLines)
      .def("ContainsRepeatedLineEdges", &Image::ContainsRepeatedLineEdges)
      .def("GetCorrelationWithCTF", &Image::GetCorrelationWithCTF)
      .def("SetupQuickCorrelationWithCTF", [](Image &__inst, CTF ctf, int *addresses, float *spatial_frequency_squared, float *azimuth)
           {
             int number_of_values;
             double norm_image;
             double image_mean;
             __inst.SetupQuickCorrelationWithCTF(ctf, number_of_values, norm_image, image_mean, addresses, spatial_frequency_squared, azimuth);
             return std::make_tuple(number_of_values, norm_image, image_mean);
           })
      .def("QuickCorrelationWithCTF", &Image::QuickCorrelationWithCTF)
      .def("ReturnIcinessOfSpectrum", &Image::ReturnIcinessOfSpectrum)
      .def("GetRealValueByLinearInterpolationNoBoundsCheckImage", [](Image &__inst)
           {
             float x;
             float y;
             float interpolated_value;
             __inst.GetRealValueByLinearInterpolationNoBoundsCheckImage(x, y, interpolated_value);
             return std::make_tuple(x, y, interpolated_value);
           })
      .def("FindPeakAtOriginFast2D", &Image::FindPeakAtOriginFast2D)
      .def("FindPeakWithIntegerCoordinates", &Image::FindPeakWithIntegerCoordinates)
      .def("FindPeakWithParabolaFit", &Image::FindPeakWithParabolaFit)
      .def("SubSampleWithNoisyResampling", &Image::SubSampleWithNoisyResampling)
      .def("SubSampleMask", &Image::SubSampleMask)
      .def("Sine1D", &Image::Sine1D)
      .def("CreateOrthogonalProjectionsImage", &Image::CreateOrthogonalProjectionsImage);

#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif
}
