import numpy as np
from agents.kart_agent import KartAgent

class Agent5Drift(KartAgent):
    # AGENT DRIFT : Il gère les dérapages dans les épingles en anticipant la courbure de la piste.
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
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
        self.pilot.reset()
        self.is_drifting = False
        self.cooldown_timer = 0
        self.turn_confirm_counter = 0

    def choose_action(self, obs):
        # On récupère l'action calculée par le Mid Pilot
        action = self.pilot.choose_action(obs)
        paths = obs['paths_end']
        speed = np.linalg.norm(obs['velocity'])

        # Sécurité si aucune donnée de piste n'est disponible
        if len(paths) == 0:
            return action

        # On regarde très loin pour détecter l'entrée d'une épingle avant d'y être
        far_target_x = paths[-1][0]
        for p in paths:
            if p[2] > self.far_lookahead:
                far_target_x = p[0]
                break

        # On regarde plus près pour anticiper la sortie du virage
        near_target_x = paths[-1][0]
        for p in paths:
            if p[2] > self.near_lookahead:
                near_target_x = p[0]
                break

        # On interdit de redrifter immédiatement après un drift pour éviter les saccades
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            self.is_drifting = False
            self.turn_confirm_counter = 0

        # CAS : ON NE DRIFT PAS ENCORE
        elif not self.is_drifting:
            # On vérifie si la piste au loin est très décalée ou si le pilote braque déjà fort.
            if abs(far_target_x) > self.far_x_trigger or abs(action['steer']) > self.steer_trigger:
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
            dist_to_center = abs(paths[0][0])
            if abs(near_target_x) < self.exit_x_limit or dist_to_center > self.max_dist_center:
                self.is_drifting = False
                self.cooldown_timer = self.cooldown_limit # Pause pour stabiliser la trajectoire

        if self.is_drifting:
            action['drift'] = True
            action['steer'] = self.conf.drift.drift_steer_angle if far_target_x > 0 else -self.conf.drift.drift_steer_angle
            action['acceleration'] = self.drift_accel
            action['nitro'] = False
        else:
            action['drift'] = False

        return action