import numpy as np
from agents.kart_agent import KartAgent
from utils.track_utils import compute_curvature, compute_slope


class Agent5Drift(KartAgent):
    """
    Agent 'Donkey Drift'
    Ce wrapper gère spécifiquement les phases de dérapage contrôlé (drift) dans les épingles
    Il utilise une double anticipation (regard lointain pour l'entrée, regard proche pour la sortie)
    pour optimiser la trajectoire et conserver une vitesse de sortie élevée
    """
    # AGENT DRIFT : Il gère les dérapages dans les épingles en anticipant la courbure de la piste
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        """
        Initialise l'agent de drift avec les paramètres de configuration

        Args:
            env (obj): L'environnement de simulation SuperTuxKart
            pilot_agent (obj): L'agent pilote enveloppé (MidPilot ou NitroPilot)
            conf (OmegaConf): Configuration contenant les paramètres de drift (seuils, cooldown)
            path_lookahead (int): Nombre de points de cheminement à anticiper
        """
        super().__init__(env)
        self.conf = conf
        self.pilot = pilot_agent
        self.name = "Donkey Drift"

        self.far_lookahead = self.conf.drift.far_lookahead
        self.near_lookahead = self.conf.drift.near_lookahead
        self.far_x_trigger = self.conf.drift.far_target_threshold
        self.steer_trigger = self.conf.drift.steer_trigger
        self.confirm_limit = self.conf.drift.confirmation_frames
        self.min_speed = self.conf.drift.min_speed
        self.exit_x_limit = self.conf.drift.exit_target_threshold
        self.max_dist_center = self.conf.drift.max_dist_center
        self.cooldown_limit = self.conf.drift.cooldown_frames
        self.drift_accel = self.conf.drift.drift_accel

        self.is_drifting = False      # État actuel du drift
        self.cooldown_timer = 0       # Pause forcée entre deux drifts pour stabiliser le kart
        self.turn_confirm_counter = 0 # Compteur pour valider que le virage est bien une épingle

    def reset(self):
        """Réinitialise l'état du drift et le pilote interne."""
        self.pilot.reset()
        self.is_drifting = False
        self.cooldown_timer = 0
        self.turn_confirm_counter = 0

    def choose_action(self, obs):
        """
        Arbitre l'activation du drift en analysant la courbure de la piste
        
        La méthode utilise une logique à deux niveaux :
        1. Entrée : Détectée par `far_target_x` et confirmée sur `confirm_limit` frames
        2. Sortie : Déclenchée quand `near_target_x` repasse sous un seuil ou si le kart dévie trop

        Args:
            obs (dict): Dictionnaire des observations (vitesse, chemins, position)

        Returns:
            dict: Action finale modifiée (ou non) par la logique de dérapage
        """
        # On récupère l'action calculée par le Mid Pilot
        action = self.pilot.choose_action(obs)
        paths = obs['paths_end']
        speed = np.linalg.norm(obs['velocity'])

        points = obs.get("paths_start", [])
        curvature = abs(compute_curvature(points[2:5]))

        # Sécurité si aucune donnée de piste n'est disponible
        if len(paths) == 0:
            return action


        # On interdit de redrifter immédiatement après un drift pour éviter les saccades
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            self.is_drifting = False
            self.turn_confirm_counter = 0

        # CAS : ON NE DRIFT PAS ENCORE
        elif not self.is_drifting:
            # On vérifie si la piste au loin est très décalée ou si le pilote braque déjà fort.
            if curvature > self.conf.pilot.speed_control.hairpin_curvature:
                self.turn_confirm_counter += 1 # On incrémente le compteur de confirmation
            else:
                self.turn_confirm_counter = 0 # Reset si l'intention de tourner disparaît

            # On ne drift uniquement que si le kart est dans une situation de drift favorable pendant x frames
            if self.turn_confirm_counter >= self.confirm_limit:
                if speed > self.min_speed:
                    self.is_drifting = True
                self.turn_confirm_counter = 0

        # CAS : ON EST EN TRAIN DE DRIFTER
        else:
            # On arrête si la piste devient droite OU si le kart s'éloigne trop du centre
            if curvature < 2:
                self.is_drifting = False
                self.cooldown_timer = self.cooldown_limit # Pause pour stabiliser la trajectoire

        if self.is_drifting:
            # Si le mode drift est actif, on écrase les commandes du pilote de base.
            action['drift'] = True
            action['steer'] = self.conf.drift.drift_steer_angle if curvature > self.conf.pilot.speed_control.hairpin_curvature else -self.conf.drift.drift_steer_angle
            action['acceleration'] = self.drift_accel
            action['nitro'] = False
        else:
            # Si on ne drift pas, on s'assure que le bouton drift est relâché
            action['drift'] = False

        return action