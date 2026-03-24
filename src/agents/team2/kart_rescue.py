## @file    kart_rescue.py
#  @brief   Détection de blocage et gestion de la marche arrière.
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou et Maty Niang
#  @date    20-01-2026


import numpy as np


## @class   StuckControl
#  @brief   Surveille la vitesse du kart et déclenche un recul si nécessaire.
#
#  Si le kart reste sous le seuil de vitesse pendant trop de steps consécutifs,
#  une séquence de marche arrière est activée pour le dégager.
#  Doit être appelé en priorité absolue dans choose_action().
class StuckControl:

    ## @brief   Initialise les paramètres de détection et de récupération.
    #
    #  @param   cfg  Configuration OmegaConf issue de configDemoPilote.yaml.
    #                Utilise les clés : vitesse, steps, recovery, braquage.
    def __init__(self, cfg):

        ## @var stuck_steps
        #  @brief Compteur de steps consécutifs où le kart est quasi-immobile.
        self.stuck_steps = 0

        ## @var recovery_steps
        #  @brief Nombre de steps restants dans la séquence de marche arrière.
        self.recovery_steps = 0

        ## @var en_marche_arriere
        #  @brief Vrai quand une séquence de recul est en cours.
        self.en_marche_arriere = False

        ## @var recovery
        #  @brief Durée totale de la marche arrière en nombre de steps.
        self.recovery = cfg.recovery

        ## @var steps
        #  @brief Nombre de steps immobiles avant de déclencher le recul.
        self.steps = cfg.steps

        ## @var vitesse
        #  @brief Seuil de vitesse (m/s) en dessous duquel le kart est considéré bloqué.
        self.vitesse = cfg.vitesse

        ## @var braquage
        #  @brief Amplitude du braquage appliqué pendant la marche arrière.
        self.braquage = cfg.braquage

    ## @brief   Vérifie si le kart est bloqué et gère la manœuvre de recul.
    #
    #  Doit être appelé en premier dans choose_action().
    #  Si le kart n'est pas bloqué, retourne None.
    #
    #  @param   obs      Dictionnaire d'observation retourné par l'environnement.
    #  @param   vitesse  Vitesse scalaire courante du kart (norme du vecteur vitesse).
    #  @param   steering Instance de SteeringPiste pour calculer le braquage de recul.
    #  @return  dict : action de marche arrière si le kart est bloqué, None sinon.
    #  @see     SteeringPiste.correction_centrePiste()
    def gerer_recul(self, obs, vitesse, steering):
        phase = obs.get("phase", 0)

        # on ne compte les blocages qu'en phase de course pour ignorer le compte à rebours
        if vitesse < self.vitesse and phase > 2:  # si vitesse nulle après le départ
            self.stuck_steps += 1
        else:
            self.stuck_steps = 0

        # déclenchement de la marche arrière si le seuil est dépassé
        if self.stuck_steps > self.steps and not self.en_marche_arriere:  # temps de decision d'activer marche arriere
            self.en_marche_arriere = True
            self.recovery_steps = self.recovery  # durée de la marche arriere

        if self.en_marche_arriere:  # execution de marche arriere
            self.recovery_steps -= 1

            # fin de la séquence : on reprend la conduite normale
            if self.recovery_steps <= 0:
                self.en_marche_arriere = False

            # on braque vers le centre de la piste pendant le recul
            # correction > 0 signifie que le centre est à droite
            correction = steering.correction_centrePiste(obs)
            braquage_arriere = self.braquage if correction > 0 else -self.braquage  # braquage

            return {
                "acceleration": 0.0,
                "steer": braquage_arriere,
                "brake": True,   # brake=True active la marche arrière dans STK
                "drift": False,
                "nitro": False,
                "rescue": False,
                "fire": False,
            }

        return None  # kart non bloqué, l'agent reprend la main