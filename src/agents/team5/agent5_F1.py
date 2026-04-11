import numpy as np
import math
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
        self.L = self.conf.pilot.navigation.l
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



    def position_track_lock(self, obs):
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
                node_vect = obs["paths_start"][self.node_idx]
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

    def position_track_fixe(self, obs):
        """
        La fonction retourne un noeud en fonction d'un indice et non pas en fonction d'une distance.
        """

        speed = np.linalg.norm(obs['velocity'])

        # Plus on est rapide plus on regarde loin (mais on limite quand même au 4ème noeud pour ne pas voir trop loin)
        lookahead = 2 

        paths = obs['paths_start'][lookahead]


        # On retourne l'écart latéral x et l'écart avant z du point cible
        return paths[0], paths[2]

    def position_track_fixe_speed(self, obs):
        """
        La fonction retourne un noeud en fonction d'un indice et non pas en fonction d'une distance.
        """

        speed = np.linalg.norm(obs['velocity'])

        # Plus on est rapide plus on regarde loin (mais on limite quand même au 4ème noeud pour ne pas voir trop loin)
        lookahead = min(int(2 + self.conf.pilot.navigation.lookahead_speed_factor * speed), 4)

        paths = obs['paths_start'][lookahead]


        # On retourne l'écart latéral x et l'écart avant z du point cible
        return paths[0], paths[2]

    def position_track_dist(self, obs):
        paths = obs.get('paths_start', [])

        if len(paths) == 0:
            return 0.0, self.ahead_dist

        speed = np.linalg.norm(obs['velocity'])

        lookahead = self.ahead_dist + speed * self.lookahead_factor
        lookahead = np.clip(lookahead, self.ahead_dist, self.lookahead_max)

        target = paths[-1]
        for p in paths:
            if p[2] > lookahead:
                target = p
                break

        return target[0], target[2]

    def compute_turning_pps(self, target_x, target_z):
        l_squared = target_x**2 + target_z**2

        if l_squared < 1e-4:
            return 0.0

        #angle = np.arctan2(2.0 * self.L * target_x, l_squared)
        angle = np.arctan2(2.0 * self.L * target_x, (l_squared))
        steering = np.clip(self.K * angle, -1.0, 1.0)

        # anti-vibration
        if abs(target_x) < 0.1 and abs(steering) < 0.07:
            steering = 0.0

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
        velocity = obs['velocity']
        speed = np.linalg.norm(velocity)

        # On commence par la vitesse d'accélération par défaut configurée
        accel = self.conf.pilot.speed_control.default_accel
        brake = False

        #Solution 1 : On a une vitesse programmée manuellement en fonction de pleins de situations
        # Solution 2 : On a une vitesse minimale (0.1) mais adaptée à l'inverse de la courbure du volant : 1/steering
        # Si steering monte alors l'accélération baisse, sinon l'accélération augmente



        # Virage standard : on ralentit un peu si le volant dépasse un certain seuil
        if abs(steering) > self.conf.pilot.speed_control.steering_threshold:
            accel = self.conf.pilot.speed_control.cornering_accel

        # Virage prononcé 
        if abs(steering) > self.hairpin_threshold:
            # On réduit fortement l'accélération pour permettre au kart de pivoter sur lui-même
            accel = self.hairpin_accel
            # Si on arrive trop vite dans l'épingle, on force un coup de frein
            if speed > self.hairpin_brake_speed:
                brake = True
        

        return accel, brake


    def manage_speed_proportionel(self, obs, steering):
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
        velocity = obs['velocity']
        speed = np.linalg.norm(velocity)
        # On commence par la vitesse d'accélération par défaut configurée
        brake = False

        #Solution 1 : On a une vitesse programmée manuellement en fonction de pleins de situations
        # Solution 2 : On a une vitesse minimale (0.1) mais adaptée à l'inverse de la courbure du volant : 1/steering
        # Si steering monte alors l'accélération baisse, sinon l'accélération augmente


        # Accélération inversement proportionnelle au steering
        
        alpha = 1
        beta = 1
        #k = -2.8
        accel = beta - alpha * (abs(steering)**3)
        

        if abs(steering) < 0.15:
            accel = self.conf.pilot.speed_control.default_accel
        elif abs(steering) > self.hairpin_threshold:
            # On réduit fortement l'accélération pour permettre au kart de pivoter sur lui-même
            accel = self.hairpin_accel
            # Si on arrive trop vite dans l'épingle, on force un coup de frein
            if speed > self.hairpin_brake_speed:
                brake = True


        return accel, brake


    def manage_speed_curvature(self, obs):
        speed = np.linalg.norm(obs["velocity"])
        points = obs.get("paths_start", [])
        brake = False

        # Valeur par défaut
        if len(points) < 3:
            return 1.0, False

        # Courbure sur quelques points devant
        curvature = abs(compute_curvature(points[2:5]))

        # Accélération inversement proportionnelle à la courbure
        accel = 1.0 / np.sqrt(1.0 + curvature * self.conf.pilot.speed_control.curvature_gain)

        # On borne 
        accel = np.clip(accel, 0, 1)

        # On freine seulement si gros virages
        brake = (
            curvature > self.conf.pilot.speed_control.hairpin_curvature
            and speed > self.conf.pilot.speed_control.hairpin_brake_speed
        )

        return float(accel), bool(brake)
        
    

    def manage_speed_paliers(self, obs, steering):
        acceleration = self.conf.pilot.speed_control.default_accel  # 1.0
        brake = False

        points = obs.get("paths_start", [])

        # Valeur par défaut
        if len(points) < 3:
            return 1.0, False

        # Courbure sur quelques points devant
        curvature = abs(compute_curvature(points[2:6]))

        if curvature < 2.4:
            acceleration = 1.0
        elif curvature < 4:  
            acceleration = 0.6
            brake = True
        elif curvature < 5.5:  
            acceleration = 0.4
            brake = True
        elif curvature <= 6 and steering > 0.6:    
            acceleration = 0.3
            brake = True
        elif curvature <= 10 and steering > 0.9:
            acceleration = 0.1
            brake = True

        return acceleration, brake

    def choose_action(self, obs):
        """
        Méthode principale orchestrant la lecture de la piste, le braquage et la vitesse
        Retourne le dictionnaire d'actions final

        Args:
            obs (dict): Dictionnaire contenant les observations de l'environnement

        Returns:
            dict: Dictionnaire d'actions (acceleration, steer, brake, drift, nitro, rescue, fire)
        """

        points = obs.get("paths_start", [])
        curvature = abs(compute_curvature(points[2:6]))
        print("Courbure : ", curvature)

        target_x, target_z = self.position_track_dist(obs)
        steering = self.compute_turning_pps(target_x, target_z)
        accel, brake = self.manage_speed_paliers(obs, steering)

        if(float(obs['distance_down_track'].item()) < 5):
            action = {
                "acceleration": 1.0,
                "steer": 0.0,
                "brake": False,
                "drift": False, "nitro": False, "rescue": False,
                "fire": False
            }
            return action    

        else : 
             
            action = {
                "acceleration": accel,
                "steer": steering,
                "brake": brake,
                "drift": False, "nitro": False, "rescue": False,
                "fire": False
            }
            return action