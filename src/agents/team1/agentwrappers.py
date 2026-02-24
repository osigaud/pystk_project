import numpy as np
import random
import math
from omegaconf import OmegaConf

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

from pathlib import Path

#chemin du fichier de configuration
path_conf = Path(__file__).resolve().parent
path_conf = str(path_conf) + '/configFIleTastyCrousteam.yaml'
#importation du fichier de configuration
conf = OmegaConf.load(path_conf)

#définition des variables qui viennent du fichier de configuration
DIST = 0.673833673012193
AJUST = 0.6386812473361506
ECARTPETIT = conf.ecartpetit
ECARTGRAND = conf.ecartgrand
MSAPETIT = conf.msapetit
MSAGRAND = conf.msagrand

#autres variables qu'on utilise dans le code 
BONUS = [0, 2, 3]
OBSTACLES = [1, 4]

#template de base d'Agent, mouvements aléatoires, initialisation des variables
class AgentInit(KartAgent):
    #variables à définir dans le fichier de configuration : 
    #   - accélération par défaut
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Tasty Crousteam"

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        acceleration = random.random()
        steering = random.random()
        action = {
            "acceleration": 1,
            "steer": 0,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }
        return action

#Agent qui suit le centre de la piste
class AgentCenter(AgentInit):

    """Agent de base chargé de maintenir le kart au centre de la piste.

    L’agent utilise les observations de l’environnement (notamment les points de la piste
    `paths_start` / `paths_end` et la distance au centre) pour corriger la direction
    (`steer`). Il applique une correction progressive proportionnelle à l’écart
    latéral pour ramener le kart vers le centre tout en limitant l’angle de braquage (pour éviter les "zig zag").
    """

    def __init__(self, env, path_lookahead=3):
        super().__init__(env, path_lookahead)
        self.dist = DIST 
        self.ajust = AJUST 

    def path_ajust(self, act, obs):
        """
        Ajuste la direction du kart pour suivre le centre de la piste.

        Args:
            act (dict): Dictionnaire des actions du kart (ex: {"steer": float}).
            obs (dict): Observations de l’environnement contenant notamment
                    "paths_end" et "center_path_distance".

        Returns:
            dict: Dictionnaire des actions corrigé avec une valeur de
                "steer" comprise entre -1 et 1.
        """
        steer = act["steer"]
        center = obs["paths_end"][2]
        if (center[2] > 20 and abs(obs["center_path_distance"]) < 3) : 
            steer = 0
        elif abs(center[0]) > self.dist : 
            steer += self.ajust * center[0]
        act["steer"] = np.clip(steer, -1, 1)
        return act
    
    def choose_action(self, obs):
        """
        Sélectionne une action puis applique une correction de trajectoire.

        Args:
            obs (dict): Observations de l’environnement.

        Returns:
            dict: Dictionnaire d’action corrigé.
    """
        act = super().choose_action(obs)
        act_corr = self.path_ajust(act, obs)
        return act_corr
            
