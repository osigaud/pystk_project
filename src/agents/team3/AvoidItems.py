import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")

from agents.team3.TakeItems import TakeItems

class AvoidItems():
    
    def choose_action(self, obs):
        action = TakeItems.choose_action(self, obs)


        
        return action
