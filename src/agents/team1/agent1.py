from pathlib import Path
import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from omegaconf import OmegaConf

from agents.kart_agent import KartAgent
from agents.team1.agent_center import AgentCenter
from agents.team1.agent_speed import AgentSpeed
from agents.team1.agent_rescue import AgentRescue
from agents.team1.agent_items import AgentItems
from agents.team1.agent_drift import AgentDrift
from agents.team1.agent_virage import AgentVirage

# kart_skin = ['adiumy', 'sara_the_racer', 'amanda', 'tux', 'beastie', 'emule', 'gavroche', 'gnu', 'hexley', 'kiki', 'konqi', 'nolok', 'pidgin', 'puffy', 'sara_the_wizard', 'suzanne', 'wilber', 'xue']

class Agent1(KartAgent):
    def __init__(self, env, path_lookahead=3, dist=None, ajust=None):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Tasty Crousteam"
        self.skin = 'adiumy'

        path_conf = Path(__file__).resolve().parent
        path_conf = str(path_conf) + '/ConfigFileTeam1.yaml'   #Chemin du fichier de configuration
        self.conf = OmegaConf.load(path_conf)                           #Importation du fichier de configuration
        
        if dist is not None:
        	self.conf.dist = dist
        if ajust is not None:
        	self.conf.ajust = ajust
        
        self.agentCenter = AgentCenter(env, self.conf, self.path_lookahead)
        self.agentSpeed = AgentSpeed(env, self.conf, self.agentCenter, self.path_lookahead)
        self.agentRescue = AgentRescue(env, self.conf, self.agentSpeed)
        self.agentItems = AgentItems(env, self.conf, self.agentRescue)
        self.agentDrift = AgentDrift(env, self.conf, self.agentItems)
        self.agentVirage = AgentVirage(env, self.conf, self.agentDrift)

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        action = self.agentItems.choose_action(obs)
        action = self.agentVirage.gestion_virage(obs, action)
        return action