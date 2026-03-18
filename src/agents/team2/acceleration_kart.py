## @file    acceleration_kart.py
#  @brief   Adaptation de l'accélération du kart selon la courbure de la piste.
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou et Maty Niang
#  @date    20-01-2026

import numpy as np
from .anticipe_kart import AnticipeKart


## @class   AccelerationControl
#  @brief   Choisit le niveau d'accélération en fonction du virage détecté.
#
#  Appelle AnticipeKart.detectVirage() pour mesurer la courbure courante,
#  puis retourne une accélération réduite selon le type de virage :
#  - Virage très serré (> cfg.virages.drift)        : 0.80
#  - Virage serré      (cfg.virages.serrer.i1 à i2) : 0.85
#  - Virage moyen      (cfg.virages.moyen.i1 à i2)  : 0.95
#  - Ligne droite      (courbure faible)             : 1.00
#
#  @see AnticipeKart
class AccelerationControl:

    ## @brief   Initialise les seuils de classification des virages.
    #
    #  @param   cfg  Configuration OmegaConf issue de configDemoPilote.yaml.
    #                Utilise les clés virages.drift, virages.serrer.i1/i2
    #                et virages.moyen.i1/i2.
    def __init__(self, cfg):

        ## @var seuildrift
        #  @brief Seuil de courbure au-delà duquel le virage est considéré très serré.
        self.seuildrift = cfg.virages.drift

        ## @var serreri1
        #  @brief Borne inférieure de l'intervalle des virages serrés.
        self.serreri1 = cfg.virages.serrer.i1

        ## @var serreri2
        #  @brief Borne supérieure de l'intervalle des virages serrés.
        self.serreri2 = cfg.virages.serrer.i2

        ## @var moyeni1
        #  @brief Borne inférieure de l'intervalle des virages moyens.
        self.moyeni1 = cfg.virages.moyen.i1

        ## @var moyeni2
        #  @brief Borne supérieure de l'intervalle des virages moyens.
        self.moyeni2 = cfg.virages.moyen.i2

        ## @var anticipe_kart
        #  @brief Instance utilisée pour mesurer la courbure à chaque step.
        self.anticipe_kart = AnticipeKart()
        # configuration des valeurs attribuées aux attributs d'instance
        self.amax = 1.0
        self.virage_tres_serré = cfg.acceleration.virage_tres_serré
        self.virage_serré = cfg.acceleration.virage_serré
        self.virage_moyen = cfg.acceleration.virage_moyen
    ## @brief   Retourne l'accélération adaptée à la situation courante.
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #  @return  float : valeur d'accélération dans [0.0, 1.0].
    #  @see     AnticipeKart.detectVirage()
    def adapteAcceleration(self, obs):
        acceleration = self.amax
        curvature = abs(self.anticipe_kart.detectVirage(obs))  # valeur absolue de l'angle

        if curvature > self.seuildrift:
            # virage très serré : fort freinage anticipé
            acceleration = self.virage_tres_serré
        elif curvature > self.serreri1 and curvature <= self.serreri2:  # virage serré
            acceleration = self.virage_serré
        elif curvature > self.moyeni1 and curvature <= self.moyeni2:    # virage moyen
            acceleration = self.virage_moyen
        else:
            # ligne droite ou courbe très légère : pleine accélération
            acceleration = self.max

        return acceleration