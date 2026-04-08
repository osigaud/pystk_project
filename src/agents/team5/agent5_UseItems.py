import numpy as np
from agents.kart_agent import KartAgent

class Agent5UseItems(KartAgent):
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.pilot = pilot_agent
        self.name = "Donkey Bombs NitroTracker"
        self.conf = conf

        #0:rien  1:chewing-gum  2:gâteau  3:quille  4:boost  5:ventouse  6:interrupteur  7:tapette à mouches  8:balle en caoutchouc  9:parachute
        self.ATTACK_ITEMS = {2, 3, 5}#3保龄球
        self.DEFENSE_ITEMS = {1}
        self.BOOST_ITEMS = {8, 4, 5}
        self.TRAP_ITEMS = {9, 6}
        self.Tap_mouche = {7}

    def choose_action(self, obs):
        action = self.pilot.choose_action(obs)
        item = obs["powerup_type"]
        #if (obs["powerup_type"] != 0):
            #print("Current item:", obs["powerup_type"])
        #print("item id:", obs["items_type"])
        #print("Current item:", obs["attachment"])

        action["fire"] = False
        if item != 0:
            if self.should_use_item(item, obs):
                action["fire"] = True
                #print("111")
        return action
    
    def should_use_item(self, item, obs):

        if item in self.BOOST_ITEMS:
            #print("1")
            return self.use_boost(obs)

        elif item in self.DEFENSE_ITEMS:
            #print("11")
            return self.use_defense(obs)

        elif item in self.ATTACK_ITEMS:
            #print("111")
            return self.use_attack(obs)

        elif item in self.TRAP_ITEMS:
            #print("1111")
            return self.use_trap(obs)
        
        elif item in self.Tap_mouche:
            return self.use_tap_mouche(obs)



        return False
    
    def use_boost(self, obs):
        action = self.pilot.choose_action(obs)
        if action["steer"] < 0.1:
            return True

        return False

    def use_defense(self, obs):

        return True
    
    def use_attack(self, obs):
        for kart in obs["karts_position"]:
            dz = kart[2] 
            if 0 < dz < 20:
                return True
        return False
    
    def use_trap(self, obs):
        return True
    
    def use_tap_mouche(self, obs):
        item_attach = obs["attachment"]
        if item_attach == 2:
            return True
        for kart in obs["karts_position"]:
            dz = kart[2]
            if 0 < dz < 3:
                return True
        return False