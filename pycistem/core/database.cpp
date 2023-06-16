#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
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

void init_database(py::module &m) {
       
  py::class_<Database> database(m, "Database");
  database
      .def(py::init<>())
      .def("Close", &Database::Close)
      .def("ReturnFilename", &Database::ReturnFilename)
      .def("CreateNewDatabase", &Database::CreateNewDatabase)
      .def("Open", &Database::Open)
      .def("Begin", &Database::Begin)
      .def("Commit", &Database::Commit)
      //.def("CreateTable", &Database::CreateTable)
      .def("DeleteTable", &Database::DeleteTable)
      .def("AddColumnToTable", &Database::AddColumnToTable)
      //.def("InsertOrReplace", &Database::InsertOrReplace)
      .def("GetMasterSettings", [](Database &__inst)
           {
             wxFileName project_directory;
             wxString project_name;
             int imported_integer_version;
             double total_cpu_hours;
             int total_jobs_run;
             wxString cistem_version_text;
             cistem::workflow::Enum workflow;
             auto __ret = __inst.GetMasterSettings(project_directory, project_name, imported_integer_version, total_cpu_hours, total_jobs_run, cistem_version_text, workflow);
             return std::make_tuple(__ret, project_directory, project_name, imported_integer_version, total_cpu_hours, total_jobs_run, cistem_version_text, workflow);
           })
      .def("SetProjectStatistics", [](Database &__inst)
           {
             double total_cpu_hours;
             int total_jobs_run;
             auto __ret = __inst.SetProjectStatistics(total_cpu_hours, total_jobs_run);
             return std::make_tuple(__ret, total_cpu_hours, total_jobs_run);
           })
      .def("CreateAllTables", &Database::CreateAllTables)
      //.def("BeginBatchInsert", &Database::BeginBatchInsert)
      //.def("AddToBatchInsert", &Database::AddToBatchInsert)
      //.def("EndBatchInsert", &Database::EndBatchInsert)
      //.def("BeginBatchSelect", &Database::BeginBatchSelect)
      //.def("GetFromBatchSelect", &Database::GetFromBatchSelect)
      //.def("EndBatchSelect", &Database::EndBatchSelect)
      .def("ExecuteSQL", &Database::ExecuteSQL)
      //.def("Prepare", &Database::Prepare)
      //.def("Step", &Database::Step)
      //.def("Finalize", &Database::Finalize)
      .def("CheckBindCode", &Database::CheckBindCode)
      .def("ReturnSingleIntFromSelectCommand", &Database::ReturnSingleIntFromSelectCommand)
      .def("ReturnSingleLongFromSelectCommand", &Database::ReturnSingleLongFromSelectCommand)
      .def("ReturnSingleDoubleFromSelectCommand", &Database::ReturnSingleDoubleFromSelectCommand)
      //.def("ReturnIntArrayFromSelectCommand", &Database::ReturnIntArrayFromSelectCommand)
      //.def("ReturnLongArrayFromSelectCommand", &Database::ReturnLongArrayFromSelectCommand)
      //.def("ReturnStringArrayFromSelectCommand", &Database::ReturnStringArrayFromSelectCommand)
      .def("DoesTableExist", &Database::DoesTableExist)
      .def("DoesColumnExist", &Database::DoesColumnExist)
      .def("ReturnProcessLockInfo", [](Database &__inst)
           {
             long active_process_id;
             wxString active_hostname;
             __inst.ReturnProcessLockInfo(active_process_id, active_hostname);
             return std::make_tuple(active_process_id, active_hostname);
           })
      .def("SetProcessLockInfo", [](Database &__inst)
           {
             long active_process_id;
             wxString active_hostname;
             __inst.SetProcessLockInfo(active_process_id, active_hostname);
             return std::make_tuple(active_process_id, active_hostname);
           })
      .def("ReturnRefinementIDGivenReconstructionID", &Database::ReturnRefinementIDGivenReconstructionID)
      .def("ReturnHighestRefinementID", &Database::ReturnHighestRefinementID)
      .def("ReturnHighestStartupID", &Database::ReturnHighestStartupID)
      .def("ReturnHighestReconstructionID", &Database::ReturnHighestReconstructionID)
      .def("ReturnHighestClassificationID", &Database::ReturnHighestClassificationID)
      .def("ReturnHighestAlignmentID", &Database::ReturnHighestAlignmentID)
      .def("ReturnHighestAlignmentJobID", &Database::ReturnHighestAlignmentJobID)
      .def("ReturnHighestFindCTFID", &Database::ReturnHighestFindCTFID)
      .def("ReturnHighestFindCTFJobID", &Database::ReturnHighestFindCTFJobID)
      .def("ReturnHighestPickingID", &Database::ReturnHighestPickingID)
      .def("ReturnHighestPickingJobID", &Database::ReturnHighestPickingJobID)
      .def("ReturnHighestParticlePositionID", &Database::ReturnHighestParticlePositionID)
      .def("ReturnHighestClassumSelectionID", &Database::ReturnHighestClassumSelectionID)
      .def("ReturnHighestTemplateMatchID", &Database::ReturnHighestTemplateMatchID)
      .def("ReturnHighestTemplateMatchJobID", &Database::ReturnHighestTemplateMatchJobID)
      .def("SetActiveTemplateMatchJobForGivenImageAssetID", &Database::SetActiveTemplateMatchJobForGivenImageAssetID)
      .def("ReturnNumberOfPreviousMovieAlignmentsByAssetID", &Database::ReturnNumberOfPreviousMovieAlignmentsByAssetID)
      .def("ReturnNumberOfPreviousTemplateMatchesByAssetID", &Database::ReturnNumberOfPreviousTemplateMatchesByAssetID)
      .def("ReturnNumberOfPreviousCTFEstimationsByAssetID", &Database::ReturnNumberOfPreviousCTFEstimationsByAssetID)
      .def("ReturnNumberOfPreviousParticlePicksByAssetID", &Database::ReturnNumberOfPreviousParticlePicksByAssetID)
      .def("ReturnNumberOfAlignmentJobs", &Database::ReturnNumberOfAlignmentJobs)
      .def("ReturnNumberOfCTFEstimationJobs", &Database::ReturnNumberOfCTFEstimationJobs)
      .def("ReturnNumberOfTemplateMatchingJobs", &Database::ReturnNumberOfTemplateMatchingJobs)
      .def("ReturnNumberOfPickingJobs", &Database::ReturnNumberOfPickingJobs)
      .def("ReturnNumberOfImageAssetsWithCTFEstimates", &Database::ReturnNumberOfImageAssetsWithCTFEstimates)
      .def("GetUniqueAlignmentIDs", &Database::GetUniqueAlignmentIDs)
      .def("GetUniqueCTFEstimationIDs", &Database::GetUniqueCTFEstimationIDs)
      .def("GetUniqueTemplateMatchIDs", &Database::GetUniqueTemplateMatchIDs)
      .def("GetUniquePickingJobIDs", &Database::GetUniquePickingJobIDs)
      .def("GetUniqueIDsOfImagesWithCTFEstimations", [](Database &__inst, int *image_ids)
           {
             int number_of_image_ids;
             __inst.GetUniqueIDsOfImagesWithCTFEstimations(image_ids, number_of_image_ids);
             return number_of_image_ids;
           })
      .def("GetMovieImportDefaults", [](Database &__inst, wxString dark_reference_filename)
           {
             float voltage;
             float spherical_aberration;
             float pixel_size;
             float exposure_per_frame;
             bool movies_are_gain_corrected;
             wxString gain_reference_filename;
             bool movies_are_dark_corrected;
             bool resample_movies;
             float desired_pixel_size;
             bool correct_mag_distortion;
             float mag_distortion_angle;
             float mag_distortion_major_scale;
             float mag_distortion_minor_scale;
             bool protein_is_white;
             int eer_super_res_factor;
             int eer_frames_per_image;
             __inst.GetMovieImportDefaults(voltage, spherical_aberration, pixel_size, exposure_per_frame, movies_are_gain_corrected, gain_reference_filename, movies_are_dark_corrected, dark_reference_filename, resample_movies, desired_pixel_size, correct_mag_distortion, mag_distortion_angle, mag_distortion_major_scale, mag_distortion_minor_scale, protein_is_white, eer_super_res_factor, eer_frames_per_image);
             return std::make_tuple(voltage, spherical_aberration, pixel_size, exposure_per_frame, movies_are_gain_corrected, gain_reference_filename, movies_are_dark_corrected, resample_movies, desired_pixel_size, correct_mag_distortion, mag_distortion_angle, mag_distortion_major_scale, mag_distortion_minor_scale, protein_is_white, eer_super_res_factor, eer_frames_per_image);
           })
      .def("GetImageImportDefaults", [](Database &__inst)
           {
             float voltage;
             float spherical_aberration;
             float pixel_size;
             bool protein_is_white;
             __inst.GetImageImportDefaults(voltage, spherical_aberration, pixel_size, protein_is_white);
             return std::make_tuple(voltage, spherical_aberration, pixel_size, protein_is_white);
           })
      .def("GetActiveDefocusValuesByImageID", [](Database &__inst, long wanted_image_id)
           {
             float defocus_1;
             float defocus_2;
             float defocus_angle;
             float phase_shift;
             float amplitude_contrast;
             float tilt_angle;
             float tilt_axis;
             __inst.GetActiveDefocusValuesByImageID(wanted_image_id, defocus_1, defocus_2, defocus_angle, phase_shift, amplitude_contrast, tilt_angle, tilt_axis);
             return std::make_tuple(defocus_1, defocus_2, defocus_angle, phase_shift, amplitude_contrast, tilt_angle, tilt_axis);
           })
      .def("AddRefinementPackageAsset", &Database::AddRefinementPackageAsset)
      //.def("Return2DClassMembers", &Database::Return2DClassMembers)
      .def("ReturnNumberOf2DClassMembers", &Database::ReturnNumberOf2DClassMembers)
      .def("AddOrReplaceRunProfile", &Database::AddOrReplaceRunProfile)
      .def("DeleteRunProfile", &Database::DeleteRunProfile)
      .def("BeginMovieAssetInsert", &Database::BeginMovieAssetInsert)
      .def("AddNextMovieAsset", [](Database &__inst, int movie_asset_id, std::string name, std::string filename, int position_in_stack, int x_size, int y_size, int number_of_frames, double voltage, double pixel_size, double dose_per_frame, double spherical_aberration, std::string gain_filename, std::string dark_reference, double output_binning_factor, int correct_mag_distortion, float mag_distortion_angle, float mag_distortion_major_scale, float mag_distortion_minor_scale, int protein_is_white, int eer_super_res_factor, int eer_frames_per_imag)
           { return __inst.AddNextMovieAsset(movie_asset_id, name, filename, position_in_stack, x_size, y_size, number_of_frames, voltage, pixel_size, dose_per_frame, spherical_aberration, gain_filename, dark_reference, output_binning_factor, correct_mag_distortion, mag_distortion_angle, mag_distortion_major_scale, mag_distortion_minor_scale, protein_is_white, eer_super_res_factor, eer_frames_per_imag); })
      .def("EndMovieAssetInsert", &Database::EndMovieAssetInsert)
      .def("UpdateNumberOfFramesForAMovieAsset", &Database::UpdateNumberOfFramesForAMovieAsset)
      .def("BeginImageAssetInsert", &Database::BeginImageAssetInsert)
      .def("AddNextImageAsset", &Database::AddNextImageAsset)
      .def("EndImageAssetInsert", &Database::EndImageAssetInsert)
      .def("BeginVolumeAssetInsert", &Database::BeginVolumeAssetInsert)
      .def("AddNextVolumeAsset", &Database::AddNextVolumeAsset)
      .def("EndVolumeAssetInsert", &Database::EndVolumeAssetInsert)
      .def("BeginParticlePositionAssetInsert", &Database::BeginParticlePositionAssetInsert)
      .def("AddNextParticlePositionAsset", &Database::AddNextParticlePositionAsset)
      .def("EndParticlePositionAssetInsert", &Database::EndParticlePositionAssetInsert)
      .def("CreateProcessLockTable", &Database::CreateProcessLockTable)
      .def("CreateParticlePickingResultsTable", [](Database &__inst)
           {
             int picking_job_id;
             auto __ret = __inst.CreateParticlePickingResultsTable(picking_job_id);
             return std::make_tuple(__ret, picking_job_id);
           })
      .def("CreateRefinementPackageContainedParticlesTable", &Database::CreateRefinementPackageContainedParticlesTable)
      .def("CreateRefinementPackageCurrent3DReferencesTable", &Database::CreateRefinementPackageCurrent3DReferencesTable)
      .def("CreateRefinementPackageRefinementsList", &Database::CreateRefinementPackageRefinementsList)
      .def("CreateRefinementPackageClassificationsList", &Database::CreateRefinementPackageClassificationsList)
      .def("CreateRefinementDetailsTable", &Database::CreateRefinementDetailsTable)
      .def("CreateTemplateMatchPeakListTable", &Database::CreateTemplateMatchPeakListTable)
      .def("CreateTemplateMatchPeakChangeListTable", &Database::CreateTemplateMatchPeakChangeListTable)
      .def("CreateRefinementResultTable", &Database::CreateRefinementResultTable)
      .def("CreateRefinementResolutionStatisticsTable", &Database::CreateRefinementResolutionStatisticsTable)
      .def("CreateRefinementAngularDistributionTable", &Database::CreateRefinementAngularDistributionTable)
      .def("CreateClassificationResultTable", &Database::CreateClassificationResultTable)
      .def("CreateClassificationSelectionTable", &Database::CreateClassificationSelectionTable)
      .def("CreateMovieImportDefaultsTable", &Database::CreateMovieImportDefaultsTable)
      .def("CreateImageImportDefaultsTable", &Database::CreateImageImportDefaultsTable)
      .def("CreateStartupResultTable", &Database::CreateStartupResultTable)
      .def("DoVacuum", &Database::DoVacuum)
      .def("BeginAllMovieAssetsSelect", &Database::BeginAllMovieAssetsSelect)
      .def("GetNextMovieAsset", &Database::GetNextMovieAsset)
      .def("EndAllMovieAssetsSelect", &Database::EndAllMovieAssetsSelect)
      .def("BeginAllMovieGroupsSelect", &Database::BeginAllMovieGroupsSelect)
      .def("GetNextMovieGroup", &Database::GetNextMovieGroup)
      .def("EndAllMovieGroupsSelect", &Database::EndAllMovieGroupsSelect)
      .def("BeginAllImageAssetsSelect", &Database::BeginAllImageAssetsSelect)
      .def("GetNextImageAsset", &Database::GetNextImageAsset)
      .def("EndAllImageAssetsSelect", &Database::EndAllImageAssetsSelect)
      .def("BeginAllImageGroupsSelect", &Database::BeginAllImageGroupsSelect)
      .def("GetNextImageGroup", &Database::GetNextImageGroup)
      .def("EndAllImageGroupsSelect", &Database::EndAllImageGroupsSelect)
      .def("BeginAllParticlePositionAssetsSelect", &Database::BeginAllParticlePositionAssetsSelect)
      .def("GetNextParticlePositionAsset", &Database::GetNextParticlePositionAsset)
      .def("GetNextParticlePositionAssetFromResults", &Database::GetNextParticlePositionAssetFromResults)
      .def("EndAllParticlePositionAssetsSelect", &Database::EndAllParticlePositionAssetsSelect)
      .def("BeginAllParticlePositionGroupsSelect", &Database::BeginAllParticlePositionGroupsSelect)
      .def("GetNextParticlePositionGroup", &Database::GetNextParticlePositionGroup)
      .def("EndAllParticlePositionGroupsSelect", &Database::EndAllParticlePositionGroupsSelect)
      .def("BeginAllVolumeAssetsSelect", &Database::BeginAllVolumeAssetsSelect)
      .def("GetNextVolumeAsset", &Database::GetNextVolumeAsset)
      .def("EndAllVolumeAssetsSelect", &Database::EndAllVolumeAssetsSelect)
      .def("BeginAllVolumeGroupsSelect", &Database::BeginAllVolumeGroupsSelect)
      .def("GetNextVolumeGroup", &Database::GetNextVolumeGroup)
      .def("EndAllVolumeGroupsSelect", &Database::EndAllVolumeGroupsSelect)
      .def("BeginAllRunProfilesSelect", &Database::BeginAllRunProfilesSelect)
      .def("GetNextRunProfile", &Database::GetNextRunProfile)
      .def("EndAllRunProfilesSelect", &Database::EndAllRunProfilesSelect)
      .def("BeginAllRefinementPackagesSelect", &Database::BeginAllRefinementPackagesSelect)
      .def("GetNextRefinementPackage", &Database::GetNextRefinementPackage)
      .def("EndAllRefinementPackagesSelect", &Database::EndAllRefinementPackagesSelect)
      //.def("AddStartupJob", &Database::AddStartupJob)
      .def("AddReconstructionJob", &Database::AddReconstructionJob)
      .def("GetReconstructionJob", [](Database &__inst, long wanted_reconstruction_id)
           {
             long refinement_package_asset_id;
             long refinement_id;
             wxString name;
             float inner_mask_radius;
             float outer_mask_radius;
             float resolution_limit;
             float score_weight_conversion;
             bool should_adjust_score;
             bool should_crop_images;
             bool should_save_half_maps;
             bool should_likelihood_blur;
             float smoothing_factor;
             int class_number;
             long volume_asset_id;
             __inst.GetReconstructionJob(wanted_reconstruction_id, refinement_package_asset_id, refinement_id, name, inner_mask_radius, outer_mask_radius, resolution_limit, score_weight_conversion, should_adjust_score, should_crop_images, should_save_half_maps, should_likelihood_blur, smoothing_factor, class_number, volume_asset_id);
             return std::make_tuple(refinement_package_asset_id, refinement_id, name, inner_mask_radius, outer_mask_radius, resolution_limit, score_weight_conversion, should_adjust_score, should_crop_images, should_save_half_maps, should_likelihood_blur, smoothing_factor, class_number, volume_asset_id);
           })
      .def("GetCTFParameters", [](Database &__inst)
           {
             int ctf_estimation_id;
             double acceleration_voltage;
             double spherical_aberration;
             double amplitude_constrast;
             double defocus_1;
             double defocus_2;
             double defocus_angle;
             double additional_phase_shift;
             double iciness;
             __inst.GetCTFParameters(ctf_estimation_id, acceleration_voltage, spherical_aberration, amplitude_constrast, defocus_1, defocus_2, defocus_angle, additional_phase_shift, iciness);
             return std::make_tuple(ctf_estimation_id, acceleration_voltage, spherical_aberration, amplitude_constrast, defocus_1, defocus_2, defocus_angle, additional_phase_shift, iciness);
           })
      .def("AddCTFIcinessColumnIfNecessary", &Database::AddCTFIcinessColumnIfNecessary)
      .def("RemoveParticlePositionsWithGivenParentImageIDFromGroup", [](Database &__inst)
           {
             int group_number_following_gui_convention;
             int parent_image_asset_id;
             __inst.RemoveParticlePositionsWithGivenParentImageIDFromGroup(group_number_following_gui_convention, parent_image_asset_id);
             return std::make_tuple(group_number_following_gui_convention, parent_image_asset_id);
           })
      .def("RemoveParticlePositionAssetsPickedFromImagesAlsoPickedByGivenPickingJobID", [](Database &__inst)
           {
             int picking_job_id;
             __inst.RemoveParticlePositionAssetsPickedFromImagesAlsoPickedByGivenPickingJobID(picking_job_id);
             return picking_job_id;
           })
      .def("RemoveParticlePositionAssetsPickedFromImageWithGivenID", [](Database &__inst)
           {
             int parent_image_asset_id;
             __inst.RemoveParticlePositionAssetsPickedFromImageWithGivenID(parent_image_asset_id);
             return parent_image_asset_id;
           })
      .def("CopyParticleAssetsFromResultsTable", [](Database &__inst)
           {
             int picking_job_id;
             int parent_image_asset_id;
             __inst.CopyParticleAssetsFromResultsTable(picking_job_id, parent_image_asset_id);
             return std::make_tuple(picking_job_id, parent_image_asset_id);
           })
      /*.def("AddArrayOfParticlePositionAssetsToResultsTable", [](Database &__inst, ArrayOfParticlePositionAssets *array_of_assets)
           {
             int picking_job_id;
             __inst.AddArrayOfParticlePositionAssetsToResultsTable(picking_job_id, array_of_assets);
             return picking_job_id;
           })
      .def("AddArrayOfParticlePositionAssetsToAssetsTable", &Database::AddArrayOfParticlePositionAssetsToAssetsTable)
      .def("ReturnArrayOfParticlePositionAssetsFromResultsTable", [](Database &__inst)
           {
             int picking_job_id;
             int parent_image_asset_id;
             auto __ret = __inst.ReturnArrayOfParticlePositionAssetsFromResultsTable(picking_job_id, parent_image_asset_id);
             return std::make_tuple(__ret, picking_job_id, parent_image_asset_id);
           })
      .def("ReturnArrayOfParticlePositionAssetsFromAssetsTable", [](Database &__inst)
           {
             int parent_image_asset_id;
             auto __ret = __inst.ReturnArrayOfParticlePositionAssetsFromAssetsTable(parent_image_asset_id);
             return std::make_tuple(__ret, parent_image_asset_id);
           })
       */
      .def("RemoveParticlePositionsFromResultsList", [](Database &__inst)
           {
             int picking_job_id;
             int parent_image_asset_id;
             __inst.RemoveParticlePositionsFromResultsList(picking_job_id, parent_image_asset_id);
             return std::make_tuple(picking_job_id, parent_image_asset_id);
           })
      .def("ReturnPickingIDGivenPickingJobIDAndParentImageID", [](Database &__inst)
           {
             int picking_job_id;
             int parent_image_asset_id;
             auto __ret = __inst.ReturnPickingIDGivenPickingJobIDAndParentImageID(picking_job_id, parent_image_asset_id);
             return std::make_tuple(__ret, picking_job_id, parent_image_asset_id);
           })
      .def("SetManualEditForPickingID", [](Database &__inst, const bool wanted_manual_edit)
           {
             int picking_id;
             __inst.SetManualEditForPickingID(picking_id, wanted_manual_edit);
             return picking_id;
           })
      .def("AddRefinement", &Database::AddRefinement)
      .def("UpdateRefinementResolutionStatistics", &Database::UpdateRefinementResolutionStatistics)
      .def("AddTemplateMatchingResult", [](Database &__inst, long wanted_template_match_id)
           {
             TemplateMatchJobResults job_details;
             __inst.AddTemplateMatchingResult(wanted_template_match_id, job_details);
             return job_details;
           })
      .def("GetTemplateMatchingResultByID", &Database::GetTemplateMatchingResultByID)
      .def("AddRefinementAngularDistribution", [](Database &__inst, long refinement_id, int class_number)
           {
             AngularDistributionHistogram histogram_to_add;
             __inst.AddRefinementAngularDistribution(histogram_to_add, refinement_id, class_number);
             return histogram_to_add;
           })
      .def("CopyRefinementAngularDistributions", &Database::CopyRefinementAngularDistributions)
      .def("GetRefinementAngularDistributionHistogramData", [](Database &__inst, long wanted_refinement_id, int wanted_class_number)
           {
             AngularDistributionHistogram histogram_to_fill;
             __inst.GetRefinementAngularDistributionHistogramData(wanted_refinement_id, wanted_class_number, histogram_to_fill);
             return histogram_to_fill;
           })
      .def("GetRefinementByID", &Database::GetRefinementByID)
      .def("AddClassification", &Database::AddClassification)
      .def("GetClassificationByID", &Database::GetClassificationByID)
      .def("CheckandUpdateSchema", [](Database& db) {
          auto [missing_tables, missing_columns] = db.CheckSchema();
          db.UpdateSchema(missing_columns);
          db.UpdateVersion();
      })
      
      .def("AddClassificationSelection", &Database::AddClassificationSelection);

}
