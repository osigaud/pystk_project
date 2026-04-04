import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

class Agent5F1(KartAgent):
    """
    Agent de base 'Donkey Bombs Mid'
    Responsable du suivi de piste principal en utilisant un contrôle Proportionnel-Dérivé
    et une gestion d'anticipation dynamique basée sur la vitesse du kart
    """
    # AGENT DE BASE : Sa seule responsabilité est de suivre la piste avec anticipation
    def __init__(self, env, conf, path_lookahead=3):
        """
        Initialise l'agent avec les paramètres de configuration YAML.
        Définit les gains du contrôleur (Kp, Kd) et les distances de visée (lookahead)

        Args:
            env (obj): L'environnement de simulation SuperTuxKart
            conf (OmegaConf): Objet de configuration chargé depuis le YAML
            path_lookahead (int): Nombre de points de cheminement à anticiper (défaut: 3)
        """
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.name = "Donkey Bombs Mid"
        self.conf = conf

        self.ahead_dist = self.conf.pilot.navigation.lookahead_meters
        self.K = self.conf.pilot.navigation.k
        self.locked_node = False
        self.node_idx = -1
        self.last_error = 0.0   # Contient l'erreur de l'angle précédent 
        self.lookahead_factor = self.conf.pilot.navigation.lookahead_speed_factor
        self.lookahead_max = self.conf.pilot.navigation.lookahead_max
        self.hairpin_threshold = self.conf.pilot.speed_control.hairpin_threshold
        self.hairpin_accel = self.conf.pilot.speed_control.hairpin_accel
        self.hairpin_brake_speed = self.conf.pilot.speed_control.hairpin_brake_speed


    def reset(self):
        """Réinitialise les variables d'état de l'agent au début d'une course"""
        self.obs, _ = self.env.reset()
        self.last_error = 0.0
        self.locked_node = False
        self.node_idx = -1




    def position_track(self, obs):
            """
            Analyse les noeuds devant et renvoie le vecteur (x, z) du point cible situé à une distance dynamique
            La distance de visée (lookahead) augmente proportionnellement à la vitesse

            Args:
                obs (dict): Dictionnaire contenant les observations de l'environnement

            Returns:
                tuple: (target_vector[0], target_vector[2])
                    - target_vector[0] (float): Écart latéral (x) du point cible
                    - target_vector[2] (float): Distance frontale (z) du point cible
            """
            # La fonction analyse les noeuds devant et renvoie le vecteur (x, z) du point cible situé à une distance dynamique
            paths = obs['paths_end']

            if len(paths) == 0:
                return 0, self.ahead_dist  # par défaut si aucun noeud n'est donné dans la liste paths_end

            # On calcule la vitesse actuelle pour adapter la distance de visée.
            speed = np.linalg.norm(obs['velocity'])

            # Plus on va vite, plus on regarde loin
            lookahead = self.ahead_dist + (speed * self.lookahead_factor)

            # On plafonne la visée
            lookahead = min(lookahead, self.lookahead_max)

            dist = tuple()
            boolen_locked = self.locked_node
            if boolen_locked:
                node_vect = obs["paths_end"][self.node_idx]
                dist = (node_vect[0], node_vect[2])
            else:
                
                target_vector = paths[-1]  # Par défaut on prend le noeud le plus loin pour éviter tout bug

                # On cherche le premier point qui dépasse notre distance de visée calculée
                for i, p in enumerate(paths):
                    if p[2] > lookahead:
                        self.node_idx = i
                        target_vector = p
                        self.locked_node = True
                        break

                # On retourne l'écart latéral x et l'écart avant z du point cible
                dist = (target_vector[0], target_vector[2])
            
            x, z = dist
            if (z <= 0):
                self.locked_node = False

            return x, z


    def compute_turning_pps(self, obs, target_x, target_z):

        l_squared = target_x**2 + target_z**2

        gamma =  self.K * (2*target_x)/(l_squared + 1e-5)
        steering = np.clip(np.arctan(gamma), -1, 1)

        width_path = obs["paths_width"][0]
        near_node = obs["paths_end"][0]
        x_nn = near_node[0]

        dist_wall = (width_path/2) - np.abs(x_nn)

        #print("largeur demi wall : ", width_path/2)
        #print("Abs distance kart - mur : ", dist_wall)
        return steering




    def manage_speed(self, obs, steering):
        """
        Gère l'accélération, le freinage et la logique de sauvetage (rescue)
        Réduit la vitesse en virage et gère les épingles serrées (hairpin)

        Args:
            obs (dict): Dictionnaire contenant les observations de l'environnement
            steering (float): Valeur de braquage actuelle calculée
            z (float): Distance frontale au point cible

        Returns:
            tuple: (accel, brake, steering)
                - accel (float): Valeur d'accélération calculée
                - brake (bool): Indique si le frein doit être activé
                - steering (float): Valeur de braquage potentiellement modifiée (ex: rescue)
        """
        dist_now = obs['distance_down_track']
        velocity = obs['velocity']
        speed = np.linalg.norm(velocity)

        # On commence par la vitesse d'accélération par défaut configurée
        accel = self.conf.pilot.speed_control.default_accel
        brake = False

        # Virage standard : on ralentit un peu si le volant dépasse un certain seuil
        if abs(steering) > self.conf.pilot.speed_control.steering_threshold:
            accel = self.conf.pilot.speed_control.cornering_accel

        # Si le volant est braqué à fond
        if abs(steering) > self.hairpin_threshold:
            # On réduit fortement l'accélération pour permettre au kart de pivoter sur lui-même
            accel = self.hairpin_accel
            # Si on arrive trop vite dans l'épingle, on force un coup de frein
            if speed > self.hairpin_brake_speed:
                brake = True

        return accel, brake, steering

    def choose_action(self, obs):
        """
        Méthode principale orchestrant la lecture de la piste, le braquage et la vitesse
        Retourne le dictionnaire d'actions final

        Args:
            obs (dict): Dictionnaire contenant les observations de l'environnement

        Returns:
            dict: Dictionnaire d'actions (acceleration, steer, brake, drift, nitro, rescue, fire)
        """
        target_x, target_z = self.position_track(obs)
        steering = self.compute_turning_pps(obs, target_x, target_z)
        accel, brake, steering = self.manage_speed(obs, steering)

        action = {
            "acceleration": accel,
            "steer": steering,
            "brake": brake,
            "drift": False, "nitro": False, "rescue": False,
            "fire": False
        }
        return action