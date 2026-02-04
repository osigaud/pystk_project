import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

class Agent5(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.name = "Donkey Bombs"

        self.Kp = 6  # Force du braquage (Plus haut = plus agressif)
        self.Kd = 0.7   # Amortisseur (Plus haut = plus stable, moins de tremblements)
        
        #Constante de distance de regard du kart. 
        #Cela va nous permettre de séléctionner les noeuds du circuit à au moins 10 m devant nous afin de lisser la trajectoire
        self.ahead_dist = 9.0  

        self.last_error = 0.0   # Contient lerreur de l'angle précédent 
        self.stuck_counter = 0  # Compte le temps passé bloqué contre un mur si kart bloqué

    def reset(self):
        self.obs, _ = self.env.reset()
        self.stuck_counter = 0
        self.last_error = 0.0



    def position_track(self, obs):
        #La fonction analyse les noeuds devant et renvoie le vecteur (x, z) du point cible situé à la distance d'au moins ahead_dist = 10 m
        
        paths = obs['paths_end']
        target_vector = paths[-1]  # Par défaut on prend le noeud le plus loin pour éviter tout bug au démarrage

        if len(paths) == 0:
            return 0, self.ahead_dist  # par défaut si aucun noeud n'est donné dans la liste paths_end


        # On cherche le premier point qui dépasse notre distance de visée
        for p in paths:
            if p[2] > self.ahead_dist: # On force le kart à prendre le point qui est à une distance ahead_dist de lui pour toujour regarder au loin 
                target_vector = p
                break

        # On retourne l'écart latéral x et l'écart avant z
        return target_vector[0], target_vector[2]



    def compute_turning(self, x, z):

        # La fonction calcule l'angle du volant en fonction des distances (x, z).
        
        # On évite de diviser par zéro si le point est trop proche.
        if z < 0.5: 
            z = 0.5
        
        # On imagine ici un triangle rectangle où x est le côté opposé et z le côté adjacent.
        # On a le ratio tan(angle) = x / z
        # Pour simplifier, on utilise directement le ratio x / z comme erreur.
        # plus x est grand (loin du centre), plus l'angle est grand.
        error_angle = x / z
        
        # La dérivée mesure la vitesse à laquelle on corrige l'erreur.
        # Formule = (Erreur de maintenant) - (Erreur d'avant)
        # Si on se rapproche vite du centre, cette valeur devient négative.
        # Elle sert d'amortisseur : elle freine le volant pour éviter de dépasser le centre de la piste et de faire des zigzags.  
        error_diff = error_angle - self.last_error
        
        # On sauvegarde l'erreur actuelle pour le calcul de la prochaine frame
        self.last_error = error_angle
        
        # Steering = (Force brute vers la cible) + (Freinage pour pas dépasser)
        # steering = (Ressort * Kp) + (Amortisseur * Kd)
        steering = (error_angle * self.Kp) + (error_diff * self.Kd)
        
        # On limite entre -1 et 1
        steering_normalise = np.clip(steering, -1, 1)
        
        return steering_normalise


    def manage_speed(self, obs, steering):
        # Gère l'accélération, le freinage et le système anti-blocage.
        
        velocity = obs['velocity']
        speed = np.linalg.norm(velocity)  # Norme euclidienne du vecteur velocity
        accel = 1.0
        brake = False

        # Si on tourne fort, on ralentit pour ne pas déraper
        if abs(steering) > 0.3:
            accel = 0.5

        is_stuck = False
        # Si on est au départ (>5m) et qu'on n'avance plus (<0.5)
        if obs['distance_down_track'] > 5.0 and speed < 0.5:
            self.stuck_counter += 1
            if self.stuck_counter > 30: 
                is_stuck = True # Bloqué depuis 0.5s
        else:
            self.stuck_counter = 0

        # Si bloqué, on brake pour reculer
        if is_stuck:
            accel = 0.0
            brake = True
            steering = -steering # On inverse le volant pour se reculer

        return accel, brake, steering

    def choose_action(self, obs):
        target_x, target_z = self.position_track(obs)
        steering = self.compute_turning(target_x, target_z)
        accel, brake, steering = self.manage_speed(obs, steering)

        action = {
            "acceleration": accel,
            "steer": steering,
            "brake": brake,
            "drift": False, 
            "nitro": True, 
            "rescue": False, 
            "fire": bool(random.getrandbits(1))
        }
        return action