#Agent qui adapte la vitesse en fonction des virages
class AgentSpeed(AgentCenter):
    

    """Agent qui adapte la vitesse en fonction de la forme de la piste dans les prochaines secondes (ligne droite ou virage?).

    Cet agent hérite de AgentCenter (qui gère le maintien au centre de la piste)
    et ajoute un comportement de gestion de l'accélération selon les
    segments de piste devant le kart (ligne droite vs virage serré).

    Attributes:
        ecartpetit (float): Seuil en dessous duquel on considère que l'écart de direction
            est faible (ligne droite).
        ecartgrand (float): Seuil à partir duquel l'écart est grand (virage serré).
        msapetit (float): Seuil bas sur obs["max_steer_angle"] pour moduler l'accélération.
        msagrand (float): Seuil haut sur obs["max_steer_angle"] pour moduler l'accélération.
    """



    def __init__(self, env, path_lookahead=3):
        super().__init__(env, path_lookahead)
        self.ecartpetit = ECARTPETIT #seuil a partir du quel on considere l'ecart comme petit (ligne droite)o
        self.ecartgrand = ECARTGRAND #seuil a partir du quel on considere l'ecart comme grand (virage serré)
        self.msapetit = MSAPETIT
        self.msagrand = MSAGRAND
        
    def analyse(self, obs):
        """Analyse la piste devant le kart et classe la situation.

        La méthode inspecte jusqu'à `path_lookahead`(on choisi 3) segments (paths_start/end) et
        estime un "écart" entre la direction des segments et le vecteur `obs["front"]`.
        Si un segment proche correspond à un écart élevé, on detecte un virage serré.

        Args:
            obs (dict): Observations de l’environnement. Clés typiques utilisées :
                - paths_start (list/array): points de début des segments.
                - paths_end (list/array): points de fin des segments.
                - front (array): direction actuelle du kart (vecteur).
                - paths_distance (list): distances latérales  associees aux segments.

        Returns:
            str: "ligne droite" ou "virage serre".
        """
        s = []
       	nbsegments = min(self.path_lookahead, len(obs["paths_start"]))
       	for i in range(nbsegments):
       		segdirection = obs["paths_end"][i] - obs["paths_start"][i]
       		diff = segdirection - obs["front"]
       		ecart = float(np.linalg.norm(diff))
       		dist = abs(obs["paths_distance"][i][0] - obs["paths_distance"][0][0])
        		
        	if ecart >= self.ecartgrand and dist < 10:
        		s.append("virage serre")
       		elif ecart <= self.ecartpetit:
       			s.append("ligne droite") 
        	
       	react = "ligne droite"
       	if "virage serre" in s: 
       		react = "virage serre"
       		return react
       	else: 
       		return react

    def gap(self, acceleration) : 
        """Borne l'accélération dans une plage utile.

        Au-dessus ou égal à 1, on force à 1
        En dessous ou égal à 0, on impose un minimum (0.1)

        Args:
            acceleration (float): Valeur d'accélération à l'instant.

        Returns:
            float: Accélération bornée.
        """
        if acceleration >= 1 : 
            return 1
        if acceleration <= 0 : 
            return 0.1
        return acceleration
        		
    def reaction(self, react, act, obs):
        """Modifie l'action `act` en fonction du contexte.

        Ajuste principalement `act["acceleration"]` selon :
        - le type de trajectoire ("ligne droite" / "virage serre")
        - `obs["max_steer_angle"]` (indicateur de la difficulté du virage)
        - une pente éventuelle dans laquelle il faut accélerer(via segdirection[1])

        Args:
            react (str): Résultat de `analyse` ("ligne droite" ou "virage serre").
            act (dict): Action courante (doit contenir "acceleration").
            obs (dict): Observations (doit contenir "max_steer_angle", "paths_start/end"...).

        Returns:
            dict: Action corrigé (accélération bornée via `gap`).
        """
        msa = obs["max_steer_angle"]
            
        if react == "ligne droite":
            act["acceleration"] = 1
            
            segdirection = obs["paths_end"][0] - obs["paths_start"][0]
            if segdirection[1] > 0.05:
            	act["acceleration"] = self.gap(act["acceleration"] + 0.2)
            	
            return act
                    
        if react == "virage serre":
            if msa <= self.msapetit: 
                accel = act["acceleration"]
                accel = accel - 0.45
                act["acceleration"] = self.gap(accel)
            elif self.msapetit < msa < self.msagrand:
            	return act
            elif msa >= self.msagrand:
                accel = act["acceleration"]
                accel = accel + 0.5
                act["acceleration"] = self.gap(accel)
                
            segdirection = obs["paths_end"][0] - obs["paths_start"][0]
            if segdirection[1] > 0.05:
            	act["acceleration"] = self.gap(act["acceleration"] + 0.2)
            	
            return act
  
    def choose_action(self, obs):
        act = super().choose_action(obs)
        react = self.analyse(obs)
        act_corr = self.reaction(react, act, obs)
        return act_corr

