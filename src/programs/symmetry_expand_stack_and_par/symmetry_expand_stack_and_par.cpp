#include "../../core/core_headers.h"

class
SymmetryExpandStackAndPar : public MyApp
{
	public:

	bool DoCalculation();
	void DoInteractiveUserInput();

	private:
};
/*
class
BruteForceMatrixToEuler
{
	RotationMatrix *all_matrices;
	long total_number_of_matrices;
	float *all_phi_values;
	float *all_theta_values;
	float *all_psi_values;
	float angular_sampling;

public :

	BruteForceMatrixToEuler();
	~BruteForceMatrixToEuler();
	void Init(float wanted_angluar_sampling=0.5f);
	void FindClosestEulerAngles(RotationMatrix *input_matrix, float &output_phi, float &output_theta, float &output_psi);
};
*/
IMPLEMENT_APP(SymmetryExpandStackAndPar)

/*
BruteForceMatrixToEuler::BruteForceMatrixToEuler()
{
	angular_sampling = 0.0f;
	total_number_of_matrices = 0;
	all_matrices = NULL;
	all_phi_values = NULL;
	all_theta_values = NULL;
	all_psi_values = NULL;
}

BruteForceMatrixToEuler::~BruteForceMatrixToEuler()
{
	if (all_matrices != NULL) delete [] all_matrices;
	if (all_phi_values != NULL) delete [] all_phi_values;
	if (all_theta_values != NULL) delete [] all_theta_values;
	if (all_psi_values != NULL) delete [] all_psi_values;
}

void BruteForceMatrixToEuler::Init(float wanted_angular_sampling)
{
	if (all_matrices != NULL) delete [] all_matrices;
	if (all_phi_values != NULL) delete [] all_phi_values;
	if (all_theta_values != NULL) delete [] all_theta_values;
	if (all_psi_values != NULL) delete [] all_psi_values;

	float current_phi;
	float current_theta;
	float current_psi;

	total_number_of_matrices = 0;
	long current_matrix = 0;
	EulerSearch	global_euler_search;

	bool parameter_map[5]; // needed for euler search init
	for (int i = 0; i < 5; i++) {parameter_map[i] = true;}

	int			best_parameters_to_keep = 20;


	global_euler_search.InitGrid("C1", wanted_angular_sampling, 0.0f, 0.0, 360.0f, wanted_angular_sampling, 0.0f, 0.5f, parameter_map, best_parameters_to_keep);

	if (global_euler_search.test_mirror == true) // otherwise the theta max is set to 90.0 and test_mirror is set to true.  However, I don't want to have to test the mirrors.
	{
		global_euler_search.theta_max = 180.0f;
		global_euler_search.CalculateGridSearchPositions();
	}


	angular_sampling = wanted_angular_sampling;

	for (long current_search_position = 0; current_search_position < global_euler_search.number_of_search_positions; current_search_position++)
	{
		for (current_psi = 0.0f; current_psi < 360.0f; current_psi += angular_sampling)
		{
			total_number_of_matrices++;
		}
	}

	wxPrintf("There are %li matrices\n", total_number_of_matrices);
/*
	for (current_phi = -180.0f; current_phi < 180.0f; current_phi += angular_sampling)
	{
		for (current_theta = 0.0f; current_theta < 90.0f; current_theta += angular_sampling)
		{
			for (current_psi = -180.0f; current_psi < 180.0f; current_psi += angular_sampling)
			{
				total_number_of_matrices++;
			}
		}

	}

	// allocate memory

	all_matrices = new RotationMatrix[total_number_of_matrices];
	all_phi_values = new float[total_number_of_matrices];
	all_theta_values = new float[total_number_of_matrices];
	all_psi_values = new float[total_number_of_matrices];

	ProgressBar *my_progress = new ProgressBar(total_number_of_matrices);

	/*for (current_phi = -180.0f; current_phi < 180.0f; current_phi += angular_sampling)
	{
		for (current_theta = 0.0f; current_theta < 90.0f; current_theta += angular_sampling)
		{
			for (current_psi = -180.0f; current_psi < 180.0f; current_psi += angular_sampling)
			{
				all_phi_values[current_matrix] = current_phi;
				all_theta_values[current_matrix] = current_theta;
				all_psi_values[current_matrix] = current_psi;
				all_matrices[current_matrix].SetToEulerRotation(current_phi, current_theta, current_psi);

				current_matrix++;
				my_progress->Update(current_matrix);
			}
		}
	}

	for (long current_search_position = 0; current_search_position < global_euler_search.number_of_search_positions; current_search_position++)
	{
		for (current_psi = 0.0f; current_psi < 360.0f; current_psi += angular_sampling)
		{
			all_phi_values[current_matrix] = global_euler_search.list_of_search_parameters[current_search_position][0];
			all_theta_values[current_matrix] = global_euler_search.list_of_search_parameters[current_search_position][1];
			all_psi_values[current_matrix] = current_psi;
			all_matrices[current_matrix].SetToEulerRotation(global_euler_search.list_of_search_parameters[current_search_position][0], global_euler_search.list_of_search_parameters[current_search_position][1], current_psi);

			current_matrix++;
			my_progress->Update(current_matrix);
		}
	}

	delete my_progress;


}

void BruteForceMatrixToEuler::FindClosestEulerAngles(RotationMatrix *input_matrix, float &output_phi, float &output_theta, float &output_psi)
{
	float best_difference = FLT_MAX;
	float best_phi;
	float best_theta;
	float best_psi;
	float current_difference;

	float current_phi;
	float current_theta;
	float current_psi;

	RotationMatrix refine_matrix;

	for (long current_matrix = 0; current_matrix < total_number_of_matrices; current_matrix++)
	{
		current_difference = 0.0f;

		current_difference += fabsf(all_matrices[current_matrix].m[0][0] - input_matrix->m[0][0]);
		current_difference += fabsf(all_matrices[current_matrix].m[1][0] - input_matrix->m[1][0]);
		current_difference += fabsf(all_matrices[current_matrix].m[2][0] - input_matrix->m[2][0]);
		current_difference += fabsf(all_matrices[current_matrix].m[0][1] - input_matrix->m[0][1]);
		current_difference += fabsf(all_matrices[current_matrix].m[1][1] - input_matrix->m[1][1]);
		current_difference += fabsf(all_matrices[current_matrix].m[2][1] - input_matrix->m[2][1]);
		current_difference += fabsf(all_matrices[current_matrix].m[0][2] - input_matrix->m[0][2]);
		current_difference += fabsf(all_matrices[current_matrix].m[1][2] - input_matrix->m[1][2]);
		current_difference += fabsf(all_matrices[current_matrix].m[2][2] - input_matrix->m[2][2]);

		if (current_difference < best_difference)
		{
			best_difference = current_difference;
			best_phi = all_phi_values[current_matrix];
			best_theta = all_theta_values[current_matrix];
			best_psi = all_psi_values[current_matrix];
		}
	}


	float old_best_phi = best_phi;
	float old_best_theta = best_theta;
	float old_best_psi = best_psi;

	for (current_phi = best_phi - angular_sampling; current_phi < old_best_phi + angular_sampling; current_phi += 0.5)
	{
		for (current_theta = best_theta - angular_sampling; current_theta < old_best_theta + angular_sampling; current_theta += 0.5)
		{
			for (current_psi = best_psi - angular_sampling; current_psi < old_best_psi + angular_sampling; current_psi += 0.5)
			{

				refine_matrix.SetToEulerRotation(current_phi, current_theta, current_psi);
				current_difference = 0.0f;

				current_difference += fabsf(refine_matrix.m[0][0] - input_matrix->m[0][0]);
				current_difference += fabsf(refine_matrix.m[1][0] - input_matrix->m[1][0]);
				current_difference += fabsf(refine_matrix.m[2][0] - input_matrix->m[2][0]);
				current_difference += fabsf(refine_matrix.m[0][1] - input_matrix->m[0][1]);
				current_difference += fabsf(refine_matrix.m[1][1] - input_matrix->m[1][1]);
				current_difference += fabsf(refine_matrix.m[2][1] - input_matrix->m[2][1]);
				current_difference += fabsf(refine_matrix.m[0][2] - input_matrix->m[0][2]);
				current_difference += fabsf(refine_matrix.m[1][2] - input_matrix->m[1][2]);
				current_difference += fabsf(refine_matrix.m[2][2] - input_matrix->m[2][2]);

				if (current_difference < best_difference)
				{
					best_difference = current_difference;
					best_phi = current_phi;
					best_theta = current_theta;
					best_psi = current_psi;
				}

			}
		}

	}


	old_best_phi = best_phi;
	old_best_theta = best_theta;
	old_best_psi = best_psi;

	for (current_phi = best_phi - 1; current_phi < old_best_phi + 1; current_phi += 0.1)
	{
		for (current_theta = best_theta - 1; current_theta < old_best_theta + 1; current_theta += 0.1)
		{
			for (current_psi = best_psi - 1; current_psi < old_best_psi + 1; current_psi += 0.1)
			{

				refine_matrix.SetToEulerRotation(current_phi, current_theta, current_psi);
				current_difference = 0.0f;

				current_difference += fabsf(refine_matrix.m[0][0] - input_matrix->m[0][0]);
				current_difference += fabsf(refine_matrix.m[1][0] - input_matrix->m[1][0]);
				current_difference += fabsf(refine_matrix.m[2][0] - input_matrix->m[2][0]);
				current_difference += fabsf(refine_matrix.m[0][1] - input_matrix->m[0][1]);
				current_difference += fabsf(refine_matrix.m[1][1] - input_matrix->m[1][1]);
				current_difference += fabsf(refine_matrix.m[2][1] - input_matrix->m[2][1]);
				current_difference += fabsf(refine_matrix.m[0][2] - input_matrix->m[0][2]);
				current_difference += fabsf(refine_matrix.m[1][2] - input_matrix->m[1][2]);
				current_difference += fabsf(refine_matrix.m[2][2] - input_matrix->m[2][2]);

				if (current_difference < best_difference)
				{
					best_difference = current_difference;
					best_phi = current_phi;
					best_theta = current_theta;
					best_psi = current_psi;
				}

			}
		}

	}


	output_phi = best_phi;
	output_theta = best_theta;
	output_psi = best_psi;

	old_best_phi = best_phi;
	old_best_theta = best_theta;
	old_best_psi = best_psi;

	for (current_phi = best_phi - 0.1; current_phi < old_best_phi + 0.1; current_phi += 0.02)
	{
		for (current_theta = best_theta - 0.1; current_theta < old_best_theta + 0.1; current_theta += 0.02)
		{
			for (current_psi = best_psi - 0.1; current_psi < old_best_psi + 0.1; current_psi += 0.02)
			{

				refine_matrix.SetToEulerRotation(current_phi, current_theta, current_psi);
				current_difference = 0.0f;

				current_difference += fabsf(refine_matrix.m[0][0] - input_matrix->m[0][0]);
				current_difference += fabsf(refine_matrix.m[1][0] - input_matrix->m[1][0]);
				current_difference += fabsf(refine_matrix.m[2][0] - input_matrix->m[2][0]);
				current_difference += fabsf(refine_matrix.m[0][1] - input_matrix->m[0][1]);
				current_difference += fabsf(refine_matrix.m[1][1] - input_matrix->m[1][1]);
				current_difference += fabsf(refine_matrix.m[2][1] - input_matrix->m[2][1]);
				current_difference += fabsf(refine_matrix.m[0][2] - input_matrix->m[0][2]);
				current_difference += fabsf(refine_matrix.m[1][2] - input_matrix->m[1][2]);
				current_difference += fabsf(refine_matrix.m[2][2] - input_matrix->m[2][2]);

				if (current_difference < best_difference)
				{
					best_difference = current_difference;
					best_phi = current_phi;
					best_theta = current_theta;
					best_psi = current_psi;
				}

			}
		}

	}


	output_phi = best_phi;
	output_theta = best_theta;
	output_psi = best_psi;

}
*/


