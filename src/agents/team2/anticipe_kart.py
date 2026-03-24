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
        path_lookahead = 5                   # on regarde 5 noeuds en avant

        noeud_cour = noeuds_piste[0]               # noeud juste devant le kart
        noeud_loin = noeuds_piste[path_lookahead]  # noeud eloigne pour anticiper le virage

        x1, z1 = noeud_cour[0], noeud_cour[2]  # coordonnees horizontales du noeud courant
        x2, z2 = noeud_loin[0], noeud_loin[2]  # coordonnees horizontales du noeud eloigne

        dx = x2 - x1  # composante X du vecteur entre les deux noeuds
        dz = z2 - z1  # composante Z du vecteur entre les deux noeuds

        angle = np.arctan2(dx, dz)  # angle de ce vecteur par rapport a l'axe avant Z

        return angle