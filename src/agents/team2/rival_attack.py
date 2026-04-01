## @file    rival_attack.py
#  @brief   Module de décision de tir sur les karts adversaires.
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou, Maty Niang
#  @date    20-01-2026

import numpy as np
from omegaconf import OmegaConf
cfg = OmegaConf.load("../agents/team2/configDemoPilote.yaml")

## @class   AttackRivals
#  @brief   Décide d'utiliser l'item offensif selon la position des adversaires.
#
#  Un tir est déclenché si un adversaire est à moins de 40 unités devant
#  le kart et dans un cône de 15 degrés autour de l'axe longitudinal (z).
#
#  @see Agent2.choose_action()
class AttackRivals:

    ## @brief   Vérifie si un adversaire est dans la zone de tir.
    #
    #  Parcourt tous les karts adversaires visibles dans l'observation,
    #  et retourne True dès qu'un adversaire remplit les deux conditions :
    #  - être devant le kart (z > 0)
    #  - être à moins de 40 unités et dans un cône de 15 degrés
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #                Doit contenir la clé "karts_position" (positions des autres karts
    #                dans le référentiel du kart courant).
    #  @return  bool : True si au moins un adversaire est dans la zone de tir,
    #                  False sinon.
    #  @note    Les karts derrière le kart (z <= 0) sont ignorés.
    def attack_rivals(self, obs):
        karts_pos = obs['karts_position']  # positions des autres karts dans le référentiel du kart
        for pos in karts_pos:
            dist = np.linalg.norm(pos)
            if pos[2] > 0:  # si l'adversaire est devant nous
                angle = np.degrees(np.arctan2(pos[0], pos[2]))
                if dist < cfg.champs_vision.dist and abs(angle) < cfg.champs_vision.angle:  # si l'adversaire est près et dans l'axe de tir
                    return True
        return False
