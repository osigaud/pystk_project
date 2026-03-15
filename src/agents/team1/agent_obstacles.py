from agents.kart_agent import KartAgent
import numpy as np

class AgentObstacles(KartAgent) : 

    """Agent qui gere les obstacles et les bonus en corrigeant la trajectoire.
    
    Attributes:
        target_obstacle (int | None): Index de l'obstacle actuellement ciblé .
        target_item (int | None): Index du bonus actuellement ciblé.
    """


    def __init__(self, env, conf, agent, path_lookahead=3): 
        super().__init__(env)
        self.conf = conf
        self.agent = agent
        self.path_lookahead = path_lookahead
        self.target_obstacle = None
        self.target_item = None

    def observation_next_item(self, obs, action) : 
        """Analyse les items visibles (bonus/obstacles) et corrige l'action soit en s'en approchant ou soit en esquivant.

        1. repère les indices des items bonus et obstacles via `obs["items_type"]`
        2. applique d'abord l'évitement des obstacles
        3. puis (si possible) l'alignement vers un bonus

        Args:
            obs (dict): Observations de l’environnement. Clés utilisées typiquement :
                - items_type (list[int] | list[str]): type de chaque item détecté.
                - items_position (list[array]): vecteur position de chaque item (x, y, z) dans le repère du kart.
            action (dict): Dictionnaire d'action courant (au minimum "steer").

        Returns:
            dict: Action corrigée après prise en compte des bonus et obstacles.
        """
        tab_bonus = [i for i in range(len(obs["items_type"])) if obs["items_type"][i] in self.conf.bonus]
        tab_obstacles = [i for i in range(len(obs["items_type"])) if obs["items_type"][i] in self.conf.obstacles]

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

        Conserve une cible (`target_obstacle`) pour éviter de changer
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

        Même principe que dodge obstacles on conserve une cible pour éviter de changer de direction à chaque frame.

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
            """
            next_node = obs["paths_end"][0]
            node_item_gap_vector = next_node - item_vector
            if 0 < node_item_gap_vector[2] < next_node[2] : #optimisation ici ? 
            if abs(item_vector[0] - action["steer"]) < 0.1 :
                return action
            else : 
            """
            action["steer"] = item_vector[0]
        return action
        
    def choose_action(self, obs) : 
        """
        Paramètres : obs
        Renvoie : action (dict), dictionnaire d'actions corrigé après prise en compte des obstacles et bonus
        """
        action = self.agent.choose_action(obs)
        action = self.observation_next_item(obs, action)
        return action
