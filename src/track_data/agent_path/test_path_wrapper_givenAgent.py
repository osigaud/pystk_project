import gymnasium as gym
from pystk2_gymnasium.envs import AgentSpec
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "src")))
from utils.TrackPathWrapper import plot_agent_path_with_track


agent = AgentSpec(name="Player", use_ai=True)
env = gym.make("supertuxkart/full-v0", render_mode="human", agent=agent, track=None)

plot_agent_path_with_track(agent, env, "minigolf")