// override the DoInteractiveUserInput

void SymmetryExpandStackAndPar::DoInteractiveUserInput()
{
	wxString	input_particle_images;
	wxString	input_parameter_file;
	wxString	output_particle_images;
	wxString    output_parameter_file;
	wxString 	symmetry;

	bool do_subtraction;
	wxString	input_reconstruction_filename;
	float		pixel_size = 1.0;
	float		voltage_kV = 300.0;
	float		spherical_aberration_mm = 2.7;
	float		amplitude_contrast = 0.07;
	bool        use_least_squares_scaling;
	float 		mask_radius;
	bool do_centring_and_cropping;
	float       centre_x_coord;
	float       centre_y_coord;
	float       centre_z_coord;
	int			cropped_box_size;
	int 		first_particle;
	int			last_particle;

	UserInput *my_input = new UserInput("SymmetryExpandStackAndPar", 1.00);

	input_particle_images = my_input->GetFilenameFromUser("Input particle images", "The input image stack, containing the experimental particle images", "my_image_stack.mrc", true);
	input_parameter_file = my_input->GetFilenameFromUser("Input Frealign parameter filename", "The input parameter file, containing your particle alignment parameters", "my_parameters.par", true);
	output_particle_images = my_input->GetFilenameFromUser("Output expanded stack", "The output image stack, containing symmetry related copies", "my_symmetry_stack.mrc", false);
	output_parameter_file = my_input->GetFilenameFromUser("Output expanded Frealign parameter filename", "The output parameter file, containing symmetry related copies", "my_symmetry_parameters.par", false);
	symmetry = my_input->GetSymmetryFromUser("Particle symmetry", "The symmetry to use", "I2");
	do_subtraction = my_input->GetYesNoFromUser("Include Subtraction Step", "do you also want to include a subtraction step?", "YES");


	if (do_subtraction == true)
	{
		input_reconstruction_filename = my_input->GetFilenameFromUser("Input reconstruction for subtraction", "The 3D reconstruction which will be subtracted", "my_reconstruction.mrc", true);
		pixel_size = my_input->GetFloatFromUser("Pixel size of images (A)", "Pixel size of input images in Angstroms", "1.0", 0.0);
		voltage_kV = my_input->GetFloatFromUser("Beam energy (keV)", "The energy of the electron beam used to image the sample in kilo electron volts", "300.0", 0.0);
		spherical_aberration_mm = my_input->GetFloatFromUser("Spherical aberration (mm)", "Spherical aberration of the objective lens in millimeters", "2.7", 0.0);
		amplitude_contrast = my_input->GetFloatFromUser("Amplitude contrast", "Assumed amplitude contrast", "0.07", 0.0, 1.0);
		use_least_squares_scaling = my_input->GetYesNoFromUser("Use Least Squares Scaling", "Answer yes to scale per particle.", "Yes");
		mask_radius = my_input->GetFloatFromUser("Mask Radius for scaling (A)", "Only consider within this radius for scaling", "100", 0.0);

		do_centring_and_cropping = my_input->GetYesNoFromUser("Centre and crop specific area", "If yes, the (3D) co-ordinates specified will be centred and cropped in the resulting 2D images. Typically, this would be the are that WASNT subtracted", "YES");
	}
	else
	{
		input_reconstruction_filename = "";
		pixel_size = 0.0f;
		voltage_kV = 0.0f;
		spherical_aberration_mm = 0.0f;
		amplitude_contrast = 0.0f;
		use_least_squares_scaling = false;
		mask_radius = 0.0f;
	}

	if (do_centring_and_cropping == true)
	{
		centre_x_coord = my_input->GetFloatFromUser("X-Coord in 3D to centre (pixels)", "0 is bottom left", "100", 0.0);
		centre_y_coord = my_input->GetFloatFromUser("Y-Coord in 3D to centre (pixels)", "0 is bottom left", "100", 0.0);
		centre_z_coord = my_input->GetFloatFromUser("Z-Coord in 3D to centre (pixels)", "0 is bottom left", "100", 0.0);
		cropped_box_size = my_input->GetIntFromUser("Output box size", "images will be cropped to this size after centreing", "100", 0.0);
	}
	else
	{
		centre_x_coord = 0.0f;
		centre_y_coord = 0.0f;
		centre_z_coord = 0.0f;
		cropped_box_size = 0;
	}

	first_particle = my_input->GetIntFromUser("First particle to process", "first particle to process", "1", 1);
	last_particle = my_input->GetIntFromUser("Last  particle to process (0 = last in stack)", "last particle to process", "0", 0);


	delete my_input;

	my_current_job.Reset(17);
	my_current_job.ManualSetArguments("tttttbtffffbfbfffiii",	input_particle_images.ToUTF8().data(),
															input_parameter_file.ToUTF8().data(),
															output_particle_images.ToUTF8().data(),
															output_parameter_file.ToUTF8().data(),
															symmetry.ToUTF8().data(),
															do_subtraction,
															input_reconstruction_filename.ToUTF8().data(),
															pixel_size,
															voltage_kV,
															spherical_aberration_mm,
															amplitude_contrast,
															use_least_squares_scaling,
															mask_radius,
															do_centring_and_cropping,
															centre_x_coord,
															centre_y_coord,
															centre_z_coord,
															cropped_box_size,
															first_particle,
															last_particle);
}

