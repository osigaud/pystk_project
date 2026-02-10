import math
import numpy as np
from .banana_detection import Banana

class Steering:
    
    def __init__(self):
        self.L = 2.5  # On simule un empattement
        self.gain = 6.0 # ajout d'un coefficient pour ramener sur notre referentiel
        self.banana_dodge = Banana() # Integration de la classe Banana
    
    def manage_pure_pursuit(self,obs):
        
        points = obs.get("paths_start",[]) # On récupère les noeuds
        
        if len(points) <= 2 : return 0.0 # Si la liste ne contient pas assez de points on renvoie un steer de 0
        
        target = points[2] # Recuperation du troisième point
        
        # --- DETECTION BANANE ---
        danger, b_x = self.banana_dodge.banana_detection(obs) # Appel de la fonction detection banane

        if danger:
            # CAS 1 : DANGER IMMÉDIAT (Priorité absolue)
            target = points[1] # Changement de référentiel pour plus de nervosite
            gx = target[0] # Recuperation de x, le decalage lateral
            gz = target[2] # Recuperation de z, la profondeur

            esquive = 0.8 # Variable d'esquive

            if b_x >= 0:
                gx-=esquive # Si la banane est à notre droite on va à gauche
            else:
                gx+=esquive # Si la banane est à notre gauche on va à droite

        else:
            # CAS 2 : PAS DE DANGER -> ON CHASSE LES BONUS 
            
            # On vérifie d'abord si la route est droite pour ne pas se tuer
            # (On utilise points[2] comme référence route)
            road_target = points[2]
            is_road_straight = abs(road_target[0]) < 3.0

            target_bonus = None
            best_score = 1000.0

            if is_road_straight:
                items_pos = obs.get('items_position', [])
                items_types = obs.get('items_type', [])

                for i in range(len(items_pos)):
                    pos = items_pos[i]
                    typ = items_types[i]
                    
                    # 0 = Cadeau, 3 = Nitro
                    if typ == 0 or typ == 3:
                        z_dist = pos[2] 
                        x_dist = pos[0]

                        # Filtres de sécurité (Pas trop large, pas trop loin)
                        if (abs(x_dist) < 1.5) and (2.0 < z_dist < 20.0):
                            # Score: Distance + Penalité latérale
                            score = z_dist + (3.0 * abs(x_dist))
                            
                            if score < best_score:
                                best_score = score
                                target_bonus = pos
            
            # Si on a trouvé un bonus, il devient la cible
            if target_bonus is not None:
                target = target_bonus
            
            # Mise à jour des coordonnées pour le calcul final
            gx = target[0] # Recuperation de x, le decalage lateral (Route ou Bonus)
            gz = target[2] # Recuperation de z, la profondeur (Route ou Bonus)


        # --- CALCUL MATHÉMATIQUE  ---
        
        l2 = gx**2 + gz**2 # calcul de l'hypoténuse
            
        if l2 < 0.01 : return 0.0 # Si on est déjà sur la cible, on ne tourne pass
            
        angle = math.atan2(2 * self.L * gx,l2) # Calcul de la formule issu de pure_pursuit et du modèle bicyclette

        steer = angle * self.gain # application du coefficient
        
        return np.clip(steer,-1,1) # Ajout d'une sécurité pour garder le steer entre -1 et 1