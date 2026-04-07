import numpy as np
from agents.kart_agent import KartAgent

class Agent5Rescue(KartAgent):
    """
    Agent 'Donkey Bombs Rescue'
    Ce wrapper surveille si le kart est bloqué contre un obstacle.
    Si le kart ne progresse plus, il déclenche une manoeuvre de marche arrière
    prioritaire pour dégager le véhicule.
    """
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        super().__init__(env)
        self.pilot = pilot_agent
        self.conf = conf

        self.stuck_counter = 0
        self.rescue_counter = 0
        self.last_distance = 0.0
        self.is_rescuing = False
        self.rescue_duration = self.conf.pilot.rescue.rescue_duration

    def reset(self):
        """Réinitialise les compteurs de blocage."""
        self.pilot.reset()
        self.stuck_counter = 0
        self.rescue_counter = 0
        self.last_distance = 0.0
        self.is_rescuing = False

    def choose_action(self, obs):
        """
        Détecte le blocage et applique la marche arrière si nécessaire.
        """
        dist_now = float(obs['distance_down_track'].item())

        action = self.pilot.choose_action(obs)

        # Phase de rescue en cours
        if self.is_rescuing:
            self.rescue_counter += 1
            if self.rescue_counter < self.rescue_duration:
                return {
                    "acceleration": 0.0,
                    "steer": -action["steer"],
                    "brake": True,
                    "drift": False,
                    "nitro": False,
                    "rescue": False,
                    "fire": False,
                }
            else:
                self.is_rescuing = False
                self.rescue_counter = 0
                self.stuck_counter = 0
                self.last_distance = dist_now

        # Détection de blocage si on reste bloqué pendant un certain temps 
        elif dist_now > self.conf.pilot.rescue.active_after_meters:
            delta = abs(dist_now - self.last_distance)

            if delta < self.conf.pilot.rescue.stuck_diff_dist_epsilon:
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0

            self.last_distance = dist_now

            if self.stuck_counter > self.conf.pilot.rescue.stuck_frames_limit:
                self.is_rescuing = True
                self.rescue_counter = 0
                self.stuck_counter = 0

        return action