from agents.kart_agent import KartAgent
import random 

import numpy as np
import random
import math
from omegaconf import OmegaConf

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

from pathlib import Path

#chemin du fichier de configuration
path_conf = Path(__file__).resolve().parent
path_conf = str(path_conf) + '/configFIleTastyCrousteam.yaml'
#importation du fichier de configuration
conf = OmegaConf.load(path_conf)

#définition des variables qui viennent du fichier de configuration
DIST = conf.dist
AJUST = conf.ajust
ECARTPETIT = conf.ecartpetit
ECARTGRAND = conf.ecartgrand
MSAPETIT = conf.msapetit
MSAGRAND = conf.msagrand
ACCEL_LIGNE_DROITE = conf.accel_ligne_droite
FREIN_VIRAGE = conf.frein_virage
ACCEL_VIRAGE = conf.accel_virage
DIST_SEGMENT = conf.dist_segment

#autres variables qu'on utilise dans le code 
BONUS = [0, 2, 3]
OBSTACLES = [1, 4]

#template de base d'Agent, mouvements aléatoires, initialisation des variables
class AgentInit(KartAgent):
    #variables à définir dans le fichier de configuration : 
    #   - accélération par défaut
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Tasty Crousteam"

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        acceleration = random.random()
        steering = random.random()
        action = {
            "acceleration": 0,
            "steer": 0,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }
        return action
