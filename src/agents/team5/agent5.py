import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .agent5_DriftPilot import Agent5Drift
from .agent5_MidPilot import Agent5Mid
from .agent5_BananaPilot import Agent5Banana
#from .agent5_Rescue import Agent5Rescue
from .agent5_NitroPilot import Agent5Nitro
from .agent5_ItemPilot import Agent5Item
from omegaconf import OmegaConf 
import os

class Agent5(KartAgent):
    """
    Agent principal 'Donkey Bombs' (Team 5).
    Cette classe agit comme un orchestrateur (Wrapper global) qui assemble les différents 
    modules de pilotage (Mid, Nitro, Drift, Banana, Item) selon une hiérarchie de priorité.
    """
    def __init__(self, env, path_lookahead=3):
        """
        Initialise l'agent complet en chargeant la configuration YAML et en 
        emboîtant les différents pilotes les uns dans les autres.
        """
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.name = "Donkey Bombs"
        self.isEnd = False

        # On trouve le chemin de notre fichier actuel
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # On créer le chemin /src/agent/team5/config.yaml
        config_path = os.path.join(current_dir, "config.yaml")

        # On charge le fichier conf avec ce chemin
        self.conf = OmegaConf.load(config_path)
        
        # On crée le Pilote qui suit la piste 
        self.pilot = Agent5Mid(env, self.conf, path_lookahead)
        
        # Enveloppement de l'agent de base dans l'agent de gestion du nitro
        self.nitro = Agent5Nitro(env, self.pilot, self.conf, path_lookahead)

        # On créer le pilote qui drift sur la piste
        self.drift = Agent5Drift(env, self.nitro, self.conf, path_lookahead)

        # On l'enveloppe dans l'agent qui esquive les bananes
        self.brain = Agent5Banana(env, self.drift, self.conf, path_lookahead)
        
        # On crée le pilot qui gère les items
        self.item = Agent5Item(env, self.brain, self.conf, path_lookahead)

        #self.rescue = Agent5Rescue(env, self.brain, self.conf, path_lookahead)

    def endOfTrack(self):
        """Indique si le kart a atteint la fin de la piste."""
        return self.isEnd

    def reset(self):
        """Réinitialise la chaîne complète des pilotes (Brain et couches inférieures)."""
        self.brain.reset()

    def choose_action(self, obs):
        """
        Méthode d'entrée principale du simulateur. 
        Elle délègue la décision à la couche supérieure du 'cerveau' qui 
        redescend ensuite la hiérarchie des wrappers.
        """
        return self.brain.choose_action(obs)
