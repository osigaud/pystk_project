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

        self.ahead_dist = self.conf.pilot.navigation.lookahead_meters
        self.lookahead_factor = self.conf.pilot.navigation.lookahead_speed_factor
        self.lookahead_max = self.conf.pilot.navigation.lookahead_max


    def reset(self):
        self.pilot.reset()

    def position_track(self, obs):
        # La fonction analyse les noeuds devant et renvoie le vecteur (x, z) du point cible situé à une distance dynamique.
        paths = obs['paths_end']

        if len(paths) == 0:
            return 0, self.ahead_dist  # par défaut si aucun noeud n'est donné dans la liste paths_end

        # On calcule la vitesse actuelle pour adapter la distance de visée.
        speed = np.linalg.norm(obs['velocity'])

        # Plus on va vite, plus on regarde loin
        lookahead = self.ahead_dist + (speed * self.lookahead_factor)

        # On plafonne la visée
        lookahead = min(lookahead, self.lookahead_max)

        target_vector = paths[-1]  # Par défaut on prend le noeud le plus loin pour éviter tout bug

        # On cherche le premier point qui dépasse notre distance de visée calculée
        for p in paths:
            if p[2] > lookahead:
                target_vector = p
                break

        # On retourne l'écart latéral x et l'écart avant z du point cible
        return target_vector[0], target_vector[2]


    def detect_banana(self, obs):
        items_pos = np.array(obs["items_position"])
        items_type = obs["items_type"]

        if items_type is None or len(items_type) == 0:
            return False, 0.0, 1.0

        index_bananas = [i for i, j in enumerate(items_type) if (j == 1 or j == 4 or j == 5)]
        bananas = items_pos[index_bananas]

        if len(index_bananas) == 0:
            return False, 0.0, 1.0

        node_x, node_z = self.position_track(obs)

        denominator = np.sqrt(node_x**2 + node_z**2)

        if denominator < 1e-6:
            return False, 0.0, 1.0

        for b in bananas:
            x_b = b[0]
            z_b = b[2]

            if 0 < z_b < self.conf.banana.detection.max_distance:

                # distance perpendiculaire entre le point de la banane et la droite séparant le kart et le noeud
                d = abs(node_x * z_b - node_z * x_b) / denominator

                if d < self.conf.banana.detection.safety_width:
                    if x_b < 0:
                        steering = self.conf.banana.avoidance.steering_force 
                    else:
                        steering = -self.conf.banana.avoidance.steering_force
                    accel = self.conf.banana.avoidance.acceleration
                    return True, steering, accel

        return False, 0.0, 1.0


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
                "fire": True
            }
        return self.pilot.choose_action(obs)