from pathlib import Path
import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from omegaconf import OmegaConf

from agents.kart_agent import KartAgent
from agents.team1.agent_center import AgentCenter
from agents.team1.agent_speed import AgentSpeed
from agents.team1.agent_obstacles import AgentObstacles
from agents.team1.agent_rescue import AgentRescue
from agents.team1.agent_items import AgentItems
"""
import math
from omegaconf import OmegaConf
"""

class Agent1(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Tasty Crousteam"

        path_conf = Path(__file__).resolve().parent
        path_conf = str(path_conf) + '/configFIleTastyCrousteam.yaml'   #Chemin du fichier de configuration
        self.conf = OmegaConf.load(path_conf)                           #Importation du fichier de configuration

        self.agentCenter = AgentCenter(env, self.conf, self.path_lookahead)
        self.agentSpeed = AgentSpeed(env, self.conf, self.agentCenter, self.path_lookahead)
        self.agentObstacles = AgentObstacles(env, self.conf, self.agentSpeed, self.path_lookahead)
        self.agentRescue = AgentRescue(env, self.conf, self.agentObstacles)
        self.agentItems = AgentItems(env, self.conf, self.agentRescue)

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        return self.agentItems.choose_action(obs)