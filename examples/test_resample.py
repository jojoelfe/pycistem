from pycistem.programs.resample import ResampleParameters, run

par = ResampleParameters(
    input_filename="/nrs/elferich/THP1_brequinar/Matches/combined_60S_2_60S_20231214/CD34P_24h.mrc",
    output_filename="/nrs/elferich/THP1_brequinar/Matches/combined_60S_2_60S_20231214/CD34P_24h_8A.mrc"

)

run(par)