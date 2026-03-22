import numpy as np
from .rival_attack import AttackRivals

class ActiveShield :
    def __init__(self):
        self.attack_rival = AttackRivals()

    def fire_shield(self,obs):

        #shield_time = obs["shield_time"][0]
        item = obs["powerup_type"]
        kart_devant = self.attack_rival.attack_rivals(obs)
        bubblegum = 1

        if item == bubblegum and kart_devant == True: #on possede l'item bubble gum
            return True
        if item != bubblegum and kart_devant :
            return True
        else :
            return False
