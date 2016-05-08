import numpy as np
import pfnet
import scipy


class MPProblem():
    problem = dict()
    net = None

    def __init__(self, network):
        self.net = network
        self.timesteps = self.net.timesteps
        self.construct_subproblems()

    def construct_subproblems(self):
        for timestep in range(self.net.timesteps):
            p = pfnet.Problem()
            p.set_network(self.net.network[timestep])
            self.problem[timestep] = p

    def add_function(self, function_type, weight):
        for t in range(self.net.timesteps):
            self.problem[t].add_function(function_type, weight)

    def add_constraint(self, constraint_type):
        for t in range(self.net.timesteps):
            self.problem[t].add_constraint(constraint_type)

    def analyze(self):
        for t in range(self.net.timesteps):
            self.problem[t].analyze()

    def get_init_point(self):
        return np.hstack([self.problem[t].get_init_point() for t in range(self.net.timesteps)])

    def eval(self, x):
        for i in range(self.net.timesteps):
            nx = self.net.num_vars
            self.problem[i].eval(x[i * nx:i * nx + nx])

        return np.hstack([self.problem[i].x for i in range(self.net.timesteps)])

    def construct_battery_constraint_matrices(self):
        """
        constructs the A and b matrices related to the energy constraints of the batteries
        :return:
        """
        a_matrices = []
        b_vectors = []
        for battery in self.net.network[0].batteries:
            (a, b) = self.get_battery_constraint(battery)
            a_matrices.append(a)
            b_vectors.append(b)

        a_total = scipy.sparse.vstack(a_matrices)
        b_total = np.hstack(b_vectors)
        return a_total, b_total

    def get_battery_constraint(self, battery):
        """
        returns the rows of the A matrix representing the battery constraints of the given battery object.
        :param battery: The battery object the constraints are for
        :return: The rows that are added to the A matrix
        """
        index = battery.index
        index_P = battery.index_P
        index_E = battery.index_E
        delta_t = self.net.delta_t

        b = np.zeros((self.net.timesteps,))
        # For first timestep
        data_a = [-1,  # Power
                  1 / delta_t]  # Energy (current)
        row_a = [0, 0]
        column_a = [index_P, index_E]
        b[0] = 1 / delta_t * self.net.e_init

        for i in range(1, self.timesteps):  # start at one as the initial time is sepcial
            nx = self.net.num_vars
            data_a += [-1,  # Power
                       (1 / delta_t),  # Energy (current)
                       (- 1 / delta_t)]  # Energy (previous)
            row_a += [i, i, i]
            column_a += [(i * nx + index_P), (i * nx + index_E), ((i - 1) * nx + index_E)]
            b[i] = 0
        nx = self.net.num_vars
        a = scipy.sparse.coo_matrix((data_a, (row_a, column_a)), shape=(self.timesteps, nx * self.timesteps))
        return a, b

    def construct_problem(self):
        """
        Constructs the A, b, l, u, Hphi and gphi matrices of the problem
        """

        # construct A and b matrices
        network_a = scipy.sparse.block_diag([self.problem[i].A for i in range(self.timesteps)])
        network_b = np.hstack([self.problem[i].b for i in range(self.timesteps)])
        (battery_a, battery_b) = self.construct_battery_constraint_matrices()

        self.A = scipy.sparse.vstack([network_a, battery_a])
        self.b = np.hstack([network_b, battery_b])

        # construct cost function matrices
        f = []
        for i in range(self.timesteps):
            f += self.problem[i].functions

        self.Hphi = scipy.sparse.block_diag([self.problem[i].Hphi for i in range(self.timesteps)])
        self.gphi = np.hstack([self.problem[i].gphi for i in range(self.timesteps)])

        self.x = np.hstack([self.problem[i].x for i in range(self.timesteps)])

        # lower and upper limits
        self.l = np.hstack([self.problem[i].l for i in range(self.timesteps)])
        self.u = np.hstack([self.problem[i].u for i in range(self.timesteps)])
