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
        
        self.look_limite = cfg.
        

    ## @brief   Calcule la courbure de la piste devant le kart.
    #
    #  Pour chaque triplet de nœuds consécutifs (i, i+1, i+2), calcule la
    #  déviation angulaire locale entre les deux segments adjacents.
    #  Retourne la moyenne des 3 déviations de plus grande valeur absolue,
    #  ce qui représente l'intensité du virage le plus serré à venir tout
    #  en filtrant les nœuds isolés bruités.
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #                Doit contenir la clé "paths_start" avec au moins 3 éléments.
    #  @return  float : courbure en radian dans ]-pi, pi].
    #                   Positif = virage à droite, négatif = virage à gauche.
    #                   Proche de zéro = ligne droite.
    def detectVirage(self, obs):
        noeuds_piste = obs["paths_start"]

        path_lookahead = min(10, len(noeuds_piste) - 2)
        if path_lookahead < 1:
            return 0.0

        deviations = []

        for i in range(path_lookahead):
            # Vecteur du segment i -> i+1
            dx0 = noeuds_piste[i+1][0] - noeuds_piste[i][0]
            dz0 = noeuds_piste[i+1][2] - noeuds_piste[i][2]

            # Vecteur du segment i+1 -> i+2
            dx1 = noeuds_piste[i+2][0] - noeuds_piste[i+1][0]
            dz1 = noeuds_piste[i+2][2] - noeuds_piste[i+1][2]

            angle0 = np.arctan2(dx0, dz0)
            angle1 = np.arctan2(dx1, dz1)

            # Déviation locale normalisée dans ]-pi, pi]
            deviation = angle1 - angle0
            deviation = (deviation + np.pi) % (2 * np.pi) - np.pi

            deviations.append(deviation)

        # Tri par valeur absolue décroissante : les virages les plus serrés en premier
        deviations.sort(key=abs, reverse=True)

        # Moyenne des 3 pires déviations : pire cas lissé pour filtrer le bruit
        top3 = deviations[:min(3, len(deviations))]
        angle_final = sum(top3) / len(top3)

        return angle_final

    ## @brief   Détermine dynamiquement le nombre de nœuds à anticiper.
    #
    #  Adapte le lookahead en fonction de l'intensité du virage détecté :
    #  plus le virage est serré, plus on regarde proche pour rester précis.
    #  Détecte également si le virage est long pour ajuster en conséquence.
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #                Doit contenir la clé "paths_start".
    #  @return  int  : nombre de nœuds à regarder devant le kart.
    #  @see     detectVirage()
    def get_dynamicLookahead(self, obs):
        node_path = obs.get("paths_start")
        if len(node_path) < 6:
            return self.path_lookahead

        angle = abs(self.detectVirage(obs))

        if angle < 0.1:       # ligne droite
            lookahead = 7
        elif angle <= 0.5:    # virage léger
            lookahead = 5
        else:                 # virage serré
            lookahead = 3
            # Vérification si le virage est long (courbure persistante)
            i = min(7, len(node_path) - 1)
            distance = np.linalg.norm(node_path[i] - node_path[0])
            self.virage_long = distance > 20
            if self.virage_long:
                lookahead = 7   # on regarde loin pour anticiper la sortie

        self.path_lookahead = lookahead
        return self.path_lookahead