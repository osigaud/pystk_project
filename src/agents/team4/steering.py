import math
import numpy as np

class Steering:
    
    def __init__(self):
        self.L = 2.5  # On simule un empattement
        
    def manage_pure_pursuit(self,gx,gz,gain):
        
        l2 = gx**2 + gz**2 # calcul de l'hypoténuse
            
        if l2 < 0.01 : return 0.0 # Si on est déjà sur la cible, on ne tourne pass
            
        angle = math.atan2(2 * self.L * gx,l2) # Calcul de la formule issu de pure_pursuit et du modèle bicyclette

        steer = angle * gain # application du coefficient
        
        return np.clip(steer,-1,1) # Ajout d'une sécurité pour garder le steer entre -1 et 1