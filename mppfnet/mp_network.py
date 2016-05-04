import pfnet


class MPNetwork():

    network = dict()
    timesteps = 1

    def __init__(self, timesteps=1):
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



