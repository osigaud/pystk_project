import gymnasium as gym
import numpy as np
import os
import csv
import pandas as pd
import plotly.graph_objects as go
from pystk2_gymnasium.envs import AgentSpec

# Set up directories
csv_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..", "records_csv","track_data"))
graph_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..", "records_graph","track_nodes_visualization"))
os.makedirs(csv_base_dir, exist_ok=True)
os.makedirs(graph_base_dir, exist_ok=True)

# Define output CSV files
track_name = "xr591"
track_data_file = os.path.join(csv_base_dir, f"{track_name}_track_data.csv")
track_nodes_file = os.path.join(csv_base_dir, f"{track_name}_track_nodes.csv")

# Initialize environment
agent = AgentSpec(name="Player", use_ai=True)
env = gym.make("supertuxkart/full-v0", render_mode="human", agent=agent, track=track_name)
obs, _ = env.reset()

# Save track paths to CSV
with open(track_data_file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Center_X", "Center_Y", "Center_Z", "Left_X", "Left_Y", "Left_Z", "Right_X", "Right_Y", "Right_Z"])
    for i in range(len(obs["paths_start"])):
        center_vector = np.array(env.unwrapped.track.path_nodes[i][0])  # Use absolute track node positions
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

try:
    env.close()
finally:
    del env

# Load CSVs for visualization
df_track = pd.read_csv(track_data_file)
df_nodes = pd.read_csv(track_nodes_file)

# Create Plotly 3D figure
fig = go.Figure()

# Plot track boundaries
fig.add_trace(go.Scatter3d(x=df_track['Center_X'], y=df_track['Center_Y'], z=df_track['Center_Z'], mode='lines', name='Center Line', line=dict(color='blue')))
fig.add_trace(go.Scatter3d(x=df_track['Left_X'], y=df_track['Left_Y'], z=df_track['Left_Z'], mode='lines', name='Left Boundary', line=dict(color='red')))
fig.add_trace(go.Scatter3d(x=df_track['Right_X'], y=df_track['Right_Y'], z=df_track['Right_Z'], mode='lines', name='Right Boundary', line=dict(color='green')))

# Create shaded track surface
for i in range(len(df_track) - 1):
    fig.add_trace(go.Mesh3d(
        x=[df_track['Left_X'][i], df_track['Left_X'][i+1], df_track['Right_X'][i+1], df_track['Right_X'][i]],
        y=[df_track['Left_Y'][i], df_track['Left_Y'][i+1], df_track['Right_Y'][i+1], df_track['Right_Y'][i]],
        z=[df_track['Left_Z'][i], df_track['Left_Z'][i+1], df_track['Right_Z'][i+1], df_track['Right_Z'][i]],
        color='gray', opacity=0.5, showscale=False
    ))

# Plot track nodes
fig.add_trace(go.Scatter3d(x=df_nodes['Start_X'], y=df_nodes['Start_Y'], z=df_nodes['Start_Z'], mode='markers', name='Track Nodes', marker=dict(color='purple', size=3)))

# Layout settings
fig.update_layout(
    title=f'3D Track & Nodes Visualization - {track_name}',
    scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
    margin=dict(l=0, r=0, b=0, t=40)
)

# Save plot as PNG
output_image = os.path.join(graph_base_dir, f"{track_name}_track_nodes_visualization.png")
fig.write_image(output_image)
print(f"Graph saved as {output_image}")

fig.show()
fig.write_html(os.path.join(graph_base_dir, f"{track_name}_track_nodes_visualization.html"), auto_open=True)