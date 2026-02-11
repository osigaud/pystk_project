import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")


class Pilot():
    
    def choose_action(self, obs):

        target = np.array(obs["paths_start"][self.path_lookahead])
        x = target[0]
        z = target[2]
        steer = (x / z) * 1.5
        items_pos = np.array(obs["items_position"])
        items_type = np.array(obs["items_type"])
        if len(items_pos) > 0:
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
        speed = (((obs["velocity"][0])**2) + ((obs["velocity"][2])**2))**0.5
        brake = False
        nitro = False
        fire = False
        if abs(steer) > 1.0:
            acceleration = 0.3
        else:
            acceleration = 1.0
        if abs(steer) < 0.1 and speed < 20.0:
            nitro = True
        if (speed < 2.0):
            self.time_blocked += 1 
            if (self.time_blocked > 10):
                acceleration = 0.0
                brake = True
                steer = -steer
        if (self.time_blocked == 20):
            self.time_blocked = 0 

        action = {
            "acceleration": acceleration,
            "steer": steer,
            "brake": brake,
            "drift": False,
            "nitro": nitro,
            "rescue": False,
            "fire": fire,
        }
        return action
