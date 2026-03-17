import numpy as np 
from .anticipe_kart import AnticipeKart 

class AccelerationControl : 
    
    def __init__(self, cfg) : 
        self.seuildrift = cfg.virages.drift
        self.serreri1 = cfg.virages.serrer.i1
        self.serreri2 = cfg.virages.serrer.i2
        self.moyeni1 = cfg.virages.moyen.i1
        self.moyeni2 = cfg.virages.moyen.i2
        self.anticipe_kart = AnticipeKart()
        

    def adapteAcceleration(self,obs):
        """
        le but va etre d'adpater l'acclération dans diverses situations dont notamment 
        les virages serrés, les virages moyens et les lignes droites --> cette fonction a fait appel à detectVirage() 
        """
        acceleration = 1.0
        curvature=abs(self.anticipe_kart.detectVirage(obs))

        if curvature > self.seuildrift:
                #0.27
            acceleration = 0.80
        elif curvature > self.serreri1 and curvature <= self.serreri2: # virage serré 
                #0.10
            acceleration= 0.85
        elif curvature > self.moyeni1 and curvature <= self.moyeni2:  #virage moyen 
                #0.05
            acceleration = 0.95
        else :
                #0.02
            acceleration = 1.0
        return acceleration 
    