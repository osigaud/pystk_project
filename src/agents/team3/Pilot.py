import math
import numpy as np



class Pilot():
    def choose_action(self, obs):
        # Récupération des nombreuses valeurs d'observation
    	# Afin que l'on récupère ce qui est important

        paths_start = obs["paths_start"]
        items_pos = obs["items_position"]
        items_type = obs["items_type"]

        # La vitesse ici est représenter par Pythagore
        speed = math.sqrt(obs["velocity"][0]**2 + obs["velocity"][2]**2)


        path_lookahead = max(2, math.floor(speed*0.17))
        path_lookahead = min(path_lookahead, len(paths_start) - 1)


		# On a hardcodé le noeud à regarder car on a des problèmes
		# Sur ce circuit en particulier
        if self.track == 'fortmagma':
            path_lookahead = 1
        
        # On récupère le noeud que l'on va regarder
        # Et on récupère leurs coordonnées x et z
        # On ignore le y vu qu'elle n'a pas que peu d'importance dans notre cas
        target_point = paths_start[path_lookahead]
        target_x = target_point[0]
        target_z = target_point[2]
        
        # Récupération de la largeur de la piste à proximité du kart
        current_width = obs["paths_width"][0]
        current_track_width = current_width[0]

        # Récupération de la largeur de la piste 
        # Au niveau du noeud que l'on prend pour cible
        lookahead_width = obs["paths_width"][path_lookahead]
        lookahead_track_width = lookahead_width[0]
        
        max_allowed_shift = (lookahead_track_width / 2.0) - 1.5

		# Le signe dépend si le virage est à droite alors le signe sera positif
		# Si le varage est à gauche alors le sera négatif
        if (max_allowed_shift < 0.0):
            max_allowed_shift = 0.0

        if (abs(target_x) > 2.0):
            if (target_x > 0):
                target_sign = 1.0
            elif (target_x < 0):
                target_sign = -1.0
            else:
                target_sign = 0.0
            apex_shift = target_sign * (max_allowed_shift * 0.75)
            target_x += apex_shift
        
        margin = 4.0 
        max_shift = 0.0
        emergency_steer = None 
        
        is_shielded = obs["shield_time"][0] > 0.0

        # Si on est protégé alors on skip cette partie
        # Sinon on évite les peaux de bananes et les bubblegums
        if not is_shielded:
            for i in range(len(items_type)):
                if ((items_type[i] == 1) or (items_type[i] == 4)):
                    # Récupération des coordonnées des bad items
                    bx, _, bz = items_pos[i]
                    
                    # Si a moins de 40m et situé sur le milieu de la piste
                    # Alors on l'évite
                    if ((0.1 < bz < 40.0) and (abs(bx) < margin)):
                        if (bx >= 0):
                            shift = bx - margin 
                        else:
                            shift = bx + margin 
                            
                        # Plus on est proche des bad items et plus notre kart sera agressif
                        # Dans sa capacité à éviter ces items dangereux
                        urgency = 1.0 - (bz / 40.0)
                        applied_shift = shift * urgency * 1.5 
                        
                        if (abs(applied_shift) > abs(max_shift)):
                            max_shift = applied_shift
                            
                        # Si danger imminent alors on devient très agressif sur le steering
                        if ((bz < 12.0) and (abs(bx) < 2.5)):
                            if (bx >= 0):
                                emergency_steer = -1.0 
                            else:
                                emergency_steer = 1.0  
                            
        # On évite les valeurs abérrantes
        if (max_shift > max_allowed_shift):
            max_shift = max_allowed_shift
        elif (max_shift < -max_allowed_shift):
            max_shift = -max_allowed_shift
        target_x += max_shift

        # Appliquation de l'algorithme de pure pursuit
        # A notre manière de piloter        
        sq = ((target_x**2) + (target_z**2))
        curvature = ((2.0 * target_x) / sq)
        desired_steer_angle = np.arctan(curvature * 1.25)
        
        # Utilisation de la variable d'observation max_steer_angle
        # Afin que le kart soit plus propre dans sa manière de rouler
        max_steer_angle = obs["max_steer_angle"][0]
        steer = desired_steer_angle / max_steer_angle
            
        # Si danger imminent alors on oublie tous les calculs complexes
        # Que l'on a fait précedemment
        is_dodging = False
        if emergency_steer is not None:
            steer = emergency_steer
            is_dodging = True
            
        # On limite le steering entre -1 et 1
        steer = max(-1.0, min(steer, 1.0))
        
        # Récupération des variables d'observations
        # Skeed_factor et center_path_distance
        skeed = obs["skeed_factor"][0]
        dist_from_center = obs["center_path_distance"][0]

        # On peut drifter sans danger si la piste est large
        # Et si le kart se situe vers le milieu de la piste
        track_wide_enough = current_track_width > 9.0
        safe_distance = abs(dist_from_center) < ((current_track_width / 2.0) - 2.0)
        can_drift_safely = track_wide_enough and safe_distance and not is_dodging
        
        # Si steer est à droite alors on drift à droite
        # Si steer est à gauche alors on drift à gauche
        # Sinon on ne drift pas
        if (self.drift_dir == 0):
            if can_drift_safely and (abs(steer) > 0.45):
                if (steer > 0):
                    self.drift_dir = 1.0
                elif (steer < 0):
                    self.drift_dir = -1.0
                else:
                    self.drift_dir = 0.0
        else:
            if not can_drift_safely or ((self.drift_dir * steer) < -0.3) or (skeed > 2.5):
                self.drift_dir = 0
            elif (abs(steer) < 0.15) and (skeed > 0.3):
                self.drift_dir = 0

        drift = (self.drift_dir != 0)

        if drift:
            if (self.drift_dir > 0): 
                steer = max(-0.1, steer) 
            else: 
                steer = min(0.1, steer)
        elif (skeed > 1.2):
            steer *= 0.7 

        # On accélère et freine différement selon différentes situations
        if is_dodging:
            acceleration = 0.4
            brake = True
        elif (abs(desired_steer_angle) > 0.7) and (speed > 15.0) and not drift:
            acceleration = 0.0
            brake = True
        elif (abs(steer) > 0.8) and not drift:
            acceleration = 0.6
            brake = False
        else:
            acceleration = 1.0
            brake = False

		# Utilisation du nitro si on est dans une ligne droite, qu'on ne freine pas
		# Qu'il n'y a pas de bad items devant nous et qu'on a récolter du nitro
        nitro = False
        current_energy = obs["energy"][0]
        if ((abs(steer) < 0.15) and (brake == False) and not is_dodging and (abs(max_shift) < 0.5) and (current_energy >= 1.0)):
            nitro = True

        action = {
            "acceleration": acceleration,
            "steer": steer,
            "brake": brake,
            "drift": drift,
            "nitro": nitro
        }
        
        return action