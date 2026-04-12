## @file    anticipe_kart.py
#  @brief   Détection de la courbure de la piste devant le kart.
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou et Maty Niang
#  @date    20-01-2026

import numpy as np


## @class   AnticipeKart
#  @brief   Détecte et mesure la courbure de la piste devant le kart.
#
#  Calcule la déviation angulaire entre chaque paire de segments consécutifs
#  sur une fenêtre de 10 nœuds, puis retourne la moyenne des 3 déviations
#  les plus fortes. Cette approche détecte le virage le plus serré à venir
#  tout en filtrant le bruit des nœuds mal placés.
#  Le résultat est utilisé par AccelerationControl pour choisir
#  le niveau d'accélération adapté.
#
#  @see AccelerationControl
class AnticipeKart:

    ## @brief   Initialise les attributs de détection de virage.
    def __init__(self, cfg):

        ## @var virage_long
        #  @brief Vrai si le virage courant est long (courbure persistante au-delà de 7 nœuds).
        self.virage_long = False

        ## @var path_lookahead
        #  @brief Nombre de nœuds anticipés, mis à jour dynamiquement par get_dynamicLookahead().
        self.path_lookahead = 5
        
        self.look_limite = cfg.look_limite 
        self.look_droite = cfg.look_droite 
        self.look_leger = cfg.look_leger
        self.droite = cfg.lookahead.droite        
        self.leger = cfg.lookahead.leger        
        self.serrer = cfg.lookahead.serrer
        self.long = cfg.lookahead.long
        self.dist = cfg.lookahead.dist
        self.prec_angle = 0.0

   ## @brief   Calcule la courbure de la piste devant le kart.
    #
    #  Prend le nœud courant (paths_start[0]) et le nœud situé 5 positions
    #  plus loin (paths_start[5]), puis calcule l'angle du vecteur qui va
    #  du premier au second par rapport à l'axe avant du kart via arctan2.
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #                Doit contenir la clé "paths_start" avec au moins 6 éléments.
    #  @return  float : angle en radian dans ]-pi, pi].
    #                   Positif = virage à gauche, négatif = virage à droite.
    #                   Proche de zéro = ligne droite.
    def detectVirage(self, obs):
        noeuds_piste = obs["paths_start"]
        path_lookahead = 5

        noeud_cour = noeuds_piste[0]
        noeud_loin = noeuds_piste[path_lookahead]

        x1, z1 = noeud_cour[0], noeud_cour[2]
        x2, z2 = noeud_loin[0], noeud_loin[2]

        dx = x2 - x1
        dz = z2 - z1

        angle = np.arctan2(dx, dz)

        return angle

    
    def changementDirection(self, obs):
        changement = False
        angle=self.detectVirage(obs)
        if abs(angle) > 0.27 and abs(self.prec_angle) > 0.27 : 
            if angle * self.prec_angle < 0 : 
                changement = True
        self.prec_angle = angle
        return changement 


    