import os
import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .agent5_DriftPilot import Agent5Drift
from .agent5_MidPilot import Agent5Mid
from .agent5_F1 import Agent5F1
from .agent5_BananaPilot import Agent5Banana
from .agent5_NitroPilot import Agent5Nitro
from .agent5_UseItems import Agent5UseItems
from .agent5_AvoidKart import Agent5AvoidKart
from omegaconf import OmegaConf
from .agent5_RescuePilot import Agent5Rescue


class Agent5(KartAgent):
    """
    Orchestrateur (Wrapper global) assemblant les différents modules de pilotage
    selon la hiérarchie de priorité suivante :
    """

    def __init__(self, env, path_lookahead=3, cfg=None):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.name = "Donkey Bombs"
        self.isEnd = False
        self.skin = 'tux'

        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config_opti.yaml")
        self.conf = OmegaConf.load(config_path)

        if cfg is not None:
            self.conf = cfg

        # 1. Pilote de base : suit la piste
        self.pilot = Agent5F1(env, self.conf, path_lookahead)

        # 2. Utilisation des items (branché sur nitro) 

        self.use_items = Agent5UseItems(env, self.pilot, self.conf, path_lookahead)

        # 3. Gestion du nitro
        self.nitro = Agent5Nitro(env, self.use_items, self.conf, path_lookahead)

        # 4. Évitement des karts adverses (branché sur use_items)
        #self.avoidkart = Agent5AvoidKart(env, self.nitro, self.conf, path_lookahead)

        #self.drift = Agent5Drift(env, self.avoidkart, self.conf, path_lookahead)


        # 5. Esquive des bananes
        self.banana = Agent5Banana(env, self.nitro, self.conf, path_lookahead)

        # 6. Gestion du blocage / rescue (couche la plus haute)
        self.brain = Agent5Rescue(env, self.banana, self.conf, path_lookahead)

    def endOfTrack(self):
        return self.isEnd

    def reset(self):
        """Réinitialise toute la chaîne des pilotes."""
        self.brain.reset()

    def choose_action(self, obs):
        """Délègue la décision à la couche supérieure (brain)."""
        return self.brain.choose_action(obs)