#Agent qui analyse les obstacles et bonus sur la course et corrige sa trajectoire en conséquences
class AgentObstacles(AgentCenter) : 

    """Agent qui gere les obstacles et les bonus en corrigeant la trajectoire.

    L'agent hérite de AgentCenter (suivi du centre de piste) et applique ensuite
    une correction de direction pour :
    - éviter les obstacles détectés
    - se diriger vers des bonus (items) si c'est pertinent

    Attributes:
        target_obstacle (int | None): Index de l'obstacle actuellement ciblé .
        target_item (int | None): Index du bonus actuellement ciblé.
    """


    def __init__(self, env, path_lookahead=3): 
        super().__init__(env, path_lookahead)
        self.target_obstacle = None
        self.target_item = None

    def observation_next_item(self, obs, action) : 
        """Analyse les items visibles (bonus/obstacles) et corrige l'action soit en s'en approchant ou soit en esquivant.

        La méthode :
        1) repère les indices des items bonus et obstacles via `obs["items_type"]`
        2) applique d'abord l'évitement des obstacles
        3) puis (si possible) l'alignement vers un bonus

        Args:
            obs (dict): Observations de l’environnement. Clés utilisées typiquement :
                - items_type (list[int] | list[str]): type de chaque item détecté.
                - items_position (list[array]): vecteur position de chaque item (x, y, z) dans le repère du kart.
            action (dict): Dictionnaire d'action courant (au minimum "steer").

        Returns:
            dict: Action corrigée après prise en compte des bonus et obstacles.
        """
        tab_bonus = [i for i in range(len(obs["items_type"])) if obs["items_type"][i] in BONUS]
        tab_obstacles = [i for i in range(len(obs["items_type"])) if obs["items_type"][i] in OBSTACLES]

        """
        for i in range(len(obs["items_type"])) :
            nextitem_type = obs["items_type"][i]
            #if nextitem_vector[2] < 17 and nextitem_vector[2] > 3 and abs(nextitem_vector[1]) < 10 : 
            if nextitem_type in BONUS : 
                action = self.take_bonus(obs, action)
            elif nextitem_type in OBSTACLES : 
                return action
                action = self.dodge_obstacle(obs, action)
        """
        for index in tab_obstacles :
            action = self.dodge_obstacle(obs, action, index)

        for index in tab_bonus : 
            action = self.take_bonus(obs, action, index)
        return action

    def dodge_obstacle(self, obs, action, index) : 
        """Évite un obstacle donné (sauf si un shield est actif).

        La logique conserve une cible (`target_obstacle`) pour éviter de changer
        d'obstacle ciblé à chaque frame. Si l'obstacle n'est plus pertinent
        (trop proche, hors zone, ou autre), la cible est remise a None.

        Args:
            obs (dict): Observations (utilise `items_position`, `attachment`, `attachment_time_left`).
            action (dict): Action courante (modifie "steer").
            index (int): Index de l'obstacle dans `obs["items_type"]` / `obs["items_position"]`.

        Returns:
            dict: Action corrigée (steer modifié pour dévier de l'obstacle).
        """
        if self.target_obstacle is None : 
            self.target_obstacle = index

        item_vector = obs["items_position"][index]
        if -1 < item_vector[2] < 1 or not ((abs(item_vector[0]) < 3.5) and (0 < item_vector[2] < 20) and (abs(item_vector[1]) < 10)): 
            self.target_obstacle = None

        if (self.target_obstacle == index):
            if (obs["attachment"] == 6 and obs["attachment_time_left"] > 2) : 
                #6 : BUBBLEGUM_SHIELD
                #à tester ici quand on aura un shield activé
                return action
    
            if item_vector[0] >= 0 : 
                action["steer"] = action["steer"] - 1
            else : 
                action["steer"] = action["steer"] + 1
        return action

    def take_bonus(self, obs, action, index) :
        """Se dirige vers un bonus (item) s'il n'y a pas d'autre priorité et s'il est pertinent de le récupérer.

        La méthode conserve une cible (`target_item`). Elle ignore un item si :
        - il est trop proche / trop loin / hors zone latérale
        - il détourne trop de la trajectoire (comparaison avec un noeud de piste)
        - un obstacle est actuellement ciblé (priorité à la sécurité)

        Args:
            obs (dict): Observations (utilise `items_position`, `paths_end`).
            action (dict): Action courante (modifie "steer").
            index (int): Index du bonus dans `obs["items_type"]` / `obs["items_position"]`.

        Returns:
            dict: Action corrigée (steer orienté vers l'item si conditions remplies).
        """
        if self.target_item is None : 
            self.target_item = index

        item_vector = obs["items_position"][index]
        if item_vector[2] < 3 or not((abs(item_vector[0]) < 3) and (3 < item_vector[2] < 16) and (abs(item_vector[1]) < 10)) : 
            self.target_item = None

        next_node = obs["paths_end"][self.path_lookahead]
        node_item_gap_vector = next_node - item_vector #vecteur pour mesurer l'écart entre l'item et le prochain noeud
        #si l'écart est trop grand, on ne détourne pas du chemin de base

        if (self.target_item == index) and (node_item_gap_vector[2] <= (next_node[2] - 1)) and (self.target_obstacle is None) :
            next_node = obs["paths_end"][0]
            node_item_gap_vector = next_node - item_vector
            #if 0 < node_item_gap_vector[2] < next_node[2] : #optimisation ici ? 
            #if abs(item_vector[0] - action["steer"]) < 0.1 :
                #return action
            #else : 
            action["steer"] = item_vector[0]
        return action
        
    def choose_action(self, obs) : 
        """
        Paramètres : obs
        Renvoie : action (dict), dictionnaire d'actions corrigé après prise en compte des obstacles et bonus
        """
        action = super().choose_action(obs)
        action = self.observation_next_item(obs, action)
        return action

