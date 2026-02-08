import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")

from agents.team3.TakeItems import TakeItems

class AvoidItems():
    
    def choose_action(self, obs):
        action = TakeItems.choose_action(self, obs)

        target = obs["paths_end"][0] #return a vector [x,y,z]
        x = target[0] #Extracting the x

        # évitement items dangereux
        next_item = obs["items_position"][0]
        item_x_axis = next_item[0]
        item_z_axis = next_item[2]
        item = obs["items_type"][0]

        if item == cfg.track_items.danger_type and item_z_axis < cfg.track_items.avoidance_distance and abs(item_x_axis) < cfg.track_items.avoidance_width:
            x = -cfg.steering.avoidance_offset if item_x_axis > 0 else cfg.steering.avoidance_offset

        action["steer"] = x

        
        return action