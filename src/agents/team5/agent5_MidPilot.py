import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

class Agent5Mid(KartAgent):
    # AGENT DE BASE : Sa seule responsabilité est de suivre la piste avec anticipation.
    def __init__(self, env, conf, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.name = "Donkey Bombs Mid"
        self.conf = conf

        self.Kp = self.conf.pilot.brain.kp  # Force du braquage (Plus haut = plus agressif)
        self.Kd = self.conf.pilot.brain.kd   # Amortisseur (Plus haut = plus stable, moins de tremblements)

        # Constante de distance de regard du kart. 
        # Cela va nous permettre de sélectionner les noeuds du circuit devant nous afin de lisser la trajectoire.
        self.ahead_dist = self.conf.pilot.navigation.lookahead_meters

        self.last_error = 0.0   # Contient l'erreur de l'angle précédent 
        self.stuck_counter = 0  # Compte le temps passé bloqué contre un mur si kart bloqué

        self.is_rescuing = False

    def reset(self):
        self.obs, _ = self.env.reset()
        self.stuck_counter = 0
        self.last_error = 0.0
        self.is_rescuing = False

    def position_track(self, obs):
        # La fonction analyse les noeuds devant et renvoie le vecteur (x, z) du point cible situé à une distance dynamique.
        paths = obs['paths_end']

        if len(paths) == 0:
            return 0, self.ahead_dist  # par défaut si aucun noeud n'est donné dans la liste paths_end

        # On calcule la vitesse actuelle pour adapter la distance de visée.
        speed = np.linalg.norm(obs['velocity'])

        # Plus on va vite, plus on regarde loin
        lookahead = self.ahead_dist + (speed * 0.22)

        # On plafonne la visée
        lookahead = min(lookahead, 18.0)

        target_vector = paths[-1]  # Par défaut on prend le noeud le plus loin pour éviter tout bug

        # On cherche le premier point qui dépasse notre distance de visée calculée
        for p in paths:
            if p[2] > lookahead:
                target_vector = p
                break

        # On retourne l'écart latéral x et l'écart avant z du point cible
        return target_vector[0], target_vector[2]

    def compute_turning(self, x, z):
        # La fonction calcule l'angle du volant en fonction des distances (x, z).

        # On évite de diviser par zéro si le point est trop proche.
        if z < self.conf.pilot.navigation.min_dist_safety:
            z = self.conf.pilot.navigation.min_dist_safety

        # On imagine ici un triangle rectangle où x est le côté opposé et z le côté adjacent.
        # Pour simplifier, on utilise directement le ratio x / z comme erreur.
        # plus x est grand (loin du centre), plus l'angle est grand.
        error_angle = x / z

        # La dérivée mesure la vitesse à laquelle on corrige l'erreur.
        # Formule = (Erreur de maintenant) - (Erreur d'avant).
        # Elle sert d'amortisseur pour éviter les zigzags.
        error_diff = error_angle - self.last_error
        self.last_error = error_angle

        # Steering = (Force brute vers la cible * Kp) + (Freinage pour pas dépasser * Kd)
        steering = (error_angle * self.Kp) + (error_diff * self.Kd)

        # On limite entre -1 et 1
        steering_normalise = np.clip(steering, -1, 1)

        return steering_normalise

    def manage_speed(self, obs, steering):
        velocity = obs['velocity']
        speed = np.linalg.norm(velocity)

        if self.is_rescuing:
            self.stuck_counter += 1
            # On recule pendant 25 frames
            if self.stuck_counter < 25:
                accel = 0.0
                brake = True
                steering = -steering # On inverse le volant pour s'extraire
                return accel, brake, steering
            else:
                self.is_rescuing = False
                self.stuck_counter = 0

        # On commence par la vitesse d'accélération par défaut configurée.
        accel = self.conf.pilot.speed_control.default_accel
        brake = False

        # Virage standard : on ralentit un peu si le volant dépasse un certain seuil.
        if abs(steering) > self.conf.pilot.speed_control.steering_threshold:
            accel = self.conf.pilot.speed_control.cornering_accel

        # Si le volant est braqué à fond
        if abs(steering) > 0.92:
            # On réduit fortement l'accélération pour permettre au kart de pivoter sur lui-même.
            accel = 0.6
            # Si on arrive trop vite dans l'épingle, on force un coup de frein.
            if speed > 15.0:
                brake = True


        # Si on ne bouge plus alors qu'on devrait avancer, on incrémente le compteur
        if obs['distance_down_track'] > self.conf.pilot.rescue.active_after_meters and speed < self.conf.pilot.rescue.stuck_speed_limit:
            self.stuck_counter += 1
            # Si on est bloqué trop longtemps, on active le mode marche arrière
            if self.stuck_counter > self.conf.pilot.rescue.stuck_frames_limit:
                self.is_rescuing = True
                self.stuck_counter = 0
        else:
            # Si on roule, on reset le compteur de blocage.
            self.stuck_counter = 0

        return accel, brake, steering

    def choose_action(self, obs):
        target_x, target_z = self.position_track(obs)
        steering = self.compute_turning(target_x, target_z)
        accel, brake, steering = self.manage_speed(obs, steering)

        action = {
            "acceleration": accel,
            "steer": steering,
            "brake": brake,
            "drift": False, "nitro": False, "rescue": False,
            "fire": False
        }
        return action