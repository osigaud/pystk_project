import math
import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")

from agents.team3.Pilot import Pilot

class FireItems():
    
    def choose_action(self, obs):
        action = Pilot.choose_action(self, obs)
        
        fire = False
        karts = np.array(obs["karts_position"])
        for i in range(len(karts)):
            kart_x = karts[i][0]
            kart_z = karts[i][2]
            if 0 < kart_z < 25.0 and abs(kart_x) < 1.5:
                fire = True
                break

        
        return action