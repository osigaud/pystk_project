from .agent_base import AgentInit
from .agent_base import DIST, AJUST
import numpy as np


class AgentCenter(AgentInit):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env, path_lookahead)
        self.dist = DIST
        self.ajust = AJUST

    def path_ajust(self, act, obs):
        """
        Paramètres : obs, act (dict)
        Renvoie : act (dict), dictionnaire des actions du kart corrigé pour suivre le centre de la piste
        """
        steer = act["steer"]
        center = obs["paths_end"][2]
        if (center[2] > 20 and abs(obs["center_path_distance"]) < 3) : 
            steer = 0
        elif abs(center[0]) > self.dist : 
            steer += self.ajust * center[0]
        act["steer"] = np.clip(steer, -1, 1)
        return act
    
    def choose_action(self, obs):
        """
        Paramètres : obs
        Renvoie : act (dict), le dictionnaire d'action après correction
        """
        act = super().choose_action(obs)
        act_corr = self.path_ajust(act, obs)
        return act_corr
