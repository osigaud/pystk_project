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
        gx = target[0] # Recuperation de x, le decalage lateral
        gz = target[2] # Recuperation de z, la profondeur
        
        danger, b_x = self.banana_dodge.banana_detection(obs) # Appel de la fonction detection banane

        if danger:

            target = points[1] # Changement de référentiel pour plus de nervosite
            gx = target[0] # Recuperation de x, le decalage lateral
            gz = target[2] # Recuperation de z, la profondeur

            esquive = 0.8 # Variable d'esquive

            if b_x >= 0:
                gx-=esquive # Si la banane est à notre droite on va à gauche
            else:
                gx+=esquive # Si la banane est à notre gauche on va à droite

        
        l2 = gx**2 + gz**2 # calcul de l'hypoténuse
            
        if l2 < 0.01 : return 0.0 # Si on est déjà sur la cible, on ne tourne pass
            
        angle = math.atan2(2 * self.L * gx,l2) # Calcul de la formule issu de pure_pursuit et du modèle bicyclette

        steer = angle * self.gain # application du coefficient
        
        return np.clip(steer,-1,1) # Ajout d'une sécurité pour garder le steer entre -1 et 1
        

        





