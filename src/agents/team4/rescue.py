import numpy as np

class RescueManager:
    def __init__(self):
        self.agent_positions = []
        self.times_blocked = 0

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
        
        
        return self.times_blocked >= 7

    def sortir_du_mur(self, current_steer):
        
        
        recovery_steer = -1.0 if current_steer > 0 else 1.0
        
        return {
            "acceleration": 0.0,
            "steer": recovery_steer,
            "brake": True,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }