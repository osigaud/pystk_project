class RescueManager:
    """
    Module RescueManager : Gère la logique de détection de blocage et de réaction au blocage
    """
    
    def __init__(self):
        self.agent_positions = []
        self.times_blocked = 0
        self.recovery_steer = None
        self.recovery_cd = 0
        self.recovery_timer = 10   #nombre de frames à garder le même sens
        self.switch_side = False

    def is_stuck(self, distance, speed):

        """
        Gère la détection d'un blocage de l'agent

        Args:
            distance(float) : Distance parcourue depuis le debut de la course.
            speed(float) : Vitesse de l'agent.
        
        Returns:
            bool : Variable permettant d'affirmer ou non que l'agent est bloqué.
        """
        
        self.agent_positions.append(distance)
        
        if len(self.agent_positions) >= 20 and distance > 10.0:
            
            delta = self.agent_positions[-1] - self.agent_positions[-7]
            if abs(delta) < 3 and speed < 0.30:
                self.times_blocked += 1
            else:
                self.times_blocked = 0

            if self.times_blocked > 14:
                self.times_blocked = 0
                self.recovery_side = -1
        
        return self.times_blocked >= 7

    def sortir_du_mur(self, current_steer):
        """
        Gère la réaction à un blocage

        Args:
            current_steer(float)
        
        Returns:
            dict : Dictionnaire d'actions à effectué pour sortir d'un blocage
        """
    
        if self.recovery_cd > 0:
            self.recovery_cd -= 1 #Si on est déjà en recovery on continue dans le même sens

        else:
            base_steer = -1.0 if current_steer > 0 else 1.0  #Choix du sens uniquement quand le cooldown est fini
            
            if self.recovery_steer is None:
                self.recovery_steer = base_steer #premier blocage donc comportement normal
            else:
                self.recovery_steer = -self.recovery_steer #blocage persistant donc on tente l'autre côté
            
            
            self.recovery_cd = self.recovery_timer #on relance le cooldown
        
        return {
            "acceleration": 0.0,
            "steer": self.recovery_steer,
            "brake": True,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }
