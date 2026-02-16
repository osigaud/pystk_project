import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent


class Agent5Nitro(KartAgent):
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.pilot = pilot_agent
        self.name = "Donkey Bombs Nitro"
        self.conf = conf

    def reset(self):
        self.pilot.reset()

    def detect_nitro(self, obs):

        # On récupère l'action du pilot pour analyser le steer
        action_pilot = self.pilot.choose_action(obs)

        steer = action_pilot["steer"]
        accel = action_pilot["acceleration"]

        # Vérifier si la valeur absolue du steer est inférieure au seuil configuré
        if abs(steer) < self.conf.nitro.detection.steering_threshold_nitro:

            # Vérifier trois conditions supplémentaires pour utiliser le nitro :
            # 1. L'accélération est supérieure au minimum configuré (kart accélère)
            # 2. Le frein n'est pas activé par le pilot
            # 3. Le dérapage (drift) n'est pas activé par le pilot
            # 4. L'energie est superieur a min_energie
            if accel > self.conf.nitro.detection.min_acceleration and not action_pilot["brake"] and not action_pilot["drift"] and (obs["energy"] > self.conf.nitro.detection.min_energy) :
                
                return True, steer, accel, True

        return False, steer, accel, False


    def choose_action(self, obs):

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