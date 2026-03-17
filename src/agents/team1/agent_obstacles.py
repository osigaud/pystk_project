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
        for i in range(len(obs["items_type"])) :
            vecteur_item = obs["items_position"][i]
            type_item = obs["items_type"][i]
            if (2 < vecteur_item[self.conf.z] < 15) and (abs(vecteur_item[self.conf.y]) < 1) :
                if (abs(vecteur_item[self.conf.x]) < 1.5) and type_item in self.conf.obstacles : 
                    action = self.dodge_obstacle(obs, action, i)
                    return action
                #elif (abs(vecteur_item[self.conf.x]) < 3) and type_item in self.conf.bonus: 
                    #action = self.take_bonus(obs, action, i)
        return action

    def dodge_obstacle(self, obs, action, index) : 
        """Évite un obstacle donné (sauf si un shield est actif).

<<<<<<< HEAD
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
        vecteur_item = obs["items_position"][index]
        if vecteur_item[self.conf.x] >= 0 : 
            action["steer" ] -= 1
        else : 
            action["steer"] += 1
        action["steer"] = np.clip(action["steer"], -1, 1) 
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
        vecteur_item = obs["items_position"][index]
        next_node = obs["paths_end"][self.path_lookahead]
        #si l'item n'est pas dans le même sens que le prochain virage
        if vecteur_item[self.conf.x] * next_node[self.conf.x] < 0 : 
            return action
        
        steer = vecteur_item[self.conf.x]
        steer = np.clip(steer, -1, 1)
        action["steer"] = steer
        return action

    def evite_ennemi(self, obs, action) :
        """Dévie légèrement le kart si on est collé à un kart ennemi en face

        Args:
            obs (dict): Observations (utilise `karts_position`).
            action (dict): Action courante (modifie "steer").
        
        Returns:
            dict: Action corrigée (steer dévié d'un possible kart en face de nous).
        """
        for kart in obs["karts_position"] :
            if abs(kart[self.conf.x]) < 0.8 and 0 < kart[self.conf.z] < 1 :
                if action["steer"] >= 0 :
                    action["steer"] += 0.3
                else :
                    action["steer"] -= 0.3
                action["steer"] = np.clip(action["steer"], -1, 1)
                return action
        return action
        
    def choose_action(self, obs) : 
        """
        Paramètres : obs
        Renvoie : action (dict), dictionnaire d'actions corrigé après prise en compte des obstacles et bonus
        """
        action = self.agent.choose_action(obs)
        action = self.observation_next_item(obs, action)
        action = self.evite_ennemi(obs, action)
        return action
