from omegaconf import DictConfig
import numpy as np
from utils.track_utils import compute_curvature

class SpeedController:
    
    """
    Module SpeedController : Gère la logique d'accélération
    """

    def __init__(self,config : DictConfig) -> None:
        """Initialise les variables d'instances de l'agent."""
        
        self.c = config
        """@private"""
        self.g = self.c.curvature_gain
        """@private"""
        self.amax = self.c.acceleration_max
        """@private"""
    
    def reset(self) -> None:
        """Réinitialise les variables d'instances de l'agent expert"""
        pass
    
    def manage_speed(self,obs:dict) -> tuple[float,bool]:
        """
        Gère l'accélération.

        Args:
            
            obs(dict) : Les données fournies par le simulateur.
        
        Returns:
            
            float: Valeur représentant l'accélération.
            bool: Variable permettant d'activer ou non le brake.

        """
        points = obs.get("paths_start",[]) # On récupère la liste des points

        p1 = np.array(points[1][:3]) # on recupère plusieurs points espacés pour regarder plus loin sur la piste
        p2 = np.array(points[2][:3])
        p3 = np.array(points[3][:3])
        p4 = np.array(points[4][:3])
        p5 = np.array(points[5][:3])

        v1 = p2 - p1 #on calcule chaque vecteurs ce qui nous permet d'avoir la direction de la piste
        v2 = p3 - p2
        v3 = p4 - p3
        v4 = p5 - p4

        def angle(a, b):
            a = a / (np.linalg.norm(a) + 1e-6)#+1e-6 permet de divisé a par une valeur >0 et eviter les divisions par 0
            b = b / (np.linalg.norm(b) + 1e-6)
            return np.arccos(np.clip(np.dot(a, b), -1.0, 1.0))#np.dot correspond au produit scalaire

        k = (angle(v1,v2) + angle(v2,v3) + angle(v3,v4)) / 3
        #print("angle renvoie ",k)

        k2 = abs(compute_curvature(points[1:5][:3]))
        #print("compute_curvature renvoie ", k2)


        v_target2 = self.amax/np.sqrt(1+self.g*k)
        print('vitesse avec angle ',v_target2)

        v_test = np.clip(self.amax/np.sqrt(1+k2),0, self.amax)
        print('vitesse avec compute_curvature ', v_test)

        if v_target2 >= 0.96:  
            v_target2 = self.amax #suite a ce calcul v_target est limité a 0.96 donc ce if lui permet d'atteindre la vitesse maximale
        
        return np.clip(v_test*1.75,0,self.amax), False #on ajoute un gain 
        
