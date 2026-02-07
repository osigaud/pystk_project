import math
import numpy as np

class Steering:
    def manage_pure_pursuit(self,obs):
        
        points = obs.get("paths_start",[])
        if len(points) > 2: 
            target = points[2] # Recuperation du troisième point
            gx = target[0] # Recuperation de x, le decalage lateral
            gz = target[2] # Recuperation de z, la profondeur
            l2 = gx**2 + gz**2 # calcul de l'hypoténuse
            
            if l2 < 0.01 : return 0.0 # Si on est déjà sur la cible, on ne tourne pass
            
            L = 2.5 # On simule un empattement

            angle = math.atan2(2 * L * gx,l2) # Calcul de la formule issu de pure_pursuit et du modèle bicyclette

            steer = angle * 6.0 # ajout d'un coefficient pour ramener sur notre referentiel

            return np.clip(steer,-1,1) # Ajout d'une sécurité pour garder le steer entre -1 et 1
        else:
            return 0.0

        





