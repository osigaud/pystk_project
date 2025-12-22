import numpy as np

class KartAgent:
    def __init__(self, env):
        self.env = env

    def step(self):
        action = self.choose_action(self.obs)
        self.obs, _, terminated, _, _ = self.env.step(action)
        self.agent_positions.append(np.array(self.env.unwrapped.world.karts[0].location))
        return terminated