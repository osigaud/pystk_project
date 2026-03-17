from .steering import Steering

class AgentBanana:

    """
    Module Agent Expert Banana : Gère la logique de détection et de réaction face aux bananes et chewing-gum
    """
    
    def __init__(self,config,config_pilote):
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.c = config
        """@private"""
        self.dodge_side = 0
        """@private"""
        self.dodge_timer = self.c.dodge_timer_basic
        """@private"""
        self.lock_mode = None
        """@private"""
        self.locked_gx = 0.0
        """@private"""
        self.pilotage = Steering(config_pilote)
        """@private"""
        
    def reset(self) -> None:
        
        """Réinitialise les variables d'instances de l'agent expert"""
        
        self.dodge_side = 0
        self.dodge_timer = 0
        self.lock_mode = None
        self.locked_gx = 0.0
        self.pilotage.reset()
        
    def banana_detection(self,obs : dict,limit_path : float,center_path : float) -> tuple[str,float,list]:
        """
        
        Gère la logique de détection des obstacles (bananes et chewing-gums)

        Args:
                
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            limit_path(float) : La largeur maximale autorisée sur la piste.
            center_path(float) : Position du centre de la piste par rapport au kart.

        Returns:
            
            str : Le mode de détection ("CLEAR", "SINGLE" ou "LIGNE").
            float : La coordonnée X cible (décalage latéral ou centre du gap).
            list : La liste des positions (x, z) des bananes détectées dans le radar.
        
        """

        items_pos = obs['items_position'] # Récupération des positions des items
        items_type = obs['items_type'] # Récupération des types des items

        banana = [] # Liste qui va accueillir nos bananes

        for i in range(len(items_pos)):
            if items_type[i] == 1 or items_type[i] == 4: # Si c'est une banane ou une chewing-gum
                pos_x = items_pos[i][0] # On récupère le décalage latéral 
                pos_z = items_pos[i][2] # On récupère la profondeur

                dist_obj_centre= abs(center_path+pos_x) #Calcul de la distance absolu de l'objet

                if dist_obj_centre > limit_path: # Si l'objet est hors des limites de la piste, on ne le prend pas en compte
                    continue

                if -self.c.radar_x <= pos_x <= self.c.radar_x and self.c.radar_zmin <= pos_z <= self.c.radar_zmax: # Si la banana est dans notre radar, on l'ajoute dans notre liste
                    banana.append((pos_x,pos_z))

        banana.sort(key=lambda x: x[1]) # On trie la liste par ordre croissant selon la profondeur

        if len(banana) == 0: # Rien à signaler
            return "CLEAR",None,None
        
        first = banana[0] # On récupère la banane la plus proche
        first_x = first[0]
        first_z = first[1]

        if len(banana) >=2: #Si on a plus de deux bananes dans notre liste
            second = banana[1] # On récupère la seconde
            x = second[0]
            z = second[1]
            if abs(z-first_z) <= self.c.seuil_ligne: # Si les bananes forment une ligne (un barrage)
                gap_x = (x+first_x)/2.0
                return "LIGNE", gap_x, banana
            else:
                return "SINGLE", first_x,banana # On revient sur le cas de la banane seule
        else:
            return "SINGLE",first_x,banana # Cas d'une seule banane
        
    
    def choose_action(self,obs : dict,gx : float ,gz : float,acceleration : float) -> tuple[bool,dict]:

        """
        
        Gère la logique de réaction à la détection des obstacles (bananes et chewing-gums)

        Args:
                
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            gx(float) : Décalage latéral actuel de la cible.
            gz(float) : Profondeur actuel de la cible.
            acceleration(float) : Accéleration de l'agent.

        Returns:
            
            bool : Permet de confirmer la présence d'un obstacle et la nécessité de l'esquiver.
            dict : Le dictionnaire d'actions à réaliser pour esquiver une banane.
        
        """

        paths_width = obs.get("paths_width",0.0)
        center_path_distance = obs.get("center_path_distance",0.0)
        limit_path = paths_width[0]/2 # Limite de la piste calculée

        # Appel de la fonction de détection
        mode, b_x, banana_list = self.banana_detection(obs,limit_path,center_path_distance)

        gain_volant = self.c.default_gain # Gain par défaut

        if mode == "CLEAR" and self.dodge_timer <= 0:
            self.lock_mode = None # On réinitialise l'état
            return False, {}
        
        if mode == "SINGLE" and self.lock_mode != "LIGNE": # Si on a capte un cas d'une banane seule et qu'on était pas déjà dans une situation d'esquive de barrage

            #print(banana_list)
            
            #Sécurité pour éviter de sortir de la piste
            if (limit_path - abs(center_path_distance)) <= self.c.seuil_limite_path :
                #print("choix par limite de bord")
                #print(limit_path, center_path_distance)
                
                # ATTENTION LOGIQUE INVERSEE POUR CENTER PATH, si > 0 l'agent se situe à droite de la piste
                if center_path_distance >= 0:
                    new_side = -1
                else:
                    new_side = 1
            else:   
                #print("choix normal")
                if b_x>=0:
                    new_side = -1
                    
                else:
                    new_side = 1
            
            # Utilisation d'un compteur pour maintenir le cap d'esquive sur x frames
            if self.dodge_timer == 0 or (self.lock_mode == "SINGLE" and self.dodge_side != new_side):
                self.lock_mode = "SINGLE"
                self.dodge_timer = self.c.dodge_timer_start
                self.dodge_side = new_side

        elif mode == "LIGNE": #Si on a capte un mode ligne
            self.lock_mode = "LIGNE"
            self.dodge_timer = self.c.dodge_timer_basic
            self.locked_gx = b_x
            #print(banana_list)
            #print("Esquive Ligne")

        if self.dodge_timer >0: # On est dans le mode Single
            #print("Esquive SINGLE")
            self.dodge_timer -= 1 # On decremente le compteur
            gx += self.c.decalage_lateral * self.dodge_side # On cree le decalage pour le cas single
            
        elif (mode == "SINGLE" or mode == "LIGNE") and self.lock_mode == "LIGNE":
            #print("Esquive LIGNE")
            gx = self.locked_gx # On vise le gap calculé pour le mode ligne
            gain_volant = self.c.adjusted_gain # Ajustement du gain pour le mode ligne

        # Appel de la fonction de steering avec les paramètres modifiés.
        steering = self.pilotage.manage_pure_pursuit(gx,gz,gain_volant)

        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue":False,
            "fire": False,
        }

        return True,action
        