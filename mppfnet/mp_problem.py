import numpy as np
import pfnet
import scipy

from . import CONSTR_TYPE_BAT_DYN


class MPProblem():
    problems = dict()
    net = None
    constraints = []

    A = None
    b = None
    Hphi = None
    gphi = None
    x = None
    l = None
    u = None

    def __init__(self, network):
        self.net = network
        self.timesteps = self.net.timesteps
        self.construct_subproblems()

    def add_constraint(self, constraint_type):
        if constraint_type == CONSTR_TYPE_BAT_DYN:
            self.constraints.append(CONSTR_TYPE_BAT_DYN)
        else:
            for t in range(self.net.timesteps):
                self.problems[t].add_constraint(constraint_type)

    def add_function(self, function_type, weight):
        for t in range(self.net.timesteps):
            self.problems[t].add_function(function_type, weight)

    def analyze(self):
        for t in range(self.net.timesteps):
            self.problems[t].analyze()

        # construct A and b matrices
        self.A = scipy.sparse.block_diag([self.problems[i].A for i in range(self.timesteps)])
        self.b = np.hstack([self.problems[i].b for i in range(self.timesteps)])

        # add battery constraints
        if CONSTR_TYPE_BAT_DYN in self.constraints:
            battery_a = scipy.sparse.vstack(
                [self.get_battery_A(battery) for battery in self.net.get_network().batteries])
            battery_b = np.hstack([self.get_battery_b(battery) for battery in self.net.get_network().batteries])

            self.A = scipy.sparse.vstack([self.A, battery_a])
            self.b = np.hstack([self.b, battery_b])

        self.Hphi = scipy.sparse.block_diag([self.problems[i].Hphi for i in range(self.timesteps)])
        self.gphi = np.hstack([self.problems[i].gphi for i in range(self.timesteps)])

        self.x = np.hstack([self.problems[i].x for i in range(self.timesteps)])

        # lower and upper limits
        self.l = np.hstack([self.problems[i].l for i in range(self.timesteps)])
        self.u = np.hstack([self.problems[i].u for i in range(self.timesteps)])

    def clear(self):
        for t in range(self.net.timesteps):
            self.problems[t].clear()

    def combine_H(self, coeff, ensure_psd):
        pass
        # TODO

    def eval(self, x):
        nx = (self.net.num_vars // self.timesteps)
        for i in range(self.net.timesteps):
            self.problems[i].eval(x[i * nx:i * nx + nx])

        self.x = np.hstack([self.problems[i].x for i in range(self.net.timesteps)])
        self.gphi = np.hstack([self.problems[i].gphi for i in range(self.net.timesteps)])
        self.Hphi = scipy.sparse.block_diag([self.problems[i].Hphi for i in range(self.timesteps)])

        return self.x
    def find_constraint(selfm, type):
        pass  # TODO

    def get_init_point(self):
        return np.hstack([self.problems[t].get_init_point() for t in range(self.net.timesteps)])

    def get_lower_limits(self):
        return np.hstack([self.problems[t].get_lower_limits() for t in range(self.net.timesteps)])

    def get_network(self):
        return self.net

    def get_upper_limits(self):
        return np.hstack([self.problems[t].get_upper_limits() for t in range(self.net.timesteps)])

    def set_network(self, net):
        self.net = net

    def show(self):
        pass  # TODO

    def store_sensitivities(self, sA, sf, sGu, sGl):
        pass  # TODO

    def update_lin(self):
        for problem in self.problems:
            problem.update_lin()

    # Methods specific for MPProblem

    def get_battery_A(self, battery):
        """
        returns the rows of the A matrix representing the battery constraints of the given battery object.
        :param battery: The battery object the constraints are for
        :return: The rows that are added to the A matrix
        """

        index_Pc = battery.index_Pc
        index_Pd = battery.index_Pd
        index_E = battery.index_E
        delta_t = self.net.delta_t

        data_a = []
        row_a = []
        column_a = []
        # For first timestep
        data_a += [-battery.eta_c, 1/battery.eta_d,  # Power
                  1 / delta_t]  # Energy (current)
        row_a = [0,0,  0]
        column_a = [index_Pc, index_Pd, index_E]

        nx = self.net.num_vars // self.timesteps
        for n in range(1, self.timesteps):  # start at one as the initial time is sepcial
            data_a += [(- 1 / delta_t)]  # Energy (previous)
            row_a += [n]
            column_a += [((n - 1) * nx + index_E)]
            data_a += [-battery.eta_c, 1/battery.eta_d,  # Power
                       (1 / delta_t)]  # Energy (current)
            row_a += [n, n, n]
            column_a += [(n * nx + index_Pc), (n * nx + index_Pd), (n * nx + index_E)]
        # For the last timestep
        #data_a += [1 / delta_t, - 1 / delta_t]  # Energy (current)
        #row_a += [self.timesteps, self.timesteps]
        #column_a += [index_E, ((self.timesteps - 1) * nx + index_E)]

        a = scipy.sparse.coo_matrix((data_a, (row_a, column_a)), shape=(self.timesteps, nx * self.timesteps))
       # a = scipy.sparse.coo_matrix((data_a, (row_a, column_a)), shape=(self.timesteps+1, nx * self.timesteps))
        return a

    def get_battery_b(self, battery):
        #b = np.zeros((self.net.timesteps+1,))
        b = np.zeros((self.net.timesteps,))

        b[0] = (1 / self.net.delta_t) * self.net.e_init
        #b[self.timesteps] =  1 / self.net.delta_t * self.net.e_init
        return b

    def construct_subproblems(self):
        for t in range(self.net.timesteps):
            p = pfnet.Problem()
            p.set_network(self.net.get_network(time=t))
            self.problems[t] = p

    def get_coupling_A(self):
        net = self.net.get_network()

        a_i_matrices = dict()
        # construct A_i s
        for bus_i in net.buses:
            row_a_i_j = []
            col_a_i_j = []
            data_a_i_j = []
            for bus_j in net.buses:
                # self-injection
                if bus_j == bus_i:
                    data_a_i_j.append(sum([branch.b for branch in bus_j.branches]))
                    row_a_i_j.append(bus_j.index)
                    col_a_i_j.append(2)
                    data_a_i_j.append(-1.0)
                    row_a_i_j.append(bus_j.index)
                    col_a_i_j.append(3)
                # outgoing branches
                for branch in bus_j.branches_from:
                    if branch.bus_to == bus_i:
                        data_a_i_j.append(-1 * branch.b)
                        row_a_i_j.append(bus_j.index)
                        col_a_i_j.append(2)
                # incoming branches
                for branch in bus_j.branches_to:
                    if branch.bus_from == bus_i:
                        data_a_i_j.append(-1 * branch.b)
                        row_a_i_j.append(bus_j.index)
                        col_a_i_j.append(2)
            # construct A_i matrix
            a_i_matrices[bus_i.index] = scipy.sparse.coo_matrix((data_a_i_j, (row_a_i_j, col_a_i_j)), shape=(net.num_buses,4))

        return a_i_matrices

    def get_local_constraints(self):
        net = self.net.get_network()
        local_constraints = dict()
        for bus in net.buses:

            # battery constraints
            for batteries in bus.bats:
                pass

            local_constraints[bus.index] = (X, l, u)

        return local_constraints