class AgentRescue(AgentObstacles) : 
    
    """Agent de secours chargé de détecter et faire reculer un kart qui est bloqué.

    Cet agent hérite de AgentObstacles et ajoute un mécanisme de détection
    de blocage basé sur la progression sur la piste (`distance_down_track`).
    Si le kart ne progresse plus pendant plusieurs itérations, l’agent déclenche
    une séquence de freinage afin de tenter de se débloquer.

    Attributes:
        last_distance (float | None): Dernière distance mesurée le long de la piste.
        block_counter (int): Nombre de frames consécutives sans progression significative.
        unblock_steps (int): Nombre d’actions restantes dans la séquence de déblocage.
        is_braking (bool): Indique si une phase de déblocage est en cours.
    """

    
    def __init__(self, env, path_lookahead=3): 
        super().__init__(env, path_lookahead)  
        self.last_distance = None
        self.block_counter = 0
        self.unblock_steps = 0
        self.is_braking = False

    def is_blocked(self, obs):
        """Détecte si le kart est bloqué et met à jour le compteur interne.

        Un blocage est détecté si la progression (`distance_down_track`)
        varie très peu pendant plusieurs frames, que le kart n’est pas en saut,
        et qu’il n’est pas affecté par certains items (ex: étourdissement).

        Args:
            obs (dict): Observations de l’environnement contenant notamment :
                - distance_down_track
                - jumping
                - attachment
        """

        distance_down_track = obs["distance_down_track"][0]
        attachment = obs["attachment"]
        if self.last_distance is None :
            self.last_distance = distance_down_track

        if abs(distance_down_track - self.last_distance) < 0.1 and distance_down_track > 5 and (obs["jumping"] == 0) and not (attachment == 2) :
            self.block_counter += 1
        else:
            self.block_counter = 0
            self.last_distance = distance_down_track

    def unblock_action(self, act):
        """Applique un recul pour tenter de débloquer le kart.

        Pendant un nombre limité de frames (`unblock_steps`), l’agent force
        une action de recul afin de sortir d’une situation de blocage.

        Args:
            act (dict): Action courante.

        Returns:
            dict: Action modifiée si une phase de déblocage est active,
                  sinon l’action originale.
        """
        if self.unblock_steps > 0 : 
            self.unblock_steps -= 1
            return {
                "acceleration" : 0, 
                "steer" : 0, 
                "brake" : True,
                "drift" : False,
                "nitro" : False,
                "rescue" : False,
                "fire" : False,
            }
        else : 
            self.is_braking = False
            return act
    
    def choose_action(self, obs):
        """Choisit une action et déclenche un déblocage si nécessaire.

        Étapes :
        1) Vérifie si le kart est bloqué.
        2) Récupère l’action normale (centre + obstacles).
        3) Si blocage est prolongé, lance un recul.

        Args:
            obs (dict): Observations de l’environnement.

        Returns:
            dict: Action finale appliquée au kart.
        """
        self.is_blocked(obs)
        action = super().choose_action(obs)   
                
        if self.block_counter > 18 :
            self.is_braking = True
            self.unblock_steps = 4
        if self.is_braking : 
            action = self.unblock_action(action)
        return action


#Agent qui derape quand la courbe est serree (virage serre)
class AgentDrift(AgentSpeed)  :

    """Agent qui active le drift dans les virages serrés.

    Hérite de AgentSpeed (gestion de la vitesse) et ajoute
    un comportement de dérapage lorsque :
    - un virage serré est détecté,
    - l'angle de direction est suffisamment important,
    - la vitesse est assez élevée.

    Le drift permet d'améliorer la prise de virage
    et de récuperer des boosts.
    """

    def __init__(self, env, path_lookahead = 3):
        super().__init__(env,path_lookahead)

    def drift_control(self, obs, action) :

        """Active ou désactive le drift selon la situation.

        Conditions d’activation :
        - Virage serré détecté via `analyse`
        - |steer| >= 0.5
        - vitesse > 6

        Args:
            obs (dict): Observations contenant notamment `velocity`.
            action (dict): Action courante (modifie la clé "drift").

        Returns:
            dict: Action avec le champ "drift" mis à True ou False.
        """
        
        virage_serre = self.analyse(obs)
        speed = np.linalg.norm(obs["velocity"])

        if virage_serre and abs(action["steer"]) >= 0.5 and speed > 6:
            action["drift"] = True
        else :
            action["drift"] = False

        return action

    def choose_action(self, obs) :
        action = super().choose_action(obs)
        action = self.drift_control(obs, action)
        return action
