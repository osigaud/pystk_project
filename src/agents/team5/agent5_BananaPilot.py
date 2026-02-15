import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent


class Agent5Banana(KartAgent):
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.pilot = pilot_agent
        self.name = "Donkey Bombs Banana"
        self.conf = conf

    def reset(self):
        self.pilot.reset()

    def detect_banana(self, obs):
        '''La fonction detecte la banane la plus proche et devant le kart, décide si on doit l'éviter et par quel coté on doit l'éviter.
        Cette fonction renvoie : si le wrapper prend le contrôle de l'agent ou pas, un float correspondant au steering, un float correspondant à l'acceleration'''

        items_pos = np.array(obs["items_position"])
        items_type = obs["items_type"]

        if items_type is None or len(items_type) == 0:
            return False, 0.0, 1.0 #Il n'y a pas d'item sur la map, le wrappern ne prend pas le controle

        index_bananas = [i for i, j in enumerate(items_type) if j == 1]
        bananas = items_pos[index_bananas]

        if len(index_bananas) == 0:
            return False, 0.0, 1.0 #Il n'y a pas banane sur la map, le wrapper ne prend pas le controle


        for b in bananas:
            x = b[0]
            z = b[2]

            if 0 < z < self.conf.banana.detection.max_distance and abs(x) < self.conf.banana.detection.safety_width:
                # Évitement
                if x < 0:
                    steering = self.conf.banana.avoidance.steering_force
                else :
                    steering = -self.conf.banana.avoidance.steering_force
                accel = self.conf.banana.avoidance.acceleration

                return True, steering, accel #Le wrapper prend le controle du kart, tourne soit à gauche soit à droite, accelère en fonction de la variable accel

        return False, 0.0, 1.0 #Si il n'y a pas de banane proche et devant le kart le wrapper ne prend pas le controle

    def choose_action(self, obs):
        '''La fonction choisit quelles actions le kart doit choisir en fonction des observation de detect_banana() et renvoie les actions choisies'''
        danger, steer, accel = self.detect_banana(obs)
        if danger:
            return {
                "acceleration": accel,
                "steer": steer,
                "drift": False, 
                "nitro": False, 
                "rescue": False,
                "brake" : False, 
                "fire": False
            }
        return self.pilot.choose_action(obs)