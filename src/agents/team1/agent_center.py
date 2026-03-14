from agents.kart_agent import KartAgent
import numpy as np

class AgentCenter(KartAgent):
    def __init__(self, env, conf, path_lookahead=3):
        super().__init__(env)
        self.conf = conf
        self.dist = self.conf.dist
        self.ajust = self.conf.ajust
        self.path_lookahead = path_lookahead

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
        action = {
            "acceleration": 0,
            "steer": 0,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }
        act_corr = self.path_ajust(action, obs)
        return act_corr
