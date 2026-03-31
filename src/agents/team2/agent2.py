## @file    agent2.py
#  @brief   Agent principal de pilotage automatique du kart (équipe 2).
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou et Maty Niang
#  @date    20-01-2026

import numpy as np
from agents.kart_agent import KartAgent
from omegaconf import OmegaConf
from .steering_piste import SteeringPiste
from .react_items import ReactionItems
from .rival_attack import AttackRivals
from .kart_rescue import StuckControl
from .acceleration_kart import AccelerationControl
from .shield_kart import ActiveShield
from .hit_rivals import HitRivals

## @var cfg
#  @brief Configuration globale chargée depuis configDemoPilote.yaml.
#         Contient les seuils de virage, les gains de correction et les angles d'items.
cfg = OmegaConf.load("../agents/team2/configDemoPilote.yaml")


## @class   Agent2
#  @brief   Agent de pilotage heuristique pour SuperTuxKart.
#
#  Agent2 orchestre plusieurs sous-modules spécialisés pour piloter le kart :
#  - SteeringPiste       : maintien au centre de la piste.
#  - ReactionItems       : gestion des items (collecte / évitement).
#  - AttackRivals        : utilisation des items offensifs contre les adversaires.
#  - StuckControl        : détection et sortie des situations de blocage.
#  - AccelerationControl : adaptation de l'accélération selon la courbure.
#  - ActiveShield        : activation du shield ou tir selon l'item possédé.
#
#  @see SteeringPiste
#  @see ReactionItems
#  @see AttackRivals
#  @see StuckControl
#  @see AccelerationControl
#  @see ActiveShield
class Agent2(KartAgent):

    ## @brief   Initialise l'agent et ses sous-modules de pilotage.
    #
    #  @param   env            Environnement Gymnasium de la course.
    #  @param   path_lookahead Nombre de nœuds anticipés devant le kart
    #                          pour calculer le steering. Par défaut 3.
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)

        ## @var path_lookahead
        #  @brief Nombre de nœuds de piste anticipés pour le calcul du steering.
        self.path_lookahead = path_lookahead

        ## @var steering
        #  @brief Module de correction latérale pour rester au centre de la piste.
        self.steering = SteeringPiste(cfg)

        ## @var items_steering
        #  @brief Module de réaction aux items présents sur la piste.
        self.items_steering = ReactionItems(cfg)

        ## @var attack_rival
        #  @brief Module de décision de tir sur les karts adversaires.
        self.attack_rival = AttackRivals()

        ## @var rescue_kart
        #  @brief Module de gestion des situations de blocage (marche arrière).
        self.rescue_kart = StuckControl(cfg)

        ## @var acceleration
        #  @brief Module d'adaptation de l'accélération selon la courbure.
        self.acceleration = AccelerationControl(cfg)

        ## @var active_shield
        #  @brief Module de gestion du shield et des items défensifs/offensifs.
        self.active_shield = ActiveShield()
        
        self.hit_rivals = HitRivals()

        ## @var agent_positions
        #  @brief Historique des positions du kart (utilisé pour la visualisation).
        self.agent_positions = []

        ## @var obs
        #  @brief Dernière observation reçue de l'environnement.
        self.obs = None

        ## @var isEnd
        #  @brief Indique si le kart a terminé la course.
        self.isEnd = False

        ## @var name
        #  @brief Nom affiché du pilote dans l'interface de la course.
        self.name = "DemoPilote "

    ## @brief   Réinitialise l'état de l'agent pour une nouvelle course.
    #
    #  Remet à zéro les positions enregistrées et les compteurs de blocage.
    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        self.stuck_steps = 0
        self.recovery_steps = 0

    ## @brief   Indique si la course est terminée pour ce kart.
    #  @return  bool : True si le kart a franchi la ligne d'arrivée, False sinon.
    def endOfTrack(self):
        return self.isEnd

    ## @brief   Calcule l'action complète à effectuer pour le step courant.
    #
    #  Fusionne les décisions de tous les sous-modules dans l'ordre de priorité :
    #  1. Sortie de blocage (StuckControl)              — priorité absolue.
    #  2. Steering vers le nœud cible (path_lookahead nœuds devant).
    #  3. Nitro si énergie disponible et trajectoire droite.
    #  4. Correction de centrage (SteeringPiste).
    #  5. Accélération adaptée au virage (AccelerationControl).
    #  6. Réaction aux items (ReactionItems).
    #  7. Attaque des adversaires si item en main (ActiveShield).
    #
    #  Le steer final est la somme clampée dans [-1, 1] de :
    #  item_steering + correction_piste + steering_lookahead.
    #
    #  @param   obs  Dictionnaire d'observation retourné par l'environnement.
    #  @return  dict : action contenant les clés :
    #           - "acceleration" (float [0,1])  : intensité d'accélération.
    #           - "steer"        (float [-1,1]) : angle de braquage.
    #           - "brake"        (bool)         : activer le frein / marche arrière.
    #           - "drift"        (bool)         : activer le drift.
    #           - "nitro"        (bool)         : activer le boost nitro.
    #           - "rescue"       (bool)         : appeler l'oiseau de secours.
    #           - "fire"         (bool)         : utiliser l'item offensif.
    #  @see     StuckControl.gerer_recul()
    #  @see     SteeringPiste.correction_centrePiste()
    #  @see     AccelerationControl.adapteAcceleration()
    #  @see     ReactionItems.reaction_items()
    #  @see     ActiveShield.fire_shield()
    def choose_action(self, obs):
        velocity = np.array(obs["velocity"])
        speed = np.linalg.norm(velocity)

        # Priorité absolue : sortie de blocage (marche arrière si nécessaire)
        action_secours = self.rescue_kart.gerer_recul(obs, speed, self.steering)
        if action_secours is not None:
            return action_secours

        nodes_path = obs.get("paths_start", [])

        # Calcul du steering vers le nœud cible
        if len(nodes_path) > self.path_lookahead:
            target_node = nodes_path[self.path_lookahead]
            angle_target = np.arctan2(target_node[0], target_node[2])
            steering = np.clip(angle_target * 2, -1, 1)
        else:
            steering = 0

        attack_karts = self.hit_rivals.hit_karts(obs)       
        if attack_karts is not None:
            return attack_karts


        # Activation de la nitro en ligne droite si énergie disponible
        nitro = obs["energy"][0] > 0 and abs(steering) < 0.2

        # Correction latérale pour rester au centre de la piste
        correction_piste = self.steering.correction_centrePiste(obs)

        # Adaptation de l'accélération selon la courbure détectée
        acceleration = self.acceleration.adapteAcceleration(obs)

        # Ajustement du steering selon les items visibles sur la piste
        item_steering = self.items_steering.reaction_items(obs)

        # Steering final : somme pondérée clampée dans [-1, 1]
        final_steering = np.clip(item_steering + correction_piste + steering, -1, 1)

        # Tir de l'item si un adversaire est dans le champ de vision
        has_item = obs.get("attachment", 0) != 0
        fire = has_item and self.active_shield.fire_shield(obs)
        #drift = self.acceleration.decideDrift(obs)
        
        return {
            "acceleration": acceleration,
            "steer":        final_steering,
            "brake":        False,
            "drift":        False,
            "nitro":        nitro,
            "rescue":       False,
            "fire":         fire,
        }