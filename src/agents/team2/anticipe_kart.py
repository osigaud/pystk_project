import numpy as np 

class AnticipeKart : 
    
    def detectVirage(self,obs):
        """ le but est de calculer l'angle qui definit les virages devant le kart
            ->la fonction renvoie un angle en radian 
        """
        noeuds_piste= obs["paths_start"]
        path_lookahead = 5
        noeud_cour= noeuds_piste[0]
        noeud_loin= noeuds_piste[path_lookahead]

        x1, z1 = noeud_cour[0], noeud_cour[2] #coordonnees pour angle
        x2, z2 = noeud_loin[0], noeud_loin[2]

        dx = x2 - x1 #coordonnées vecteur
        dz = z2 - z1

        angle= np.arctan2(dx,dz) #angle entre les vecteurs dx et dz en radian
        #print("angle:",angle)

        return angle
    