import numpy as np 


class SteeringPiste:
    def __init__(self, correction):
        self.correction = correction
    
    
    def correction_centrePiste(self, obs):
        """
        Calcule la correction nécessaire pour rester au centre de la piste.
        """
        #si paths_start n'existe pas,on renvoie 0 et on veut qu'il y ait au moins 2 points devant le kar
        if "paths_start" not in obs or len(obs["paths_start"])<3:
            return 0.0
        #le point au centre de la piste juste devant le kart
        point_proche_kart = obs["paths_start"][2]
        x = point_proche_kart[0] #coordonees du point qui nous indique gche ou drte
        z = point_proche_kart[2] #coordonnees du pt qui nous indique devant ou derriere
        if z<=0.0:
            return 0.0
        # angle qu'il faut tourner pour atteindre le point
        angle_vers_centre= np.arctan2(x, z)
        # if abs(angle_vers_centre)<0.03:
        #     return 0.0
        correction = angle_vers_centre * self.correction
        return np.clip(correction, -0.6, 0.6) #np.clip (=barrière de sécurité) sécurise pour que le res ne dépasse pas l'intervalle (= les limites physiques du volant, car un volant ne tourne pas infiniment)
