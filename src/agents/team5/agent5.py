import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

class Agent5(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.name = "Donkey Bombs"

        # Réglages
        self.Kp = 4                 # Force du braquage (Plus haut = plus agressif)
        self.Kd = 0.6               # Amortisseur (Plus haut = plus stable, moins de tremblements)
        self.LOOKAHEAD_DIST = 10.0  # Distance de visée en mètres (Regarder loin)

        # Variable interne
        self.last_error = 0.0   # Mémorise l'angle précédent pour le calcul dérivé
        self.stuck_counter = 0  # Compte le temps passé bloqué contre un mur

    def reset(self):
        self.obs, _ = self.env.reset()
        self.stuck_counter = 0
        self.last_error = 0.0

    # FONCTION DE VISION (Où le kart doit aller ?)
    def position_track(self, obs):
        # Scanne la route devant et renvoie le vecteur (x, z) du point cible situé à la distance LOOKAHEAD_DIST.
        
        paths = obs['paths_end']
        target_vector = paths[-1] # Par défaut le plus loin

        # SÉCURITÉ : Si la liste est vide, on renvoie 0,0
        if len(paths) == 0:
            return 0.0, 10.0 # On fait semblant que la cible est tout droit à 10m

        # On cherche le premier point qui dépasse notre distance de visée
        for p in paths:
            if p[2] > self.LOOKAHEAD_DIST: # On force le kart à prendre le point qui est à une distance LOOKAHEAD_DIST de lui pour toujour regarder au loin 
                target_vector = p
                break

        # On retourne juste X (écart latéral) et Z (distance devant)
        return target_vector[0], target_vector[2]


    # FONCTION DE BRAQUAGE
    def compute_turning(self, x, z):
        """
        Calcule l'angle du volant en fonction de la cible (x, z).
        """
        
        # On évite de diviser par zéro si le point est trop proche.
        if z < 0.5: z = 0.5
        
        # CALCUL DE L'ERREUR
        # Imagine un triangle rectangle où x est le côté opposé et z le côté adjacent.
        # Mathématiquement tan(angle) = x / z.
        # Pour simplifier, on utilise directement le ratio x / z comme Angle à atteindre.
        # C'est notre erreur : Plus x est grand (loin du centre), plus l'angle est grand.
        error_angle = x / z
        
        # CALCUL DE LA DÉRIVÉE
        # La dérivée mesure la VITESSE à laquelle on corrige l'erreur.
        # Formule : (Erreur de maintenant) - (Erreur d'avant)
        # Si on se rapproche vite du centre, cette valeur devient négative.
        # Elle sert d'AMORTISSEUR : elle freine le volant pour éviter de dépasser le centre de la piste et de faire des zigzags.  
        derivative = error_angle - self.last_error
        
        # On sauvegarde l'erreur actuelle pour le calcul de la prochaine frame
        self.last_error = error_angle
        
        # FORMULE FINALE
        # Steering_raw = (Force brute vers la cible) + (Freinage pour pas dépasser)
        # steering_raw = (Ressort * Kp) + (Amortisseur * Kd)
        steering_raw = (error_angle * self.Kp) + (derivative * self.Kd)
        
        # On limite entre -1 et 1
        steering = np.clip(steering_raw * 1, -1, 1)
        
        return steering


    # FONCTION PÉDALES 
    def manage_speed_rescue(self, obs, steering):
        # Gère l'accélération, le freinage et le système anti-blocage.
        
        velocity = obs['velocity']
        speed = np.linalg.norm(velocity)
        accel = 1.0
        brake = False

        # Si on tourne fort, on ralentit pour ne pas déraper
        if abs(steering) > 0.3:
            accel = 0.5

        is_stuck = False

        # Si on est au départ (>5m) et qu'on n'avance plus (<0.5)
        if obs['distance_down_track'] > 5.0 and speed < 0.5:
            self.stuck_counter += 1
            if self.stuck_counter > 30: is_stuck = True # Bloqué depuis 0.5s
        else:
            self.stuck_counter = 0

        # Si bloqué, on écrase tout pour reculer
        if is_stuck:
            accel = 0.0
            brake = True
            steering = -steering # On inverse le volant pour se dégager

        return accel, brake, steering

    def choose_action(self, obs):
        # Récupérer les coordonnées de la cible
        target_x, target_z = self.position_track(obs)

        # Calculer le steering du volant
        steering = self.compute_turning(target_x, target_z)

        # Calculer vitesse et gérer les blocages (On récupère steering car la marche arrière peut l'inverser)
        accel, brake, steering = self.manage_speed_rescue(obs, steering)

        # ENVOI
        action = {
            "acceleration": accel,
            "steer": steering,
            "brake": brake,
            "drift": False, "nitro": False, "rescue": False, "fire": False
        }
        return action