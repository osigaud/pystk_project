class RescueManager:
    def __init__(self):
        self.agent_positions = []
        self.times_blocked = 0
        self.recovery_steer = None
        self.recovery_cd = 0
        self.recovery_timer = 12   # nombre de frames à garder le même sens
        self.switch_side = False

    def is_stuck(self, distance, speed):
        
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
        # Si on est déjà en recovery on continue dans le même sens
        if self.recovery_cd > 0:
            self.recovery_cd -= 1

        else:
            # Choix du sens uniquement quand le cooldown est fini
            base_steer = -1.0 if current_steer > 0 else 1.0
            
            if self.recovery_steer is None:
                # premier blocage → comportement normal
                self.recovery_steer = base_steer
            else:
                # blocage persistant → on tente l'autre côté
                self.recovery_steer = -self.recovery_steer
            
            # on relance le cooldown
            self.recovery_cd = self.recovery_timer
        
        return {
            "acceleration": 0.0,
            "steer": self.recovery_steer,
            "brake": True,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }
