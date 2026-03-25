## @file    shield_kart.py
#  @brief   Gestion de l'activation du shield et des items offensifs.
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou et Maty Niang
#  @date    20-01-2026

import numpy as np
from .rival_attack import AttackRivals


## @class   ActiveShield
#  @brief   Décide d'utiliser l'item en possession selon la situation de course.
#
#  Utilise AttackRivals pour détecter la présence d'un adversaire devant
#  le kart, puis décide si l'item courant doit être activé.
#  Le bubblegum est posé derrière (item défensif), les autres items
#  sont tirés vers l'avant (items offensifs).
#
#  @see AttackRivals
class ActiveShield:

    ## @var BUBBLEGUM
    #  @brief Identifiant de l'item bubblegum dans l'énumération pystk2.Powerup.
    BUBBLEGUM = 1

    ## @brief   Initialise le module avec un détecteur d'adversaires.
    def __init__(self):

        ## @var attack_rival
        #  @brief Module de détection des adversaires dans le champ de vision.
        self.attack_rival = AttackRivals()

    ## @brief   Indique si l'item en possession doit être utilisé maintenant.
    #
    #  Retourne True si un adversaire est détecté devant le kart,
    #  quel que soit le type d'item possédé.
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #                Doit contenir les clés "powerup_type" et "karts_position".
    #  @return  bool : True si l'item doit être utilisé, False sinon.
    #  @see     AttackRivals.attack_rivals()
    def fire_shield(self, obs):
        item        = obs["powerup_type"]
        kart_devant = self.attack_rival.attack_rivals(obs)

        if kart_devant:
            return True
        return False