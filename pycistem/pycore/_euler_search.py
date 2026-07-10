"""Pure-Python reimplementation of the EulerSearch/ParameterMap classes.

Ported from cisTEM/src/core/euler_search.cpp and
cisTEM/src/core/particle.cpp. Only the parts actually used elsewhere in
this repo (grid position counting for match_template.py) are implemented;
EulerSearch.Run() requires the full FFTW-backed Image engine (Tier B) and
is not implemented here.
"""

import math

import numpy as np

_f32 = np.float32


def _deg2rad(degrees):
    # cisTEM/src/core/functions.h: deg_2_rad computes `degrees * PIf / 180.`
    # with `degrees` and PIf as float32 but the division in double
    # precision, narrowed back to float32 on return.
    return _f32(_f32(degrees) * _f32(3.14159265359) / 180.0)


class ParameterMap:
    def __init__(self):
        self.phi = False
        self.theta = False
        self.psi = False
        self.x_shift = False
        self.y_shift = False

    def SetAllTrue(self):
        self.phi = True
        self.theta = True
        self.psi = True
        self.x_shift = True
        self.y_shift = True


class EulerSearch:
    def __init__(self):
        self.number_of_search_dimensions = 0
        self.refine_top_N = 0
        self.number_of_search_positions = 0
        self.best_parameters_to_keep = 0
        self.angular_step_size = 0.0
        self.max_search_x = 0.0
        self.max_search_y = 0.0
        self.phi_max = 0.0
        self.phi_start = 0.0
        self.theta_max = 0.0
        self.theta_start = 0.0
        self.psi_max = 0.0
        self.psi_step = 0.0
        self.psi_start = 0.0
        self.resolution_limit = 0.0
        self.parameter_map = ParameterMap()
        self.test_mirror = False
        self.for_mt = False
        self.symmetry_symbol = ""
        self.list_of_search_parameters = []

    def Init(self, wanted_resolution_limit, wanted_parameter_map, wanted_parameters_to_keep):
        self.parameter_map = wanted_parameter_map
        self.resolution_limit = wanted_resolution_limit
        self.best_parameters_to_keep = wanted_parameters_to_keep

    def InitGrid(
        self,
        wanted_symmetry_symbol,
        wanted_angular_step_size,
        wanted_phi_start,
        wanted_theta_start,
        wanted_psi_max,
        wanted_psi_step,
        wanted_psi_start,
        wanted_resolution_limit,
        wanted_parameter_map,
        wanted_parameters_to_keep,
    ):
        if self.number_of_search_positions == 0:
            self.Init(wanted_resolution_limit, wanted_parameter_map, wanted_parameters_to_keep)

        self.angular_step_size = wanted_angular_step_size
        self.phi_start = wanted_phi_start
        self.theta_start = wanted_theta_start
        self.psi_max = wanted_psi_max
        self.psi_step = wanted_psi_step
        self.psi_start = wanted_psi_start
        self.symmetry_symbol = wanted_symmetry_symbol

        self.SetSymmetryLimits()
        self.CalculateGridSearchPositions()

        if self.number_of_search_positions < self.best_parameters_to_keep:
            self.best_parameters_to_keep = self.number_of_search_positions

    def CalculateGridSearchPositions(self, random_start_angle=True):
        # cisTEM declares all of these as C++ `float` (32-bit); the exact
        # positions of the `theta < theta_max_local + theta_step / 2.0` and
        # `phi < phi_max` loop boundaries are precision-sensitive (an
        # off-by-one there changes number_of_search_positions), so the
        # arithmetic below is done in float32 throughout to match.
        angular_step_size = _f32(self.angular_step_size)
        phi_max = _f32(self.phi_max)
        theta_max = _f32(self.theta_max)
        theta_start = _f32(self.theta_start)
        phi_start = _f32(self.phi_start)

        phi_step = _f32(360.0)
        theta_step = _f32(360.0)
        theta_max_local = theta_max
        phi_start_local = phi_start
        theta_start_local = theta_start

        if self.parameter_map.phi:
            theta_step = theta_max_local / _f32(int(theta_max_local / angular_step_size + _f32(0.5)))
            if random_start_angle:
                theta_start_local = abs(theta_step / _f32(2.0) * _f32(_uniform_random()))
            else:
                theta_start_local = _f32(0.0)
            if self.for_mt:
                theta_start_local = theta_start
        else:
            theta_start_local = theta_start
            theta_max_local = theta_start

        self.list_of_search_parameters = []
        theta = theta_start_local
        while theta < theta_max_local + theta_step / _f32(2.0):
            if self.parameter_map.phi:
                if theta == _f32(0.0) or theta == _f32(180.0):
                    phi_step = phi_max
                else:
                    # angular sampling adapted from Spider subroutine VOEA (Paul Penczek)
                    phi_step = abs(angular_step_size / _f32(math.sin(_deg2rad(theta))))
                    if phi_step > phi_max:
                        phi_step = phi_max
                    phi_step = phi_max / _f32(int(phi_max / phi_step + _f32(0.5)))
                if theta != _f32(0.0) and theta != _f32(180.0):
                    if random_start_angle:
                        phi_start_local = phi_step / _f32(2.0) * _f32(_uniform_random())
                    else:
                        phi_start_local = _f32(0.0)
                    if self.for_mt:
                        phi_start_local = phi_start

            phi = _f32(0.0)
            while phi < phi_max:
                self.list_of_search_parameters.append((float(phi + phi_start_local), float(theta)))
                phi += phi_step
            theta += theta_step

        self.number_of_search_positions = len(self.list_of_search_parameters)

        if not self.parameter_map.psi:
            self.test_mirror = False

    def CalculateRandomSearchPositions(self):
        raise NotImplementedError("EulerSearch.CalculateRandomSearchPositions is not implemented in pycore")

    def InitRandom(self, *args, **kwargs):
        raise NotImplementedError("EulerSearch.InitRandom is not implemented in pycore")

    def Run(self, *args, **kwargs):
        raise NotImplementedError(
            "EulerSearch.Run requires the FFTW-backed Image engine, not implemented in pycore"
        )

    def SetSymmetryLimits(self):
        # Frealign limits, original code written by Richard Henderson.
        if len(self.symmetry_symbol) < 1:
            raise ValueError("Must specify symmetry symbol")

        symmetry_type = self.symmetry_symbol[0].upper()
        if len(self.symmetry_symbol) == 1:
            symmetry_number = 0
        else:
            try:
                symmetry_number = int(self.symmetry_symbol[1:])
            except ValueError as exc:
                raise ValueError("Invalid n after symmetry symbol") from exc

        if symmetry_type == "C":
            if symmetry_number == 0:
                raise ValueError("Invalid n after symmetry symbol")
            self.phi_max = 360.0 / symmetry_number
            self.theta_max = 90.0
            self.test_mirror = True
            return

        if symmetry_type == "D":
            if symmetry_number == 0:
                raise ValueError("Invalid n after symmetry symbol")
            self.phi_max = 360.0 / symmetry_number
            self.theta_max = 90.0
            self.test_mirror = False
            return

        if symmetry_type == "T":
            self.phi_max = 180.0
            self.theta_max = 54.7
            self.test_mirror = False
            return

        if symmetry_type == "O":
            self.phi_max = 90.0
            self.theta_max = 54.7
            self.test_mirror = False
            return

        if symmetry_type == "I":
            self.phi_max = 180.0
            self.theta_max = 31.7
            self.test_mirror = False
            return

        raise ValueError("Invalid symmetry symbol")


def _uniform_random():
    # Only used when random_start_angle=True (not the case for
    # match_template.py's grid-counting usage of InitGrid), so an exact
    # RNG match to cisTEM's global_random_number_generator is not needed.
    import random

    return random.uniform(-1.0, 1.0)
