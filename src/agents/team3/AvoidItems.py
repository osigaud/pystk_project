import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")

from agents.team3.TakeItems import TakeItems

class AvoidItems():
    
    def choose_action(self, obs):
        action = TakeItems.choose_action(self, obs)

        target = np.array(obs["paths_start"][self.path_lookahead]) 
        x = target[0]
        z = target[2]

        steer = (x / z) * 1.5
        
        items_pos = np.array(obs["items_position"])
        items_type = np.array(obs["items_type"])
        for i in range(len(items_pos)):
            item_pos = items_pos[i]
            item_type = items_type[i]
            if (item_type == 1 or item_type == 4):
                item_x = item_pos[0]
                item_z = item_pos[2]
                if (0 < item_z < 30 and abs(item_x) < 3.0):
                    if item_x <= 0:
                        steer += 0.5
                    else:
                        steer -= 0.5

        action["steer"] = steer

        
        return action
