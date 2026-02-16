import numpy as np
from agents.kart_agent import KartAgent

class Agent5Drift(KartAgent):
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        super().__init__(env)
        self.conf = conf
        self.pilot = pilot_agent
        self.path_lookahead = path_lookahead
        self.name = "Donkey Drift"

