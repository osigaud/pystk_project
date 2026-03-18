## @file    react_items.py
#  @brief   Ajustement du steering selon les items visibles sur la piste.
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou et Maty Niang
#  @date    20-01-2026

import numpy as np


## @class   ReactionItems
#  @brief   Oriente le kart vers les bons items et l'éloigne des mauvais.
#
#  Priorité : esquiver un mauvais item proche l'emporte toujours
#  sur aller chercher un bon item.
#
#  Bons items  : BONUS_BOX(0), NITRO_BIG(2), NITRO_SMALL(3), EASTER_EGG(6).
#  Mauvais items : tout le reste (banane, bubblegum...).
class ReactionItems:

    ## @brief   Initialise les angles d'esquive depuis la configuration.
    #
    #  @param   cfg  Configuration OmegaConf issue de configDemoPilote.yaml.
    #                Utilise les clés angle_evite_n et angle_evite_p.
    def __init__(self, cfg):

        ## @var angle_n
        #  @brief Angle d'esquive quand le mauvais item est à droite (valeur négative = virage à gauche).
        self.angle_n = cfg.angle_evite_n

        ## @var angle_p
        #  @brief Angle d'esquive quand le mauvais item est à gauche (valeur positive = virage à droite).
        self.angle_p = cfg.angle_evite_p

    ## @brief   Retourne un ajustement de steering selon les items devant le kart.
    #
    #  Parcourt tous les items visibles (Z > 0, distance < 25).
    #  Pour les bons items : calcule l'angle vers le plus proche et ajuste le steering.
    #  Pour les mauvais items à moins de 15 unités : applique un angle d'esquive fixe.
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #                Utilise les clés "items_position" et "items_type".
    #  @return  float : ajustement de steering entre -1.0 et 1.0.
    #                   0.0 si aucun item pertinent n'est détecté.
    def reaction_items(self, obs):
        items_pos  = obs.get('items_position', [])
        items_type = obs.get('items_type', [])
        steering_adjustment = 0.0

        GOOD_ITEM_IDS  = [0, 2, 3, 6]  # BONUS_BOX, NITRO_BIG, NITRO_SMALL, EASTER_EGG
        best_good_dist = 1000.0         # distance du meilleur bon item vu jusqu'ici
        angle_evite    = 0.0            # angle d'esquive si un mauvais item est détecté
        dist_min_evite = 15.0           # distance déclenchant l'esquive d'un mauvais item

        for i, pos in enumerate(items_pos):  # i sert à faire le lien entre la position et le type
            pos  = np.array(pos)
            dist = np.linalg.norm(pos)

            # items derriere ou trop loin => ignorer
            if pos[2] < 0 or dist > 25.0:
                continue

            item_type = items_type[i] if i < len(items_type) else None

            if item_type in GOOD_ITEM_IDS:
                # on retient le bon item le plus proche
                # le *5 pondère cette correction face à la correction de centrage de piste
                if dist < best_good_dist:
                    best_good_dist = dist
                    angle = np.arctan2(pos[0], pos[2])
                    steering_adjustment = float(np.clip(angle * 5, -0.8, 0.8))  # adapter aux differentes pistes
            else:
                # eviter les bad items proches
                # pos[0] > 0 = item à droite = on part à gauche (angle_n < 0)
                if dist < dist_min_evite:
                    angle_evite = self.angle_n if pos[0] > 0 else self.angle_p

        if abs(angle_evite) > 0:
            return angle_evite  # evite bad item

        return steering_adjustment  # se dirige vers good items