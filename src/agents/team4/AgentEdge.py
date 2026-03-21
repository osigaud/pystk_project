from .steering import Steering
from omegaconf import DictConfig

class AgentEdge:
    """
    Module Agent Expert Edge : Empêche la sortie de piste en surveillant la distance par rapport au centre.
    """
    def __init__(self,config : DictConfig ,config_pilote : DictConfig):

        """Initialise les variables d'instances de l'agent expert"""
     
        self.conf = config
        """@private"""
        self.correction_steer = self.conf.correction_steer
        """@private"""
        self.pilotage = Steering(config_pilote)
        """@private"""

    def reset(self) -> None:

        """Réinitialise les variables d'instances de l'agent expert"""
        
        self.pilotage.reset()

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
        center_path_distance = obs.get("center_path_distance", 0.0)[0]
        paths_width = obs.get("paths_width", [10.0]) # 10.0 par défaut
        center_path = obs.get("center_path", [0.0, 0.0, 0.0])
        limit_path = paths_width[0] / 2

        #print((limit_path - abs(center_path_distance))[0])
        
        # Vérification de la sortie de piste imminente
        if ((limit_path - abs(center_path_distance))[0]) <= self.conf.epsilon_limite :

            gx = center_path[0] # Récupération du décalage latéral du centre de la piste
            gz = center_path[2] # Récupération de la profondeur du centre de la piste

            #print(gx)
            #print(center_path_distance)
            
            if gz < self.conf.epsilon_gz:    
                # ATTENTION LOGIQUE INVERSEE POUR CENTER PATH, si > 0 l'agent se situe à droite de la piste
                if center_path_distance > 0:
                    #print("Esquive Vers la gauche")
                    steer = -self.correction_steer
                else:
                    #print("Esquive Vers la droite")
                    steer = self.correction_steer
            else:
                #print("Esquive Par Pure_Pursuit")
                
                # Logique inversée pour le décalage latéral d'où -gx
                steer = self.pilotage.manage_pure_pursuit(-gx,gz,self.conf.gain)

            # On réduit l'accélération pour reprendre de l'adhérence
            new_accel = self.conf.new_accel

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