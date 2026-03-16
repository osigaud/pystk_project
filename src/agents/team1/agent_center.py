from agents.kart_agent import KartAgent
import numpy as np

class AgentCenter(KartAgent):

    """Agent de base chargé de maintenir le kart au centre de la piste.
    
    Attributes :
    -dist (float): Distance seuil acceptée avant de considérer que l'on dévie du centre
    -ajust (float): Valeur d'ajustement pour corriger la trajectoire
    """


    def __init__(self, env, conf, path_lookahead=3):
        super().__init__(env)
        self.conf = conf
        self.dist = self.conf.dist
        self.ajust = self.conf.ajust
        self.path_lookahead = path_lookahead

    def path_ajust(self, obs, action):
        """
        Ajuste la direction du kart pour suivre le centre de la piste.

        Args:
            act (dict): Dictionnaire des actions du kart (ex: {"steer": float}).
            obs (dict): Observations de l’environnement contenant notamment
                    "paths_end" et "center_path_distance".

        Returns:
            dict: Dictionnaire des actions corrigé avec une valeur de
                "steer" comprise entre -1 et 1.
        """
        steer = action["steer"]
        center = obs["paths_end"][2]
        if (center[2] > 20 and abs(obs["center_path_distance"]) < 3) : 
            steer = 0
        elif abs(center[0]) > self.dist : 
            steer += self.ajust * center[0]
        action["steer"] = np.clip(steer, -1, 1)
        return action
    
    def choose_action(self, obs):
        """
        Applique une correction de trajectoire.

        Args:
            obs (dict): Observations de l’environnement.

        Returns:
            dict: Dictionnaire d’action corrigé.
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
        act_corr = self.path_ajust(obs, action)
        return act_corr
