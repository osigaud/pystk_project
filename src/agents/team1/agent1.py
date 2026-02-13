from agents.team1.agentwrappers import *

class Agent1(AgentRescue):
    def __init__(self, env, path_lookahead=3): 
        super().__init__(env,path_lookahead)