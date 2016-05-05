from datetime import datetime

import numpy as np
import pfnet
import scipy.sparse

from . import load_profile
from . import solar_profile


class MPNetwork():

    network = dict()
    problem = dict()
    timesteps = 8760
    start_date = datetime.strptime("1.1.2016", "%d.%m.%Y")
    end_date = datetime.strptime("1.1.2017", "%d.%m.%Y")
    load_profile_map = dict()
    solar_profile_map = dict()

    def __init__(self, timesteps=8760):
        self.timesteps = timesteps
        for i in range(self.timesteps):
            self.network[i] = pfnet.Network()


    def load(self, filename):
        for i in range(self.timesteps):
            self.network[i].load(filename)

    def __str__(self):
        return "Multi-Period Network with {0} timesteps".format(self.timesteps)

    def show_components(self):
        buses = self.network[0].num_buses
        branches = self.network[0].num_branches
        shunts = self.network[0].num_shunts
        generators = self.network[0].num_gens
        loads = self.network[0].num_loads

        print("Network Components")
        print("------------------")
        print("timesteps:       : {0}".format(self.timesteps))
        print("buses:           : {0}".format(buses))
        print("branches:        : {0}".format(branches))
        print("shunts:          : {0}".format(shunts))
        print("generators:      : {0}".format(generators))
        print("loads:           : {0}".format(loads))

    def get_bus(self, index, timestep):
        return self.network[timestep].get_bus(index)

    def get_branch(self, index, timestep):
        return self.network[timestep].get_branch(index)

    def get_shunt(self, index, timestep):
        return self.network[timestep].get_shunt(index)

    def get_gen(self, index, timestep):
        return self.network[timestep].get_gen(index)

    def get_load(self, index, timestep):
        return self.network[timestep].get_load(index)

    def generate_load_profiles(self):
        for i in range(self.network[0].num_loads):
            self.load_profile_map[i] = load_profile.LoadProfile().get_load_profile()

            for n in range(self.timesteps):
                load = self.get_load(i, n)
                load.P = self.load_profile_map[i][n] / (self.network[n].base_power * 1e6) # convert to p.u.

    def generate_solar_profiles(self):
        for i in range(self.network[0].num_gens):
            self.solar_profile_map[i] = solar_profile.SolarProfile().get_generation_profile()

            for n in range(self.timesteps):
                generator = self.get_gen(i, n)
                generator.P = self.solar_profile_map[i][n] / (self.network[n].base_power * 1e6) # convert to p.u.


    def get_network_for_time(self, timestep):
        return self.network[0]

    def construct_problem(self):
        self.construct_subproblems()
        A = scipy.sparse.block_diag([self.problem[i].A for i in range(self.timesteps)])

        x = np.vstack([np.array(self.problem[i].x, ndmin=2).transpose() for i in range(self.timesteps)])
        b = np.vstack([np.array(self.problem[i].b, ndmin=2).transpose() for i in range(self.timesteps)])
        f = []
        for i in range(self.timesteps):
            f += self.problem[i].functions
        return A, x, b, f

    def construct_subproblems(self):
        for timestep in range(self.timesteps):
            p = pfnet.Problem()
            p.set_network(self.network[timestep])

            self.network[timestep].clear_flags()

            # bus voltage angles
            self.network[timestep].set_flags(pfnet.OBJ_BUS,
                                             pfnet.FLAG_VARS,
                                             pfnet.BUS_PROP_NOT_SLACK,
                                             pfnet.BUS_VAR_VANG)

            # slack gens active powers
            self.network[timestep].set_flags(pfnet.OBJ_GEN,
                                             pfnet.FLAG_VARS,
                                             pfnet.GEN_PROP_SLACK,
                                             pfnet.GEN_VAR_P)

            p.add_constraint(pfnet.CONSTR_TYPE_DCPF)  # power flow
            p.add_constraint(pfnet.CONSTR_TYPE_PAR_GEN_P)  # generator participation
            p.add_constraint(pfnet.CONSTR_TYPE_PAR_GEN_Q)  # generator participation
            p.analyze()
            x = p.get_init_point()
            p.eval(x)

            self.problem[timestep] = p

    def eval(self, x):
        for i in range(self.timesteps):
            m = len(self.problem[i].x)
            self.problem[i].eval(x.transpose().flatten()[i * m:i * m + m])

        return np.vstack([np.array(self.problem[i].x, ndmin=2).transpose() for i in range(self.timesteps)])

    def update_properties(self, x):
        for i in range(self.timesteps):
            m = len(self.problem[i].x)
            self.network[i].update_properties(x.transpose().flatten()[i * m:i * m + m])

    def get_battery_constraint(self, battery):
        """
        returns the rows of the A matrix representing the battery constraints of the given battery object.
        :param battery: The battery object the constraints are for
        :return: The rows that are added to the A matrix
        """
        pass
