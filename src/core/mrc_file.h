//  \brief  Object for manipulating MRC Files..
//

class MRCFile : public AbstractImageFile {

	public:

	std::fstream my_file;
	MRCHeader my_header;
	wxString filename;

	bool rewrite_header_on_close;
	int max_number_of_seconds_to_wait_for_file_to_exist;


	MRCFile();
	MRCFile(std::string filename, bool overwrite = false);
	MRCFile(std::string filename, bool overwrite, bool wait_for_file_to_exist);
	~MRCFile();

	inline int ReturnXSize() {MyDebugAssertTrue(my_file.is_open(), "File not open!");	return my_header.ReturnDimensionX();};
	inline int ReturnYSize() {MyDebugAssertTrue(my_file.is_open(), "File not open!");	return my_header.ReturnDimensionY();};
	inline int ReturnZSize() {MyDebugAssertTrue(my_file.is_open(), "File not open!");	return my_header.ReturnDimensionZ();};
	inline int ReturnNumberOfSlices() {MyDebugAssertTrue(my_file.is_open(), "File not open!");	return my_header.ReturnDimensionZ();};

	inline bool IsOpen() {return my_file.is_open();}

	bool OpenFile(std::string filename, bool overwrite, bool wait_for_file_to_exist = false);
	void CloseFile();

	inline void ReadSliceFromDisk(int slice_number, float *output_array) {ReadSlicesFromDisk(slice_number, slice_number, output_array);}
	void ReadSlicesFromDisk(int start_slice, int end_slice, float *output_array);

	inline void WriteSliceToDisk(int slice_number, float *input_array) {WriteSlicesToDisk(slice_number, slice_number, input_array);}
	void WriteSlicesToDisk(int start_slice, int end_slice, float *input_array);

	inline void WriteHeader() {my_header.WriteHeader(&my_file);};

	void PrintInfo();

	void SetPixelSize(float wanted_pixel_size);
	inline void SetDensityStatistics( float wanted_min, float wanted_max, float wanted_mean, float wanted_rms ){my_header.SetDensityStatistics(wanted_min, wanted_max, wanted_mean, wanted_rms);}

};
