import csv
from datetime import datetime

import pfnet
import scipy

from . import load_profile
from . import solar_profile


class MPNetwork():
    networks = dict()
    num_vars = None
    timesteps = 8760
    start_date = datetime.strptime("1.1.2016", "%d.%m.%Y")
    end_date = datetime.strptime("1.1.2017", "%d.%m.%Y")
    load_profile_map = dict()
    solar_profile_map = dict()
    e_init = 0  # (in MWh)
    delta_t = 1  # (in hours)
    energy_price = 35.0  # (in €/Mwh)

    def __init__(self, timesteps=8760):
        """
        Instanciates a new multi-period pfnet network.
        :param timesteps: The number of timesteps the network is created for
        """
        self.timesteps = timesteps
        for i in range(self.timesteps):
            self.networks[i] = pfnet.Network()

    def __str__(self):
        return "Multi-Period Network with {0} timesteps".format(self.timesteps)

    def add_vargens(self, buses, penetration, uncertainty, corr_radius, corr_value):
        """
        Add a variable generator (PV, Wind, etc.) to the network
        :param buses: The buses the generators should be added to
        :param penetration:
        :param uncertainty:
        :param corr_radius:
        :param corr_value:
        """
        for network in self.networks:
            network.add_vargens(buses, penetration, uncertainty, corr_radius, corr_value)

    def adjust_generators(self):
        """

        """
        for network in self.networks:
            network.adjust_generators()

    def clear_error(self):
        for network in self.networks:
            network.clear_error()

    def clear_properties(self):
        for network in self.networks:
            network.clear_properties()

    def clear_sensitivities(self):
        for network in self.networks:
            network.clear_sensitivities()

    def create_sorted_bus_list(self, sort_by, time=0):
        return self.networks[time].create_sorted_bus_list(sort_by)

    def create_vargen_P_sigma(self, spread, corr):
        for network in self.networks:
            network.create_vargen_P_sigma(spread, corr)

    def get_branch(self, index, time=0):
        return self.networks[time].get_branch(index)

    def get_bus(self, index, time=0):
        """
        gets a specific bus for a given time
        :param index: the bus index
        :param time: the time to get the bus for (defaults to 0)
        :return: a pfnet bus object
        """
        return self.networks[time].get_bus(index)

    def get_bus_by_name(self, name, time=0):
        """
        gets a specific bus for a given time
        :param index: the bus name
        :param time: the time to get the bus for (defaults to 0)
        :return: a pfnet bus object
        """
        return self.networks[time].get_bus_by_name(name)

    def get_bus_by_number(self, number, time=0):
        """
        gets a specific bus for a given time
        :param index: the bus number
        :param time: the time to get the bus for (defaults to 0)
        :return: a pfnet bus object
        """
        return self.networks[time].get_bus_by_number(number)

    def get_gen(self, index, time=0):
        """
        gets a specific generator for a given time
        :param index: the generator index
        :param time: the time to get the generator for (defaults to 0)
        :return: a pfnet generator object
        """
        return self.networks[time].get_gen(index)

    def get_gen_buses(self, time=0):
        return self.networks[time].get_gen_buses()

    def get_load(self, index, time=0):
        """
        gets a specific load for a given time
        :param index: the load index
        :param time: the time to get the load for (defaults to 0)
        :return: a pfnet load object
        """
        return self.networks[time].get_load(index)

    def get_load_buses(self, time=0):
        return self.networks[time].get_load_buses()

    def get_num_P_adjust_gens(self, time=0):
        return self.networks[time].get_num_P_adjust_gens()

    def get_num_P_adjust_loads(self, time=0):
        return self.networks[time].get_num_P_adjust_loads()

    def get_num_branches(self, time=0):
        return self.networks[time].get_num_branches()

    def get_num_branches_not_on_outage(self, time=0):
        return self.networks[time].get_num_branches_not_on_outage()

    def get_num_buses(self, time=0):
        return self.networks[time].get_num_buses()

    def get_num_buses_reg_by_gen(self, time=0):
        return self.networks[time].get_num_buses_reg_by_gen()

    def get_num_buses_reg_by_shunt(self, only=False, time=0):
        return self.networks[time].get_num_buses_reg_by_shunt(only)

    def get_num_buses_reg_by_tran(self, only=False, time=0):
        return self.networks[time].get_num_buses_reg_by_tran(only)

    def get_num_fixed_shunts(self, time=0):
        return self.networks[time].get_num_fixed_shunts()

    def get_num_fixed_trans(self, time=0):
        return self.networks[time].get_num_fixed_trans()

    def get_num_gens(self, time=0):
        return self.networks[time].get_num_gens()

    def get_num_gens_not_on_outage(self, time=0):
        return self.networks[time].get_num_gens_not_on_outage()

    def get_num_lines(self, time=0):
        return self.networks[time].get_num_lines()

    def get_num_loads(self, time=0):
        return self.networks[time].get_num_loads()

    def get_num_phase_shifters(self, time=0):
        return self.networks[time].get_num_phase_shifters()

    def get_num_reg_gens(self, time=0):
        return self.networks[time].get_num_reg_gens()

    def get_num_shunts(self, time=0):
        return self.networks[time].get_num_shunts()

    def get_num_slack_buses(self, time=0):
        return self.networks[time].get_num_slack_buses()

    def get_num_slack_gens(self, time=0):
        return self.networks[time].get_num_slack_gens()

    def get_num_switched_shunts(self, time=0):
        return self.networks[time].get_num_switched_shunts()

    def get_num_tap_changers(self, time=0):
        return self.networks[time].get_num_tap_changers()

    def get_num_tap_changers_Q(self, time=0):
        return self.networks[time].get_num_tap_changers_Q()

    def get_num_tap_changers_v(self, time=0):
        return self.networks[time].get_num_tap_changers_v()

    def get_num_vargens(self, time=0):
        return self.networks[time].get_num_vargens()

    def get_properties(self, time=0):
        return self.networks[time].get_properties()

    def get_shunt(self, index, time=0):
        return self.networks[time].get_shunt(index)

    def get_var_projection(self, obj_type, var, time=0):
        return self.networks[time].get_var_projection(obj_type, var)

    def get_var_values(self, code=pfnet.CURRENT, time=0):
        return self.networks[time].get_var_values(code)

    def get_vargen(self, index, time=0):
        return self.networks[time].get_vargen(index)

    def get_vargen_by_name(self, name, time=0):
        return self.networks[time].get_vargen_by_name(name)

    def has_error(self):
        for network in self.networks:
            if network.has_error():
                return True
        return False

    def load(self, filename):
        for i in range(self.timesteps):
            self.networks[i].load(filename)
            self.networks[i].clear_flags()

        # set base power and num_vars so mppfnet behaves like pfnet
        self.base_power = self.networks[0].base_power
        self.num_vars = self.timesteps * self.networks[0].num_vars

    def set_flags(self, obj_type, flags, props, vals):
        """
        Sets flags of networks components with specific properties.
        :param obj_type: Component Types
        :param flags: Flag Marks
        :param props:
        :param vals:
        """
        for i in range(self.timesteps):
            self.networks[i].set_flags(obj_type, flags, props, vals)

        # Update number of variables
        self.num_vars = self.timesteps * self.networks[0].num_vars

    def set_flags_of_component(self, obj, flags, vals):
        """
        Sets flags of networks components with specific properties.
        :param obj:
        :param flags:
        :param vals:
        """
        for i in range(self.timesteps):
            self.networks[i].set_flags_of_component(obj, flags, vals)

    def set_var_values(self, values):
        for i in range(self.timesteps):
            nx = self.num_vars // self.timesteps
            self.networks[i].set_var_values(values[i * nx:i * nx + nx])

    def show_buses(self, number, sort_by, time=0):
        self.networks[time].show_buses(number, sort_by)

    def show_components(self):
        """
        Shows the components of the networks
        """
        net = self.networks[0]

        print("Network Components")
        print("-----------------------------")
        print("timesteps:           : {0}".format(self.timesteps))
        print("------- per timestep --------")
        print("buses:               : {0}".format(net.get_num_buses()))
        print("   slack:            : {0}".format(net.get_num_slack_buses()))
        print("   reg by gen:       : {0}".format(net.get_num_buses_reg_by_gen()))
        print("   reg by tran:      : {0}".format(net.get_num_buses_reg_by_tran()))
        print("   reg by shunt:     : {0}".format(net.get_num_buses_reg_by_shunt()))
        print("shunts:              : {0}".format(net.get_num_shunts()))
        print("   fixed:            : {0}".format(net.get_num_fixed_shunts()))
        print("   switched v:       : {0}".format(net.get_num_switched_shunts()))
        print("branches:            : {0}".format(net.get_num_branches()))
        print("   lines:            : {0}".format(net.get_num_lines()))
        print("   fixed trans:      : {0}".format(net.get_num_fixed_trans()))
        print("   phase shifters    : {0}".format(net.get_num_phase_shifters()))
        print("   tap changers v    : {0}".format(net.get_num_tap_changers_v()))
        print("   tap changers Q    : {0}".format(net.get_num_tap_changers_Q()))
        print("generators:          : {0}".format(net.get_num_gens()))
        print("   slack:            : {0}".format(net.get_num_slack_gens()))
        print("   reg:              : {0}".format(net.get_num_reg_gens()))
        print("   P adjust          : {0}".format(net.get_num_P_adjust_gens()))
        print("loads:               : {0}".format(net.get_num_loads()))
        print("   P adjust:         : {0}".format(net.get_num_P_adjust_loads()))
        print("vargens:             : {0}".format(net.get_num_vargens()))
        print("batteries:           : {0}".format(net.get_num_bats()))

    def show_properties(self, time=0):
        self.networks[time].show_properties()

    def update_properties(self, values=None):
        for i in range(self.timesteps):
            nx = self.num_vars // self.timesteps
            if values is not None:
                self.networks[i].update_properties(values[i * nx:i * nx + nx])
            else:
                self.networks[i].update_properties()

    def update_set_points(self):
        for network in self.networks:
            network.update_set_points()

    # Methods specific to MPPFNET
    def get_network(self, time=0):
        """
        get the pfnet network for a given time
        :param time: the time to get the network for (default: 0)
        :return: a pfnet network object
        """
        return self.networks[time]

    def generate_load_profiles(self):
        """
        generates load profiles using alpg
        """
        for i in range(self.networks[0].num_loads):
            self.load_profile_map[i] = load_profile.LoadProfile().get_load_profile()

            for n in range(self.timesteps):
                load = self.get_load(i, n)
                load.P = self.load_profile_map[i][n] / (self.networks[n].base_power * 1e6)  # convert to p.u.

    def generate_solar_profiles(self):
        """
        Generates solar profiles using PVWatts
        """
        for i in range(self.networks[0].num_vargens):
            self.solar_profile_map[i] = solar_profile.SolarProfile().get_generation_profile()

            for n in range(self.timesteps):
                generator = self.get_vargen(i, n)
                generator.P = self.solar_profile_map[i][n] / (self.networks[n].base_power * 1e6)  # convert to p.u.

    def set_prices(self, price_vector):
        """
        set the price attribute of the buses to the values given.
        :param price_vector: A vector of prices that has at least as many entries as there are time steps in the network.
        """
        for i in range(self.timesteps):
            for bus in self.networks[i].buses:
                if not bus.is_slack():
                    bus.price = price_vector[i]

    def get_adjacency_matrix(self):
        nb = self.get_network().get_num_buses()
        rows = []
        columns = []
        data = []
        for branch in self.get_network().branches:
            rows.append(branch.bus_from.index)
            columns.append(branch.bus_to.index)
            data.append(branch.b)
            # symmetry
            rows.append(branch.bus_to.index)
            columns.append(branch.bus_from.index)
            data.append(branch.b)
        return scipy.sparse.coo_matrix((data, (rows, columns)), shape=(nb, nb))



    def load_load_profile_from_csv(self, filename):
        """
        loads a load profile from a csv file and updates the network accordingly. This also takes care of the conversion according to the base power.
        :param filename: the path to the CSV file
        """
        with open(filename, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for n, row in enumerate(reader):
                if n < self.timesteps:
                    for i, col in enumerate(row):
                        load = self.get_load(i, n)
                        load.P = float(col) / (self.networks[n].base_power * 1e6)  # convert to p.u.

    def get_projection_matrix(self, buses):
        """
        get the projection matrices for a list of buses
        :param buses:
        :return:
        """
        p_mats, p_ang, p_x = dict(), dict(), dict()
        num_vars = 0
        num_ang = 0
        num_local_only_vars = 0

        # other buses
        for bus in filter(lambda bus: (not bus.is_slack()), self.get_network().buses):
            num_vars, num_ang, num_local_only_vars = 0, 0, 0
            rows_p, cols_p, data_p = [], [], []
            rows_ang, cols_ang, data_ang = [], [], []
            rows_x, cols_x, data_x = [], [], []

            for bat in bus.bats:
                if bat.has_flags(pfnet.FLAG_VARS, pfnet.BAT_VAR_E):
                    rows_p += [num_vars]
                    cols_p += [bat.index_E]
                    data_p += [1]
                    rows_x += [num_vars]
                    cols_x += [bat.index_E]
                    data_x += [1]
                    num_vars += 1
                    num_local_only_vars += 1
                if bat.has_flags(pfnet.FLAG_VARS, pfnet.BAT_VAR_P):
                    rows_p += [num_vars + 0, num_vars + 1]
                    cols_p += [bat.index_Pc, bat.index_Pd]
                    data_p += [1, 1]
                    rows_x += [num_vars + 0, num_vars + 1]
                    cols_x += [bat.index_Pc, bat.index_Pd]
                    data_x += [1, 1]
                    num_vars += 2
                    num_local_only_vars += 2

            for gen in filter(lambda gen: gen.has_flags(pfnet.FLAG_VARS, pfnet.GEN_VAR_P), bus.gens):
                rows_p += [num_vars, ]
                cols_p += [gen.index_P, ]
                data_p += [1, ]
                rows_x += [num_vars, ]
                cols_x += [gen.index_P, ]
                data_x += [1, ]
                num_vars += 1
                num_local_only_vars += 1

            # for gen in filter(lambda gen: gen.has_flags(pfnet.FLAG_VARS, pfnet.GEN_VAR_Q), bus.gens):
            #     rows_p += [num_vars, ]
            #     cols_p += [gen.index_Q, ]
            #     data_p += [1, ]
            #     num_vars += 1
            #     num_local_only_vars += 1

            for vargen in filter(lambda vargen: vargen.has_flags(pfnet.FLAG_VARS, pfnet.VARGEN_VAR_P), bus.vargens):
                rows_p += [num_vars, ]
                cols_p += [vargen.index_P, ]
                data_p += [1, ]
                rows_x += [num_vars, ]
                cols_x += [vargen.index_P, ]
                data_x += [1, ]
                num_vars += 1
                num_local_only_vars += 1

            # for vargen in  filter(lambda gen: gen.has_flags(pfnet.FLAG_VARS, pfnet.VARGEN_VAR_Q), bus.vargens):
            #     rows_p += [num_vars, ]
            #     cols_p += [vargen.index_Q, ]
            #     data_p += [1, ]
            #     num_vars += 1
            #     num_local_only_vars += 1
            if bus.has_flags(pfnet.FLAG_VARS, pfnet.BUS_VAR_VANG):
                rows_x += [num_vars]
                cols_x += [bus.index_v_ang]
                data_x += [1]

            adj_buses = [br.bus_from for br in bus.branches_to] + [br.bus_to for br in bus.branches_from]  + [bus]
            adj_buses = filter(lambda bus: bus.has_flags(pfnet.FLAG_VARS, pfnet.BUS_VAR_VANG), adj_buses)
            adj_buses = list(filter(lambda bus: (not bus.is_slack()), adj_buses))
            adj_buses = sorted(adj_buses, key=lambda b: b.index)

            for adj_bus in adj_buses:
                rows_p += [num_vars, ]
                cols_p += [adj_bus.index_v_ang, ]
                data_p += [1, ]

                rows_ang += [num_ang, ]
                cols_ang += [num_vars, ]
                data_ang += [1, ]
                num_ang += 1
                num_vars += 1
            p_ang[bus.index] = scipy.sparse.coo_matrix((data_ang, (rows_ang, cols_ang)),
                                                       shape=(num_vars - num_local_only_vars, num_vars))
            p_mats[bus.index] = scipy.sparse.coo_matrix((data_p, (rows_p, cols_p)), shape=(num_vars, self.get_network().num_vars))
            p_x[bus.index] = scipy.sparse.coo_matrix((data_x, (rows_x, cols_x)),
                                                    shape=(num_vars, self.get_network().num_vars))

        # check matrices
        n_var = 0
        #for bus in filter(lambda bus: (not bus.is_slack()), self.get_network().buses):
        #    index = bus.index
        #    num_gens = len(list(filter(lambda gen: gen.has_flags(pfnet.FLAG_VARS, pfnet.GEN_VAR_P), bus.gens)))
        #    num_vargens = len(list(filter(lambda vargen: vargen.has_flags(pfnet.FLAG_VARS, pfnet.VARGEN_VAR_P), bus.vargens)))
        #    local_variables = num_vargens + len(bus.bats) * 3 + num_gens
        #    angles = 1 + bus.degree
        #    n_var += 1 + local_variables
            #assert (p_mats[index].shape == (local_variables + angles, self.get_network().num_vars))
            #assert (p_ang[index].shape == (angles, local_variables + angles))
        sim_p_mats, sim_p_ang, sim_p_x= dict(), dict(), dict()

        for bus in filter(lambda bus: (not bus.is_slack()), self.get_network().buses):
            sim_p_mats[bus.index] = scipy.sparse.block_diag([p_mats[bus.index] for i in range(self.timesteps)])
            #sim_p_ang[bus.index] = scipy.sparse.block_diag([p_ang[bus.index] for i in range(self.timesteps)])
            #sim_p_x[bus.index] = scipy.sparse.block_diag([p_x[bus.index] for i in range(self.timesteps)])

        return (sim_p_mats, sim_p_ang, sim_p_x)

    def get_power_balance_projection(self):
        p_pbs = dict()  # projection matrix to select the power balance from A
        for bus in filter(lambda bus: (not bus.is_slack()), self.get_network().buses):
            p_pb = scipy.sparse.coo_matrix(([1], ([0], [bus.index])),
                                                          shape=(1, self.get_num_buses()))
            # stack matrix
            p_pbs[bus.index] = scipy.sparse.block_diag([p_pb for i in range(self.timesteps)])

        return p_pbs

    def get_coupling_ang_projection(self):
        p_zs = dict()
        for bus in filter(lambda bus: (not bus.is_slack()), self.get_network().buses):
            adj_buses = []
            adj_buses += [br.bus_from for br in bus.branches_to] + [br.bus_to for br in bus.branches_from] + [bus]
            adj_buses = list(filter(lambda bus: (not bus.is_slack()), adj_buses))
            adj_buses = sorted(adj_buses, key=lambda b: b.index)

            cols, rows, data = [], [], []

            for n, adj_bus in enumerate(adj_buses):
                cols += [adj_bus.index]
                rows += [n]
                data += [1]
            p_z = scipy.sparse.coo_matrix((data, (rows, cols)), shape=(len(adj_buses), self.get_network().num_buses - 1))

            p_zs[bus.index] = scipy.sparse.block_diag([p_z for i in range(self.timesteps)])
        return p_zs


    def get_branch_projection(self):
        p_bs = dict()
        for bus in self.get_network().buses:
            cols, rows, data = [], [], []

            for n, branch in enumerate(bus.branches):
                cols += [branch.index]
                rows += [n]
                data += [1]
            p_b = scipy.sparse.coo_matrix((data, (rows, cols)), shape=(len(bus.branches), self.get_num_branches_not_on_outage()))

            p_bs[bus.index] = scipy.sparse.block_diag([p_b for i in range(self.timesteps)])
        return p_bs