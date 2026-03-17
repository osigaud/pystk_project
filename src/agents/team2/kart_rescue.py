import numpy as np


class StuckControl : 
    def __init__(self) : 
        self.stuck_steps = 0    
        self.recovery_steps = 0 
        self.en_marche_arriere = False

    def gerer_recul(self, obs, vitesse, steering):
        """ Gère la détection de blocage et la marche arrière """
        phase = obs.get("phase", 0)
        
        if vitesse < cfg.vitesse and phase > 2: #si vitesse nulle après le départ
            self.stuck_steps += 1
        else:
            self.stuck_steps = 0

        if self.stuck_steps > cfg.steps and not self.en_marche_arriere: #temps de decision d'activer marche arriere
            self.en_marche_arriere = True
            self.recovery_steps = cfg.recovery #durée de la marche arriere 

        if self.en_marche_arriere:   #execution de marche arriere
            self.recovery_steps -= 1
            if self.recovery_steps <= 0:
                self.en_marche_arriere = False
            
            #braquage 
            correction = steering.correction_centrePiste(obs)
            braquage_arriere = cfg.braquage if correction > 0 else -cfg.braquage #braquage 
            
            return {
                "acceleration": 0.0,
                "steer": braquage_arriere,
                "brake": True, #declencher la marche arriere
                "drift": False,
                "nitro": False,
                "rescue": False,
                "fire": False,
            }
        return None