// override the do calculation method which will be what is actually run..

bool SymmetryExpandStackAndPar::DoCalculation()
{
	Particle refine_particle;
	Particle search_particle;

	wxString input_particle_images 				= my_current_job.arguments[0].ReturnStringArgument();
	wxString input_parameter_file 				= my_current_job.arguments[1].ReturnStringArgument();
	wxString output_particle_images				= my_current_job.arguments[2].ReturnStringArgument();
	wxString output_parameter_file				= my_current_job.arguments[3].ReturnStringArgument();
	wxString symmetry							= my_current_job.arguments[4].ReturnStringArgument();
	bool do_subtraction							= my_current_job.arguments[5].ReturnBoolArgument();
	wxString	input_reconstruction_filename	= my_current_job.arguments[6].ReturnStringArgument();
	float		pixel_size						= my_current_job.arguments[7].ReturnFloatArgument();
	float		voltage_kV						= my_current_job.arguments[8].ReturnFloatArgument();
	float		spherical_aberration_mm 		= my_current_job.arguments[9].ReturnFloatArgument();
	float		amplitude_contrast				= my_current_job.arguments[10].ReturnFloatArgument();
	bool        use_least_squares_scaling		= my_current_job.arguments[11].ReturnBoolArgument();
	float 		mask_radius						= my_current_job.arguments[12].ReturnFloatArgument();
	bool do_centring_and_cropping				= my_current_job.arguments[13].ReturnBoolArgument();
	float       centre_x_coord					= my_current_job.arguments[14].ReturnFloatArgument();
	float       centre_y_coord					= my_current_job.arguments[15].ReturnFloatArgument();
	float       centre_z_coord					= my_current_job.arguments[16].ReturnFloatArgument();
	int			cropped_box_size				= my_current_job.arguments[17].ReturnIntegerArgument();
	int			first_particle					= my_current_job.arguments[18].ReturnIntegerArgument();
	int			last_particle					= my_current_job.arguments[19].ReturnIntegerArgument();


	long current_image;
	long position_in_output_stack = 1;
	int symmetry_counter;
	int number_of_images_to_process;



	float temp_float[50];
	float current_phi;
	float current_theta;
	float current_psi;

	float percentage;
	float variance;
	float mask_radius_for_noise;
	float scale_factor;


	float original_x_coord;
	float original_y_coord;
	float original_z_coord;

	float rotated_x_coord;
	float rotated_y_coord;
	float rotated_z_coord;


	double dot_product;
	double self_dot_product;
	long used_pixels;

	long image_counter;
	long pixel_counter;

	float old_x_shift;
	float old_y_shift;

	int number_of_images_processed;

	Image particle_image;
	Image buffer_image;
	Image sum_power;
	Image temp_image;
	Image projection_image;
	Image cropped_image;


	Curve noise_power_spectrum;
	Curve number_of_terms;

	SymmetryMatrix my_symmetry_matrices;
	RotationMatrix original_matrix;
	RotationMatrix current_symmetry_related_matrix;
	RotationMatrix matrix_for_centring;

	ImageFile input_stack(input_particle_images.ToStdString(), false);
	ImageFile *input_3d_file;
	ReconstructedVolume input_3d;

	FrealignParameterFile my_input_par_file(input_parameter_file, OPEN_TO_READ);
	FrealignParameterFile my_output_par_file(output_parameter_file, OPEN_TO_WRITE);

	my_input_par_file.ReadFile();
	if (last_particle == 0) last_particle = my_input_par_file.number_of_lines;
	number_of_images_to_process = (last_particle - first_particle) + 1;

	MRCFile output_stack(output_particle_images.ToStdString(), true);
	my_symmetry_matrices.Init(symmetry);

	AnglesAndShifts my_parameters;
	CTF my_ctf;

	ProgressBar *my_progress;

	if (do_subtraction == true)
	{
		input_3d_file = new ImageFile(input_reconstruction_filename.ToStdString(), false);
		input_3d.InitWithDimensions(input_3d_file->ReturnXSize(), input_3d_file->ReturnYSize(), input_3d_file->ReturnZSize(), pixel_size, "C1");
		input_3d.density_map.ReadSlices(input_3d_file,1,input_3d.density_map.logical_z_dimension);
		input_3d.mask_radius = FLT_MAX;
		input_3d.PrepareForProjections(0.0, 2.0 * pixel_size);

		original_x_coord = centre_x_coord - input_3d.density_map.physical_address_of_box_center_x;
		original_y_coord = centre_y_coord - input_3d.density_map.physical_address_of_box_center_y;
		original_z_coord = centre_z_coord - input_3d.density_map.physical_address_of_box_center_z;

		projection_image.Allocate(input_3d.density_map.logical_x_dimension, input_3d.density_map.logical_y_dimension, false);
		sum_power.Allocate(input_3d.density_map.logical_x_dimension, input_3d.density_map.logical_y_dimension, false);
		if (do_centring_and_cropping == true) cropped_image.Allocate(cropped_box_size, cropped_box_size, 1);

		// now get the power spectra..

		wxPrintf("\nCalculating noise power spectrum...\n\n");

		percentage = float(2500) / float(my_input_par_file.number_of_lines);
		sum_power.SetToConstant(0.0);
		mask_radius_for_noise = mask_radius / pixel_size;

		if (2.0 * mask_radius_for_noise + 0.05 / pixel_size > 0.95 * particle_image.logical_x_dimension)
		{
			mask_radius_for_noise = 0.95 * particle_image.logical_x_dimension / 2.0 - 0.05 / 2.0 / pixel_size;
		}

		noise_power_spectrum.SetupXAxis(0.0, 0.5 * sqrtf(2.0), int((sum_power.logical_x_dimension / 2.0 + 1.0) * sqrtf(2.0) + 1.0));
		number_of_terms.SetupXAxis(0.0, 0.5 * sqrtf(2.0), int((sum_power.logical_x_dimension / 2.0 + 1.0) * sqrtf(2.0) + 1.0));

		my_progress = new ProgressBar(my_input_par_file.number_of_lines);
		image_counter = 0;

		for (current_image = 1; current_image <= my_input_par_file.number_of_lines; current_image++)
		{
			my_input_par_file.ReadLine(temp_float);
			image_counter++;
			my_progress->Update(image_counter);

			if ((global_random_number_generator.GetUniformRandom() < 1.0 - 2.0 * percentage)) continue;

			particle_image.ReadSlice(&input_stack, int(temp_float[0] + 0.5));
			variance = particle_image.ReturnVarianceOfRealValues(mask_radius / pixel_size, 0.0, 0.0, 0.0, true);
			if (variance == 0.0) continue;
			particle_image.MultiplyByConstant(1.0 / sqrtf(variance));
			particle_image.CosineMask(mask_radius / pixel_size, 0.05 / pixel_size, true);
			particle_image.ForwardFFT();
			temp_image.CopyFrom(&particle_image);
			temp_image.ConjugateMultiplyPixelWise(particle_image);
			sum_power.AddImage(&temp_image);
		}


		sum_power.Compute1DRotationalAverage(noise_power_spectrum, number_of_terms);
		noise_power_spectrum.SquareRoot();

		my_input_par_file.Rewind();
		delete my_progress;
	}

	if (do_subtraction == false) wxPrintf("\nExpanding...\n\n");
	else wxPrintf("\nExpanding and Subtracting...\n\n");

	my_progress = new ProgressBar(number_of_images_to_process);

	number_of_images_processed = 0;

	for (current_image = 1; current_image <= my_input_par_file.number_of_lines; current_image++)
	//for (current_image = 1; current_image <= 1; current_image++)
	{
		my_input_par_file.ReadLine(temp_float);
		if (temp_float[0] < first_particle || temp_float[0] > last_particle) continue;

		old_x_shift = temp_float[4];
		old_y_shift = temp_float[5];

		particle_image.ReadSlice(&input_stack, current_image);

		current_phi = temp_float[1];
		current_theta = temp_float[2];
		current_psi = temp_float[3];

		original_matrix.SetToEulerRotation(current_phi, current_theta, current_psi);

		for (symmetry_counter = 1; symmetry_counter <= ReturnNumberofAsymmetricUnits(symmetry); symmetry_counter++)
		{
			current_symmetry_related_matrix = original_matrix * my_symmetry_matrices.rot_mat[symmetry_counter - 1];
			current_symmetry_related_matrix.ConvertToValidEulerAngles(temp_float[1], temp_float[2], temp_float[3]);
			//current_symmetry_related_matrix_transposed = current_symmetry_related_matrix.ReturnTransposed();

			if (do_subtraction == true)
			{
				buffer_image.CopyFrom(&particle_image);
				my_parameters.Init(temp_float[3], temp_float[2], temp_float[1], temp_float[4], temp_float[5]);
				my_ctf.Init(voltage_kV, spherical_aberration_mm, amplitude_contrast, temp_float[8], temp_float[9], temp_float[10], 0.0, 0.0, 0.0, pixel_size, temp_float[11]);

				input_3d.density_map.ExtractSlice(projection_image, my_parameters);
				projection_image.ApplyCTF(my_ctf);
				projection_image.PhaseShift(temp_float[4] / pixel_size, temp_float[5] / pixel_size);
				projection_image.SwapRealSpaceQuadrants();
				projection_image.ApplyCurveFilter(&noise_power_spectrum);
				projection_image.BackwardFFT();

				if (use_least_squares_scaling == true)
				{
					used_pixels = 0;
					dot_product = 0.0;
					self_dot_product = 0.0;

					int x;
					int y;

					float max_radius = powf(mask_radius / pixel_size, 2.0f);
					float x_rad_sq;
					float y_rad_sq;
					float current_radius_squared;

					pixel_counter = 0;

					for ( y = 0; y < particle_image.logical_y_dimension; y ++ )
					{
						y_rad_sq = powf(y - particle_image.physical_address_of_box_center_y, 2.0f);

						for ( x = 0; x < particle_image.logical_x_dimension; x ++ )
						{
							x_rad_sq = powf(x - particle_image.physical_address_of_box_center_x, 2.0f);
							current_radius_squared = x_rad_sq + y_rad_sq;

							if (particle_image.real_values[pixel_counter] != 0. && projection_image.real_values[pixel_counter] != 0. && current_radius_squared < max_radius)
							{
								dot_product += particle_image.real_values[pixel_counter] * projection_image.real_values[pixel_counter];
								self_dot_product += pow(projection_image.real_values[pixel_counter], 2);
								used_pixels++;
							}
							pixel_counter++;

						}

						pixel_counter += particle_image.padding_jump_value;

					}

					scale_factor = dot_product / self_dot_product;
					projection_image.MultiplyByConstant(scale_factor);
				}

				buffer_image.SubtractImage(&projection_image);
				//projection_image.QuickAndDirtyWriteSlice("/tmp/projs.mrc", position_in_output_stack);
				//particle_image.QuickAndDirtyWriteSlice("/tmp/particle.mrc", position_in_output_stack);


			}

			if (do_centring_and_cropping == true)
			{
				// work out rotated coords..

				matrix_for_centring.SetToEulerRotation(-temp_float[1], -temp_float[2], -temp_float[3]);
				matrix_for_centring.RotateCoords(original_x_coord, original_y_coord, original_z_coord, rotated_x_coord, rotated_y_coord, rotated_z_coord);

				//wxPrintf("original coords (%i) = %.2f, %.2f, %.2f\n", symmetry_counter + 1, original_x_coord, original_y_coord, original_z_coord);
				//wxPrintf("rotated  coords (%i) = %.2f, %.2f, %.2f\n", symmetry_counter + 1, rotated_x_coord, rotated_y_coord, rotated_z_coord);


				// phase_shift the subtracted image so that the bit we want is in the centre..

				cropped_image.SetToConstant(0.0f);



				if (do_subtraction == true)
				{
					buffer_image.PhaseShift(-rotated_x_coord - temp_float[4] / pixel_size, -rotated_y_coord - temp_float[5] / pixel_size);
					//buffer_image.PhaseShift(-rotated_x_coord, -rotated_y_coord);
					buffer_image.ClipInto(&cropped_image);
				}
				else
				{
					particle_image.PhaseShift(-rotated_x_coord - temp_float[4] / pixel_size, -rotated_y_coord - temp_float[5] / pixel_size);
					particle_image.ClipInto(&cropped_image);
				}

				cropped_image.WriteSlice(&output_stack, position_in_output_stack);

			}
			else
			{
				if (do_subtraction == true) buffer_image.WriteSlice(&output_stack, position_in_output_stack);
				else particle_image.WriteSlice(&output_stack, position_in_output_stack);
			}

			temp_float[0] = (current_image - 1) * ReturnNumberofAsymmetricUnits(symmetry) + symmetry_counter;
			position_in_output_stack++;

			if (do_centring_and_cropping)
			{
				temp_float[4] = 0.0f;
				temp_float[5] = 0.0f;
				my_output_par_file.WriteLine(temp_float);
				temp_float[4] = old_x_shift;
				temp_float[5] = old_y_shift;
			}

		}

		number_of_images_processed++;
		my_progress->Update(number_of_images_processed);
	}

	delete my_progress;

	if (do_subtraction == true)
	{
		delete input_3d_file;
	}

	wxPrintf("\nSymmetryExpandStackAndPar: Normal termination\n\n");

	return true;
}
