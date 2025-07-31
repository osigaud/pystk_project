import sys
import gymnasium as gym
import numpy as np
import os
import csv
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "src")))
from pystk2_gymnasium.envs import AgentSpec
from utils.TrackUtils import TrackVisualizer  

from customAgents.MedianAgent import MedianAgent
from customAgents.EulerAgent import EulerAgent
from customAgents.ItemsAgent import ItemsAgent
from pystk2_gymnasium.envs import STKRaceMultiEnv, AgentSpec

# Set output folder
current_dir = os.path.dirname(os.path.abspath(__file__))  
output_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "records_graph", "agent_path"))

# Define output CSV files
track_name = "minigolf"
track_data_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "records_csv", "track_data")), f"{track_name}_track_data.csv")
track_nodes_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "records_csv", "track_nodes")), f"{track_name}_track_nodes.csv")
agent_path_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "records_csv", "agent_path")), f"{track_name}_agent_path.csv")

# Initialize environment
#agent = AgentSpec(name="Player", use_ai=True)
theAgent = AgentSpec(name="Euler", rank_start=0, use_ai=False)
env = gym.make("supertuxkart/full-v0", render_mode="human", agent=theAgent, track=track_name)
agent = EulerAgent(MedianAgent(env, path_lookahead=2))
obs, _ = env.reset()

# Save track paths to CSV
with open(track_data_file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Center_X", "Center_Y", "Center_Z", "Left_X", "Left_Y", "Left_Z", "Right_X", "Right_Y", "Right_Z"])
    for i in range(len(obs["paths_start"])):
        center_vector = np.array(env.unwrapped.track.path_nodes[i][0])
        track_width = obs["paths_width"][i][0]
        direction_vector = np.array(env.unwrapped.track.path_nodes[i][1]) - np.array(env.unwrapped.track.path_nodes[i][0])
        direction_vector = direction_vector / np.linalg.norm(direction_vector)
        left_offset = np.cross(direction_vector, [0, 1, 0]) * (track_width / 2)
        right_offset = -left_offset
        left_vector = center_vector + left_offset
        right_vector = center_vector + right_offset
        writer.writerow([*center_vector, *left_vector, *right_vector])

# Save track nodes to CSV
track = env.unwrapped.track
with open(track_nodes_file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Start_X", "Start_Y", "Start_Z", "End_X", "End_Y", "End_Z"])
    for segment in track.path_nodes:
        start, end = segment
        writer.writerow([*start, *end])

# Track agent path
with open(agent_path_file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Agent_X", "Agent_Y", "Agent_Z"])
    done = False
    agent_positions = []

    while not done:
        #action = env.action_space.sample()
        action = agent.calculate_action(obs)  # Use the EulerAgent to calculate the action
        obs, _, terminated, truncated, _ = env.step(action)
        agent_abs_pos = np.array(env.unwrapped.world.karts[0].location)

        agent_positions.append(agent_abs_pos)
        writer.writerow(agent_abs_pos)

        done = terminated or truncated

env.close()

# Load CSVs
df_track = pd.read_csv(track_data_file)
df_nodes = pd.read_csv(track_nodes_file)
df_agent = pd.read_csv(agent_path_file)

# Convert track data
track_data = {
    "Center_X": df_track["Center_X"],
    "Center_Y": df_track["Center_Y"],
    "Center_Z": df_track["Center_Z"],
    "Left_X": df_track["Left_X"],
    "Left_Y": df_track["Left_Y"],
    "Left_Z": df_track["Left_Z"],
    "Right_X": df_track["Right_X"],
    "Right_Y": df_track["Right_Y"],
    "Right_Z": df_track["Right_Z"]
}

# Convert nodes
nodes = list(zip(df_nodes["Start_X"], df_nodes["Start_Y"], df_nodes["Start_Z"]))

# Convert agent path
agent_positions = list(zip(df_agent["Agent_X"], df_agent["Agent_Y"], df_agent["Agent_Z"]))

# Use TrackVisualizer to plot everything
visualizer = TrackVisualizer(track_data=track_data, agent_path=agent_positions, nodes=nodes)
visualizer.plot_track()
