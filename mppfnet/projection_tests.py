import unittest
from .mp_network import MPNetwork
import scipy
class ProjectionTest(unittest.TestCase):
    def test_projection_constraints(self):
        mp = MPNetwork(timesteps=168)
        mp.load("../data/case32.art")
        p_pbs = mp.get_power_balance_projection()
        for p in p_pbs.values():
            self.assertEqual(p.nnz, mp.timesteps)


    def test_coupling_projection(self):
        mp = MPNetwork(timesteps=168)
        mp.load("../data/case32.art")
        p_zs = mp.get_coupling_ang_projection()
        for bus in mp.get_network().buses:
            if bus.is_slack():
                self.assertEqual(p_zs[bus.index].nnz, mp.timesteps * bus.degree)
                self.assertEqual(p_zs[bus.index].shape,
                             ((bus.degree) * mp.timesteps, mp.get_num_buses() * mp.timesteps))

            else:
                self.assertEqual(p_zs[bus.index].nnz, mp.timesteps * (bus.degree + 1))
                self.assertEqual(p_zs[bus.index].shape, ((bus.degree + 1) * mp.timesteps, mp.get_num_buses() * mp.timesteps))
        self.assertEqual(len(p_zs), mp.get_num_buses())

if __name__ == '__main__':
    unittest.main()
