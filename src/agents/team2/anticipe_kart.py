## @file    anticipe_kart.py
#  @brief   Détection de la courbure de la piste devant le kart.
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou et Maty Niang
#  @date    20-01-2026


import numpy as np

## @class   AnticipeKart
#  @brief   Calcule l'angle du virage à venir en comparant deux nœuds de piste.
#
#  Compare le nœud courant (index 0) et un nœud éloigné (index 5) dans
#  le plan horizontal XZ du référentiel du kart.
#  Le résultat est utilisé par AccelerationControl pour choisir
#  le niveau d'accélération adapté.
#
#  @see AccelerationControl
class AnticipeKart:
    def __init__(self) : 
        self.virage_long = False
        self.path_lookahead = 5
    ## @brief   Calcule l'angle du virage devant le kart.
    #
    #  Mesure la déviation angulaire entre le nœud courant et le nœud
    #  situé path_lookahead positions devant, dans le plan horizontal XZ.
    #  Un angle proche de zéro indique une ligne droite.
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #                Doit contenir la clé "paths_start" avec au moins 6 éléments.
    #  @return  float : angle en radian.
    #                   Positif = virage à droite, négatif = virage à gauche.
    #                   La valeur absolue représente l'intensité du virage.
    def detectVirage(self, obs):
        noeuds_piste   = obs["paths_start"]  # noeuds de piste dans le repere du kart (Z=avant, X=droite)
        path_lookahead = 5 #self.path_lookahead                   # on regarde 5 noeuds en avant

        noeud_cour = noeuds_piste[0]               # noeud juste devant le kart
        noeud_loin = noeuds_piste[path_lookahead]  # noeud eloigne pour anticiper le virage

        x1, z1 = noeud_cour[0], noeud_cour[2]  # coordonnees horizontales du noeud courant
        x2, z2 = noeud_loin[0], noeud_loin[2]  # coordonnees horizontales du noeud eloigne

        dx = x2 - x1  # composante X du vecteur entre les deux noeuds
        dz = z2 - z1  # composante Z du vecteur entre les deux noeuds

        angle = np.arctan2(dx, dz)  # angle de ce vecteur par rapport a l'axe avant Z

        return angle
    
    
    def get_dynamicLookahead(self, obs) :
        """ Cette fonction permet de déterminer dynamiquement le nombre de noeuds à regarder au plus loin 
        en fonction des différents seuils de virages
        
        Args : 
        - obs(dict) : Dictionnaire d'observation retourné par l'environnement
        
        Return : 
                int : nombre de noeuds à regarder
        """
        node_path = obs.get("paths_start")
        if len(node_path) < 6 : 
            return self.path_lookahead
        
        angle = abs(self.detectVirage(obs))
        virage_long = False
        
        if angle < 0.1 :         # ligne droite 
            lookahead = 7
        elif angle <=0.5:        # virage leger
            lookahead = 5     
        else :                    
            lookahead =  3        # virage serré
            # on verifie si le virage est long ou pas 
            i = min(7, len(node_path)-1)
            distance = np.linalg.norm(node_path[i] - node_path[0])
            virage_long = distance > 20
            if virage_long :
                lookahead = 7 # on regarde loin pour un long virage 
        self.path_lookahead = lookahead
        self.virage_long = virage_long # sera utilisé dans l'acceleration pour ajuster la vitesse du kart dans les virages longs
        return self.path_lookahead