import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")

from agents.team3.Pilot import Pilot

class TakeItems():
    
    def choose_action(self, obs):
        action = Pilot.choose_action(self, obs)

        target = obs["paths_end"][0] #return a vector [x,y,z]
        x = target[0] #Extracting the x

        # # items
        # items_pos = obs["items_position"]
        # items_type = obs["items_type"]
        # closest_dist = np.inf
        # bonus_x = None
        
        # for pos, typ in zip(items_pos, items_type):
        #     if typ in cfg.track_items.collectible_types:
        #         dist_z = pos[2]
        #         dist_x = pos[0]
        #         if 0 < dist_z < cfg.track_items.detection_distance and abs(dist_x) < cfg.steering.max_track_offset:
        #             if dist_z < closest_dist:
        #                 closest_dist = dist_z
        #                 bonus_x = dist_x

        # if bonus_x is not None:
        # 	x = bonus_x

        
        return action