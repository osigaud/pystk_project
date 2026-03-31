from .steering import Steering
from omegaconf import DictConfig

class AgentEdge:
    """
    Module Agent Expert Edge : Empêche la sortie de piste en surveillant la distance par rapport au centre.
    """
    def __init__(self,config : DictConfig ,config_pilote : DictConfig, path_lookahead : int):

        """Initialise les variables d'instances de l'agent expert"""
     
        self.conf = config
        """@private"""
        self.pilotage = Steering(config_pilote)
        """@private"""
        self.timer = 0
        """@private"""
        self.last_dist = None
        """@private"""
        self.duration = 0
        """@private"""
        self.path_lookahead = path_lookahead
        """@private"""

    def reset(self) -> None:

        """Réinitialise les variables d'instances de l'agent expert"""
        
        self.pilotage.reset()
        self.timer = 0
        self.last_dist = None
        self.duration = 0

    def choose_action(self, obs : dict) -> tuple[bool,dict]:
        """
        Analyse la position latérale et corrige si nécessaire

        Args:

            obs(dict) : Les données de télémétrie fournies par le simulateur.
        
        Returns:

            bool : Variable affirmant ou non la nécessite de se réaxer.
            dict : Dictionnaire d'actions à réaliser pour se réaxer.

        """
        # Récupération des données de piste
        cpd = obs.get("center_path_distance", 0.0)
        center_path_distance = cpd[0]
        
        pw = obs.get("paths_width", [10.0, 0.0, 0.0])
        limit_path = pw[0] / 2
        limit_path = limit_path[0]
        
        # Calcul de la marge de sécurité (Distance bord <-> Kart)
        marge_securite = limit_path - abs(center_path_distance)
        #print((limit_path - abs(center_path_distance))[0])
        
        points = obs.get("paths_start",[])

        target = points[self.path_lookahead] # On récupère le x-ème point de la liste defini par la variable de classe
        gx = target[0] # On récupère x, le décalage latéral
        gz = target[2] # On récupère z, la profondeur
        
        #print(f"Timer = {self.timer}")
        
        # Vérification de la sortie de piste imminente
        if marge_securite <= self.conf.epsilon_limite_max:
            if self.last_dist is None:
                self.timer+=1
            else:
                if marge_securite < self.last_dist: # Si on est en train de s'approcher du vide, on incremente le timer
                    self.timer+=1
                else:
                    self.timer = max(0,self.timer-1)
        else:
            self.timer=0
            self.last_dist = None

        self.last_dist = marge_securite
            
        # Si le timer a depasse 3, le danger est confirmé
        if self.timer >= self.conf.timer:

            #print(f"Marge = {marge_securite}, Limite = {limit_path}, Width = {pw[0]}") 
            self.duration = self.conf.duree
            self.timer = 0
            self.last_dist = None

        # On se réaxe sur x frames
        if self.duration > 0:

            self.duration-=1
            
            new_accel = self.conf.new_accel

            if center_path_distance > 0:
                gx-=self.conf.decalage_lateral
                #print("Danger !! On se reaxe vers la gauche") 
            else:
                #print("Danger !! On se reaxe vers la droite")
                gx+=self.conf.decalage_lateral

            steer = self.pilotage.manage_pure_pursuit(gx,gz,self.conf.gain)

            action = {
            "acceleration": new_accel,
            "steer": steer,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue":False,
            "fire": False,
            } 
            
            return True, action

        # Pas de danger, on laisse le pilote principal gérer
        return False, {}