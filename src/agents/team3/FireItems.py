import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")

from agents.team3.AvoidItems import AvoidItems

class FireItems():
    
    def choose_action(self, obs):
        action = AvoidItems.choose_action(self, obs)
        
        target = np.array(obs["paths_start"][self.path_lookahead]) 
        x = target[0]
        z = target[2]

        if (x<1.0):
        	action["fire"]= True

        
        return action