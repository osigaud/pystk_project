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
#  - Virage très serré (> cfg.virages.drift)        : cfg.acceleration.virage_tres_serré
#  - Virage serré      (cfg.virages.serrer.i1 à i2) : cfg.acceleration.virage_serré
#  - Virage moyen      (cfg.virages.moyen.i1 à i2)  : cfg.acceleration.virage_moyen
#  - Ligne droite      (courbure faible)             : 1.0
#
#  Les valeurs d'accélération sont optimisées automatiquement par Optuna.
#
#  @see AnticipeKart
class AccelerationControl(AnticipeKart):

    ## @brief   Initialise les seuils de classification des virages.
    #
    #  @param   cfg  Configuration OmegaConf issue de configDemoPilote.yaml.
    #                Utilise les clés virages.drift, virages.serrer.i1/i2,
    #                virages.moyen.i1/i2 et acceleration.virage_*.
    def __init__(self, cfg):
        super().__init__()

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

        ## @var amax
        #  @brief Accélération maximale appliquée en ligne droite (toujours 1.0).
        self.amax = 1.0

        ## @var virage_tres_serré
        #  @brief Accélération appliquée lors d'un virage très serré, optimisée par Optuna.
        self.virage_tres_serré = cfg.acceleration.virage_tres_serré

        ## @var virage_serré
        #  @brief Accélération appliquée lors d'un virage serré, optimisée par Optuna.
        self.virage_serré = cfg.acceleration.virage_serré

        ## @var virage_moyen
        #  @brief Accélération appliquée lors d'un virage moyen, optimisée par Optuna.
        self.virage_moyen = cfg.acceleration.virage_moyen

    ## @brief   Retourne l'accélération adaptée à la situation courante.
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #  @return  float : valeur d'accélération dans [0.0, 1.0].
    #  @see     AnticipeKart.detectVirage()
    def adapteAcceleration(self, obs):
        acceleration = self.amax
        curvature = abs(self.detectVirage(obs))

        if curvature > self.seuildrift:
            acceleration = self.virage_tres_serré
        elif curvature > self.serreri1 and curvature <= self.serreri2:
            acceleration = self.virage_serré
        elif curvature > self.moyeni1 and curvature <= self.moyeni2:
            acceleration = self.virage_moyen
        else:
            acceleration = self.amax

        return acceleration