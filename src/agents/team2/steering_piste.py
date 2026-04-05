## @file    steering_piste.py
#  @brief   Module de correction latérale pour maintenir le kart au centre de la piste.
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou, Maty Niang
#  @date    20-01-2026

import numpy as np


## @class   SteeringPiste
#  @brief   Calcule la correction de steer pour maintenir le kart au centre de la piste.
#
#  Utilise le nœud de piste situé 2 positions devant le kart
#  (obs["paths_start"][2]) pour calculer l'angle de correction.
class SteeringPiste:

    ## @brief   Initialise le module avec le gain de correction configuré.
    #
    #  @param   cfg  Configuration OmegaConf chargée depuis configDemoPilote.yaml.
    #                Doit contenir la clé "correction".
    def __init__(self, cfg):

        ## @var correction
        #  @brief Gain multiplicatif appliqué à l'angle de correction.
        #         Plus la valeur est élevée, plus la correction est agressive.
        self.correction = cfg.correction

    ## @brief   Calcule la correction latérale pour rester au centre de la piste.
    #
    #  Récupère le nœud de piste à l'index 2 dans le référentiel du kart,
    #  calcule l'angle arctan2(x, z) vers ce point, applique le gain,
    #  puis clamp le résultat dans [-0.6, 0.6].
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #                Doit contenir la clé "paths_start" avec au moins 3 éléments.
    #  @return  float : correction de steer dans [-0.6, 0.6].
    #                   Retourne 0.0 si pas assez de nœuds disponibles
    #                   ou si le nœud cible est derrière le kart (z <= 0).
    #  @note    Le clamp à ±0.6 simule la limite physique du volant.
    #  @see     Agent2.choose_action()
    def correction_centrePiste(self, obs):
        # si paths_start n'existe pas, on renvoie 0 et on veut qu'il y ait au moins 3 points devant le kart
        if "paths_start" not in obs or len(obs["paths_start"]) < 3:
            return 0.0

        # le point au centre de la piste juste devant le kart
        point_proche_kart = obs["paths_start"][1]
        x = point_proche_kart[0]  # coordonnées du point qui nous indique gauche ou droite
        z = point_proche_kart[2]  # coordonnées du point qui nous indique devant ou derrière

        if z <= 0.0:
            return 0.0

        # angle qu'il faut tourner pour atteindre le point
        angle_vers_centre = np.arctan2(x, z)

        # if abs(angle_vers_centre)<0.03:
        #     return 0.0

        correction = angle_vers_centre #* self.correction

        # np.clip = barrière de sécurité : sécurise pour que le résultat ne dépasse pas
        # l'intervalle [-0.6, 0.6] (limites physiques du volant)
        return np.clip(correction, -0.6, 0.6)