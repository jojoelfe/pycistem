from pycistem.core import EulerSearch, ParameterMap

global_euler_search = EulerSearch()
parameter_map = ParameterMap()
parameter_map.SetAllTrue( )


global_euler_search.InitGrid("C1",10.0, 0.0, 0.0, 360.0, 10.0, 0.0, 1.0 / 2.0, parameter_map, 10)

global_euler_search.theta_max = 180.0

global_euler_search.CalculateGridSearchPositions(False)

print(global_euler_search.number_of_search_positions)
