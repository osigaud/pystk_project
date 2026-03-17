class AgentRescue:
    """
    Module Agent Expert Rescue : Gère la logique de détection et de réaction face au blocage
    """
    
    def __init__(self,config):
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.c = config
        """@private"""
        self.agent_positions = []
        """@private"""
        self.times_blocked = 0
        """@private"""
        self.recovery_steer = None
        """@private"""
        self.recovery_cd = 0
        """@private"""
        self.recovery_timer = self.c.recovery_timer #nombre de frames à garder le même sens
        """@private"""   
        self.switch_side = False
        """@private"""

    def reset(self) -> None:

        """Réinitialise les variables d'instances de l'agent expert"""
        
        self.agent_positions = []
        self.times_blocked = 0
        self.recovery_steer = None
        self.recovery_cd = 0
        self.recovery_timer = self.c.recovery_timer #nombre de frames à garder le même sens
        self.switch_side = False
        
    def is_stuck(self, distance : float, speed : float) -> bool:

        """
        Gère la détection d'un blocage de l'agent

        Args:
            
            distance(float) : Distance parcourue depuis le debut de la course.
            speed(float) : Vitesse de l'agent.
        
        Returns:
            
            bool : Variable permettant d'affirmer ou non que l'agent est bloqué.
        """
        
        self.agent_positions.append(distance)
        
        if len(self.agent_positions) >= self.c.seuil_agent_position and distance > self.c.seuil_distance:
            
            delta = self.agent_positions[-1] - self.agent_positions[-7]
            if abs(delta) < self.c.seuil_delta and speed < self.c.seuil_speed:
                self.times_blocked += 1
            else:
                self.times_blocked = 0

            if self.times_blocked > self.c.seuil_blocked:
                self.times_blocked = 0
                self.recovery_side = -1
        
        return self.times_blocked >= self.c.seuil_blocked_trigger

    def choose_action(self, current_steer : float, speed : float, distance : float) -> tuple[bool,dict]:
        """
        Gère la réaction à un blocage

        Args:
            
            current_steer(float) : Angle actuel du braquage des roues.
            speed(float) : Vitesse actuelle de l'agent.
            distance(float) : Distance parcourue depuis le debut de la course.
        
        Returns:
            
            bool : Permet de confirmer la détection d'un blocage de l'agent.
            dict : Dictionnaire d'actions à effectué pour sortir d'un blocage.
        """
    
        stuck = self.is_stuck(distance,speed)

        if stuck or self.recovery_cd > 0:
            
            if self.recovery_cd > 0:
                self.recovery_cd -= 1 #Si on est déjà en recovery on continue dans le même sens

            else:
                base_steer = -1.0 if current_steer > 0 else 1.0  #Choix du sens uniquement quand le cooldown est fini
                
                if self.recovery_steer is None:
                    self.recovery_steer = base_steer #premier blocage donc comportement normal
                else:
                    self.recovery_steer = -self.recovery_steer #blocage persistant donc on tente l'autre côté
                
                
                self.recovery_cd = self.recovery_timer #on relance le cooldown
            
            action = {
            "acceleration": 0.0,
            "steer": self.recovery_steer,
            "brake": True,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
            }

            return True, action
        
        return False, {}
