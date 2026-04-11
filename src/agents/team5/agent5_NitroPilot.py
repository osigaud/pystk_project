import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent


class Agent5Nitro(KartAgent):
    """
    Agent 'Donkey Bombs Nitro'.
    Ce wrapper gère l'utilisation optimale du boost (Nitro). 
    Il agit comme une couche décisionnelle supplémentaire qui surveille l'état du kart 
    et l'énergie disponible pour injecter de la puissance en ligne droite
    """
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        """
        Initialise le module Nitro.

        Args:
            env (obj): L'environnement de simulation SuperTuxKart
            pilot_agent (obj): L'agent pilote enveloppé (MidPilot)
            conf (OmegaConf): Objet de configuration contenant les seuils d'activation du nitro
            path_lookahead (int): Nombre de points de cheminement à anticiper
        """
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.pilot = pilot_agent
        self.name = "Donkey Bombs Nitro"
        self.conf = conf
        self.using_nitro = False

    def reset(self):
        """Réinitialise l'état du Nitro et du pilote interne."""
        self.pilot.reset()
        self.using_nitro = False

    def detect_nitro(self, obs):
        """
        Analyse si les conditions sont favorables au déclenchement du Nitro
        Une fois activé, le Nitro est maintenu jusqu'à épuisement de la jauge (energy > 0)

        Args:
            obs (dict): Dictionnaire contenant les observations de l'environnement (énergie, etc.)

        Returns:
            tuple: (use_nitro, steer, accel, nitro_active)
                - use_nitro (bool): True si le nitro doit être utilisé à cette frame
                - steer (float): Valeur de braquage récupérée du pilote
                - accel (float): Valeur d'accélération récupérée du pilote
                - nitro_active (bool): État de la commande nitro pour le dictionnaire d'action
        """
        # On récupère l'action du pilot pour analyser le steer
        action_pilot = self.pilot.choose_action(obs)

        steer = action_pilot["steer"]
        accel = action_pilot["acceleration"]
        energy = obs["energy"]
        points = obs.get("paths_start", [])
        curvature = abs(compute_curvature(points[2:5]))

        if self.using_nitro: # Si on utilise le Nitro et que l’énergie est supérieure à 0, on va tout utiliser.
            if energy > 0:
                return True, steer, accel, True
            else:
                self.using_nitro = False
                return False, steer, accel, False
        # Vérifier si la valeur absolue du steer est inférieure au seuil configuré
        if curvature < 4:

            # Vérifier trois conditions supplémentaires pour utiliser le nitro :
            # 1. L'accélération est supérieure au minimum configuré (kart accélère)
            # 2. Le frein n'est pas activé par le pilot
            # 3. Le dérapage (drift) n'est pas activé par le pilot
            if accel > self.conf.nitro.detection.min_acceleration and not action_pilot["brake"] and not action_pilot["drift"]:

                self.using_nitro = True
                return True, steer, accel, True

        return False, steer, accel, False


    def choose_action(self, obs):
        """
        Arbitre entre l'action boostée et l'action normale du pilote

        Args:
            obs (dict): Dictionnaire contenant les observations de l'environnement

        Returns:
            dict: Dictionnaire d'actions final envoyé au simulateur
        """
        # La fonction choisit quelles actions le kart doit choisir en fonction des observation de detect_nitro()
        use_nitro, steer, accel, nitro = self.detect_nitro(obs)

        if use_nitro:
            return {
                "acceleration": accel,
                "steer": steer,
                "drift": False,
                "nitro": nitro,
                "rescue": False,
                "brake": False,
                "fire": False
            }

        return self.pilot.choose_action(obs)