import math
import numpy as np
from .banana_detection import Banana

class Steering:
    
    def __init__(self):
        self.L = 2.5  # On simule un empattement
        self.gain = 6.0 # ajout d'un coefficient pour ramener sur notre referentiel
        self.banana_dodge = Banana()
    
    
    def manage_pure_pursuit(self,obs):
        
        points = obs.get("paths_start",[])
        
        if len(points) <= 2:return 0.0 
        
        target = points[2] # Recuperation du troisième point
        gx = target[0] # Recuperation de x, le decalage lateral
        gz = target[2] # Recuperation de z, la profondeur
        
        danger, b_x = self.banana_dodge.banana_detection(obs)
        
        l2 = gx**2 + gz**2 # calcul de l'hypoténuse
            
        if l2 < 0.01 : return 0.0 # Si on est déjà sur la cible, on ne tourne pass
            
        angle = math.atan2(2 * self.L * gx,l2) # Calcul de la formule issu de pure_pursuit et du modèle bicyclette

        steer = angle * self.gain # ajout d'un coefficient pour ramener sur notre referentiel

        return np.clip(steer,-1,1) # Ajout d'une sécurité pour garder le steer entre -1 et 1
        

        





