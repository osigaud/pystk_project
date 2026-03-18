import numpy as np
from agents.kart_agent import KartAgent


class Agent5AvoidKart(KartAgent):

    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        super().__init__(env)

        self.conf = conf
        self.pilot = pilot_agent
        self.name = "Kart Avoidance"

        # configuration
        self.safe_distance = self.conf.avoid_karts.safe_distance    # Distance maximale à laquelle un kart est considéré dangereux
        self.max_avoid_steer = self.conf.avoid_karts.avoid_steer  # Intensité maximale de la correction de direction
        self.side_threshold = self.conf.avoid_karts.side_threshold  # Seuil latéral pour déterminer si un kart est dans notre trajectoire


        self.is_avoiding = False


    def detect_risk(self, obs):

        repulsion = 0.0 # Force de répulsion totale qui sera appliquée sur la direction
        closest_dist = 1111111 # Distance minimale détectée 

        for kart in obs["karts_position"]:

            dx = kart[0]    # Distance latérale (axe x) entre notre kart et l'autre kart
            dz = kart[2]    # Distance longitudinale (axe z) entre notre kart et l'autre kart

            # ignorer les karts derrière
            if dz < 0:  # Si la distance en avant est négative, le kart est derrière
                continue

            dist = np.sqrt(dx**2 + dz**2)   # Calcul de la distance euclidienne entre les deux karts

            # ignorer les karts trop loin
            if dist > self.safe_distance:   # Si la distance dépasse la distance de sécurité
                continue

            closest_dist = min(closest_dist, dist)  # Mise à jour de la distance minimale observée

            # influence latérale seulement si la voiture est proche de notre ligne
            if abs(dx) < self.side_threshold:   # Si le kart est proche de notre ligne de course

                # facteur de danger (plus proche = plus fort)
                danger = (self.safe_distance - dist) / self.safe_distance

                # direction opposée
                direction = -1 if dx > 0 else 1

                repulsion += direction * danger # Ajouter la contribution de ce kart à la force totale

        self.is_avoiding = closest_dist < self.safe_distance    # True si un kart est dans la zone de danger

        steer_adjust = np.clip(repulsion * self.max_avoid_steer, -1, 1)

        return self.is_avoiding, steer_adjust


    def choose_action(self, obs):

        base_action = self.pilot.choose_action(obs) # On demande d'abord au pilote de base

        has_risk, steer_adjust = self.detect_risk(obs)  # On analyse les observations pour savoir s'il faut éviter un kart

        if has_risk:

            base_action["steer"] = np.clip( # On ajoute la correction de direction calculée
                base_action["steer"] + steer_adjust,
                -1.0,
                1.0
            )

        return base_action