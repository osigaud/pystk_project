from .steering import Steering
from omegaconf import DictConfig
import numpy as np

class AgentEsquiveAdv:

    """
    Module Agent Expert Esquive Adversaire : Gère la logique de détection d'adversaires et de dépassement
    """
    
    def __init__(self,config : DictConfig ,config_pilote : DictConfig) -> None:
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.c = config
        """@private"""
        self.pilotage = Steering(config_pilote)
        """@private"""
        self.curr_dist = 0
        """@private"""
        self.timer = 0
        """@private"""
        self.duration = 0
        """@private"""
        self.locked_ax = 0
        """@private"""
    
    def reset(self) -> None:

        """Réinitialise les variables d'instances de l'agent expert"""
        self.pilotage.reset()
        self.curr_dist = 0
        self.timer = 0
        self.duration = 0
        self.locked_ax = 0
        
    def esquive_adv(self,obs : dict) -> tuple[bool,float,float]:
        """
        Détecte Les Adversaires.

        Args:
            
            obs(dict) : Les données de télémétrie fournies par le simulateur.
        
        Returns:
            
            bool : Variable permettant d'affirmer la présence d'un adversaire.
            float : Position latéral de l'adversaire.
            float : Profondeur de l'adversaire.
        """


        kart_pos = obs.get('karts_position', []) 
        if len(kart_pos) == 0:
            return False, 0.0, 0.0

        adv=kart_pos[0] # On récupère le kart adverse le plus proche

        #print(self.timer)
        
        distance = np.linalg.norm(adv) # Calcul de la norme du vecteur distance
        
        nx, nz = adv[0], adv[2] # Récupération du décalage latéral et de la profondeur

        # Si l'adversaire est assez proche et dans notre couloir
        if abs(nx) <= self.c.radar_x and self.c.radar_zmin < nz <= self.c.radar_zmax :
            
            # Si il est en train de se rapprocher, on incremente le timer
            if self.curr_dist ==0 or (self.curr_dist - distance) > self.c.ecart_danger: 
                self.timer += 1
            self.curr_dist = distance
            
            # Si pendant 4 frames, on a continué à s'approcher du kart, c'est un danger
            if self.timer >= self.c.timer:
                #print("On esquive !!")
                #print(nx,nz)
                self.timer = 0
                self.curr_dist = 0
                return True,nx,nz
        else:
            self.timer = 0
            self.curr_dist = 0
            
        return False, 0,0

    
    def choose_action(self,obs : dict,gx : float,gz : float,acceleration : float) -> tuple[bool,dict]:

        """
        
        Gère la logique de réaction à la détection d'un adversaire

        Args:
                
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            gx(float) : Décalage latéral actuel de la cible.
            gz(float) : Profondeur actuel de la cible.
            acceleration(float) : Accéleration de l'agent.

        Returns:
            
            bool : Permet de confirmer la présence d'un adversaire et la nécessité de le dépasser.
            dict : Le dictionnaire d'actions à réaliser pour esquiver un adversaire.
        
        """
        
        # Appel de la fonction de détection
        danger_adv, a_x,a_z = self.esquive_adv(obs)

        # Tant qu'on capte un danger, on mets à jour le decalage ainsi que le timer permettant de maintenir l'esquive sur x frames
        if danger_adv:
            
            self.locked_ax = a_x
            self.duration = self.c.duration
        
        # Si le timer > 0, on esquive
        if self.duration > 0:    
            
            self.duration -= 1
            if self.locked_ax >= 0:
                gx -= self.c.decalage_lateral # On se décale à gauche 
            else:
                gx += self.c.decalage_lateral # On se décale à droite
            
            gain_volant = self.c.default_gain
            steering = self.pilotage.manage_pure_pursuit(gx,gz,gain_volant)
            action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue":False,
            "fire": False,
            }
            return True, action
        
        return False, {}