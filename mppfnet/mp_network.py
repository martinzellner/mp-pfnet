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
    e_init = 0  # (in MWh)
    delta_t = 1  # (in hours)
    energy_price = 35.0  # (in €/Mwh)

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
        batteries = self.network[0].num_batteries

        print("Network Components")
        print("------------------")
        print("timesteps:       : {0}".format(self.timesteps))
        print("buses:           : {0}".format(buses))
        print("branches:        : {0}".format(branches))
        print("shunts:          : {0}".format(shunts))
        print("generators:      : {0}".format(generators))
        print("loads:           : {0}".format(loads))
        print("batteries:       : {0}".format(batteries))

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
        Hphi = scipy.sparse.block_diag([self.problem[i].Hphi for i in range(self.timesteps)])
        x = np.hstack([self.problem[i].x for i in range(self.timesteps)])
        b = np.hstack([self.problem[i].b for i in range(self.timesteps)])
        l = np.hstack([self.problem[i].get_lower_limits() for i in range(self.timesteps)])
        u = np.hstack([self.problem[i].get_upper_limits() for i in range(self.timesteps)])
        gphi = np.hstack([self.problem[i].gphi for i in range(self.timesteps)])
        f = []
        for i in range(self.timesteps):
            f += self.problem[i].functions
        return A, x, b, f, l, u, Hphi, gphi

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
            p.add_function(pfnet.FUNC_TYPE_NETCON_COST, 1.0)
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

    def get_battery_a(self):
        a_matrices = []
        b_vectors = []
        for battery in self.network[0].batteries:
            (a, b) = self.get_battery_constraint(battery)
            a_matrices.append(a)
            b_vectors.append(b)

        a_total = scipy.sparse.vstack(a_matrices)
        b_total = np.hstack(b_vectors)
        return (a_total, b_total)


    def get_battery_constraint(self, battery):
        """
        returns the rows of the A matrix representing the battery constraints of the given battery object.
        :param battery: The battery object the constraints are for
        :return: The rows that are added to the A matrix
        """
        index = battery.index
        index_P = battery.index_P
        index_E = battery.index_E
        delta_t = self.delta_t

        b = np.zeros((self.timesteps, 1))
        # For first timestep
        data_a = [-1,  # Power
                  1 / delta_t]  # Energy (current)
        row_a = [0, 0]
        column_a = [index_P, index_E]
        b[0] = 1 / delta_t * self.e_init

        for i in range(1, self.timesteps):  # start at one as the initial time is sepcial
            m = len(self.problem[i].x)
            data_a += [-1,  # Power
                       (1 / delta_t),  # Energy (current)
                       (- 1 / delta_t)]  # Energy (previous)
            row_a += [i, i, i]
            column_a += [(i * m + index_P), (i * m + index_E), ((i - 1) * m + index_E)]
            b[i] = 0
        a = scipy.sparse.coo_matrix((data_a, (row_a, column_a)), shape=(self.timesteps, m * self.timesteps))
        return (a, b.flatten())

    def set_prices(self):
        for i in range(self.timesteps):
            for bus in self.network[i].buses:
                bus.price = self.energy_price
