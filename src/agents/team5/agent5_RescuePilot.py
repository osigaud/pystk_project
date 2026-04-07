import numpy as np
from agents.kart_agent import KartAgent

class Agent5Rescue(KartAgent):
    """
    Agent 'Donkey Bombs Rescue'
    Ce wrapper surveille si le kart est bloqué contre un obstacle
    Si le kart ne progresse plus, il déclenche une manoeuvre de marche arrière
    prioritaire pour dégager le véhicule
    """
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        """
        Initialise le module de sauvetage

        Args:
            env (obj): L'environnement de simulation
            pilot_agent (obj): L'agent pilote enveloppé (celui qui a la priorité juste en dessous)
            conf (OmegaConf): Configuration contenant les seuils de blocage et durée de recul
            path_lookahead (int): Nombre de points de cheminement à anticiper
        """
        super().__init__(env)
        self.pilot = pilot_agent
        self.conf = conf

        self.stuck_counter = 0
        self.last_distance = 0.0
        self.is_rescuing = False
        self.rescue_duration = self.conf.pilot.rescue.rescue_duration

    def reset(self):
        """Réinitialise les compteurs de blocage"""
        self.pilot.reset()
        self.stuck_counter = 0
        self.last_distance = 0.0
        self.is_rescuing = False

    def choose_action(self, obs):
        """
        Détecte le blocage et applique la marche arrière si nécessaire

        Args:
            obs (dict): Observations courantes

        Returns:
            dict: Action de recul si bloqué, sinon action du pilote inférieur
        """
        dist_now = obs['distance_down_track']
        action = self.pilot.choose_action(obs)

        # LOGIQUE DE DÉTECTION
        if obs["attachment"] == 0 :
            if self.is_rescuing:
                self.stuck_counter += 1
                if self.stuck_counter < self.rescue_duration:
                    # Manoeuvre de secours : On recule en inversant le volant
                    return {
                        "acceleration": 0.0,
                        "steer": -action["steer"],
                        "brake": True,
                        "drift": False, "nitro": False, "rescue": False, "fire": False
                    }
                else:
                    self.is_rescuing = False
                    self.stuck_counter = 0
                    self.last_distance = dist_now

        # Vérification si on est bloqué (après la ligne de départ)
        elif dist_now > self.conf.pilot.rescue.active_after_meters:
            if abs(dist_now - self.last_distance) < self.conf.pilot.rescue.stuck_diff_dist_epsilon:
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0

            self.last_distance = dist_now

            if self.stuck_counter > self.conf.pilot.rescue.stuck_frames_limit:
                self.is_rescuing = True
                self.stuck_counter = 0

        return action