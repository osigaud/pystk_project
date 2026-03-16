import numpy as np 

class AttackRivals : 

    def attack_rivals(self, obs):
        """ 
        permet d'utiliser les item seulement lorsqu'il y a des adversaires devant notre kart
        """
        karts_pos = obs['karts_position']  # les pos des autres karts
        for pos in karts_pos:
            dist = np.linalg.norm(pos)
            if pos[2] > 0: # si l'adversaire est devant nous
                angle = np.degrees(np.arctan2(pos[0], pos[2]))
                if dist < 40 and abs(angle) < 15.0: # si l'adversaire est pres de nous, alors utiliser l'item
                    return True
        return False