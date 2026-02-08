import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")

from agents.team3.AvoidItems import AvoidItems

class FireItems():
    
    def choose_action(self, obs):
        action = AvoidItems.choose_action(self, obs)

        

        
        return action