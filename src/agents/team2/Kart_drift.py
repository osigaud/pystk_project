import math
import numpy as np
from utils.track_utils import compute_curvature, compute_slope
from omegaconf import OmegaConf
from .agent2 import Agent2
cfg = OmegaConf.load("../agents/team2/configDemoPilote.yaml")


class Kart_drift(Agent2):
    def calcul_rayon(self,n1,n2,n3):
        """permet de calculer le rayon d'un virage à partir de 3 noeuds qui se trouvent en face du kart """
        x1 , z1 = n1[0],n1[2]
        x2, z2 = n2[0], n2[2]
        x3, z3 = n3[0], n3[2]
        # on cherche d'abord la distance de l'arc
        AC = np.array([x3 - x1, z3 - z1])
        distance_AC = np.linalg.norm(AC)

        AB = np.array([x2 - x1, z2 - z1])
        distance_AB = np.linalg.norm(AB)
        
        AC_moit = np.array(AC/2)
        distance_AC_moit = np.linalg.norm(AC_moit)
        # on cherche mtn la hauteur depuis le deuxieme noeud jusqu a l'arc
        coord = distance_AB **2 - distance_AC_moit **2
        #il faut verifier le domaine de definition de la fonction racine carré
        if coord < 0 : 
            return 1.0
        else :  
            h = np.sqrt(coord)
            if h  == 0 : 
                h=1.0
            R = (h**2 /4) + (distance_AC**2)/(8*h)
        return R
    
    
    def detectVirage(self,obs):

        nodes_path = obs["paths_start"] #liste des neoud de la piste
        nb_nodes = len(nodes_path)
        path_lookahead = 5

        virages = [] #liste resultat pour stocker les virages detectes

        for i in range (nb_nodes - path_lookahead): #boucle pour le second (noeud loin=anticipation)

            curr_node = nodes_path[i] #le premier noeud qu'on rgd (noeud proche)
            nv = nodes_path[i + self.path_lookahead - 2]
            lookahead_node = nodes_path[i+path_lookahead] #noeud loin

            x1, z1 = curr_node[0], curr_node[2] #coordonnees pour angle
            x2, z2 = lookahead_node[0], lookahead_node[2]

            angle1 = np.arctan2(x1, z1)
            angle2 = np.arctan2(x2, z2)
            curvature = angle1 - angle2 
            R = self.calcul_rayon(curr_node,nv,lookahead_node)
            if R < 80: 
                virages.append({ "index": i, "curvature": curvature, "rayon":R, "noeuds" : [curr_node,nv,lookahead_node]})
        return virages
    
    
    def adapteAcceleration(self,obs):
        """le but va etre d'adpater l'acclération dans diverses situations dont notamment 
        les virages serrés, les lignes droites ou une legere curvature """
        
        liste_virage=self.anticipeVirage(obs)
        acceleration = 1.0 # c l'accélération maximale 
        drift = False

        vitesse_actuelle = np.linalg.norm(obs.get("velocity"))
        
        if len(liste_virage) < 1 :  # s'il n'y a pas de virage 
            return acceleration, drift
        else :
            
            proche_virage = liste_virage[0]
            curvature = proche_virage["curvature"]
            rayons = proche_virage["rayon"]
            a_max = 8
            
            vitesse_lim = np.sqrt(rayons * a_max) 
            if  abs(curvature) > 4 and rayons < 10: 
                acceleration = acceleration - 0.6
                if vitesse_actuelle > vitesse_lim : 
                    drift = True  
            elif abs(curvature) > cfg.virages.serrer.i1 and curvature  <= cfg.virages.serrer.i2: # virage serré 
                acceleration= acceleration - 0.4
                if vitesse_actuelle > vitesse_lim : 
                    drift = True
                else : 
                    drift = False
            else :    
                acceleration = 1.0
                drift = False
        return acceleration, drift
        
        
    def adapteAcceleration(self, obs):
        #calcul de la vitesse réelle (norme)
        velocity = np.array(obs.get("velocity", [0, 0, 0]))
        speed = np.linalg.norm(velocity)
        
        liste_virage = self.detectVirage(obs)
        acceleration = 1.0
        drift = False

        if len(liste_virage) < 1:
            acceleration = cfg.acceleration.sans_virage
        else:
            proche_virage = liste_virage[0]
            curvature = proche_virage["curvature"]
            
            #drift courbure maximale
            if curvature > cfg.virages.drift:
                # On n'active le drift que si on a assez de vitesse
                if speed > 10.0:
                    drift = True
                    acceleration = 1.0 - 0.27 # Ta valeur pour le drift
                else:
                    acceleration = 1.0 - 0.27 # Trop lent pour drift, mais on ralentit quand même
            
            #virage serré 
            elif cfg.virages.serrer.i1 < curvature <= cfg.virages.serrer.i2:
                acceleration = 1.0 - 0.10
            
            #virage moyen
            elif cfg.virages.moyen.i1 < curvature <= cfg.virages.moyen.i2:
                acceleration = 1.0 - 0.05
            
            #virage léger 
            else:
                acceleration = 1.0 - 0.02
                
        return acceleration, drift #on renvoie un tuple
 
 
