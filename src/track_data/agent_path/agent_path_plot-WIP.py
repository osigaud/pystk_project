import gymnasium as gym
import numpy as np
import os
import csv
import pandas as pd
import plotly.graph_objects as go
from pystk2_gymnasium.envs import AgentSpec
from pystk2_gymnasium.utils import rotate  

# Set output folder
current_dir = os.path.dirname(os.path.abspath(__file__))  
output_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "records_graph", "agent_path"))

# Define output CSV files
track_name = "xr591"
track_data_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "records_csv", "track_data")), f"{track_name}_track_data.csv")
track_nodes_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "records_csv", "track_nodes")), f"{track_name}_track_nodes.csv")
agent_path_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "records_csv", "agent_path")), f"{track_name}_agent_path.csv")

# Initialize environment
agent = AgentSpec(name="Player", use_ai=True)
env = gym.make("supertuxkart/full-v0", render_mode="human", agent=agent, track=track_name)
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

# Track agent path with absolute world positions
with open(agent_path_file, "w", newline="") as file:
    writer = csv.writer(file)
    #writer.writerow(["Agent_X", "Agent_Y", "Agent_Z"])
    writer.writerow(["Agent_X", "Agent_Y", "Agent_Z", "Node_X", "Node_Y", "Node_Z", "Vector_X", "Vector_Y", "Vector_Z"])
    done = False
    while not done:
        action = env.action_space.sample()
        obs, _, terminated, truncated, _ = env.step(action)
        agent_abs_pos = np.array(env.unwrapped.world.karts[0].location)  # <----------- Fetch dynamically updated position /!\ DO NOT DECLARE KARTS[0] AND USE IT LATER, ELSE THE LOCATION WON'T BE UPDATED!!!
        '''
        Important note on here-above line:
        env.unwrapped.world.karts[0] is re-fetched every step to ensure the position is updated dynamically.
        The issue was that kart was a stale reference to the kart object and wasn’t automatically refreshing.
        '''
        agent_front = np.array(env.unwrapped.world.karts[0].front)
        movement_vector = agent_front - agent_abs_pos
        movement_vector /= np.linalg.norm(movement_vector)  # Normalize

        # Extract track nodes
        track_nodes = [np.array(segment[0]) for segment in env.unwrapped.track.path_nodes]
        #track_nodes_agent = map(obs.kartview(),track_nodes)

        # Filter only nodes that are ahead of the agent
        nodes_ahead = []
        for node in track_nodes:
            direction_to_node = node - agent_abs_pos
            node_distance = np.linalg.norm(direction_to_node)

            # Normalize direction vector
            if node_distance > 0:
                direction_to_node /= node_distance
            
            dot_product = np.dot(movement_vector, direction_to_node)
            # Ensure the node is ahead and not too far below/above
            height_diff = abs(node[1] - agent_abs_pos[1])  # Difference in Y (height)

            # Ensure the node is in front of the agent
            if dot_product > 0 and height_diff < 5.0:  # Ensuring it's ahead and within a reasonable height
                nodes_ahead.append((i, node, node_distance))

        # Sort nodes ahead by distance
        nodes_ahead.sort(key=lambda x: (x[0], x[2]))  # Sort by distance (ascending)

        # Select the second closest node
        if len(nodes_ahead) > 1:
            second_node_pos = nodes_ahead[2][1]  # The second closest node ahead
        elif len(nodes_ahead) == 1:
            second_node_pos = nodes_ahead[0][0]  # If only one valid node ahead
        else:
            second_node_pos = agent_abs_pos  # Fallback if no valid node found

        # Compute the vector from the agent to the second node
        vector = second_node_pos - agent_abs_pos        
        writer.writerow([*agent_abs_pos, *second_node_pos, *vector])
        done = terminated or truncated

try:
    env.close()
finally:
    del env

# Load CSVs for visualization
df_track = pd.read_csv(track_data_file)
df_nodes = pd.read_csv(track_nodes_file)
df_agent = pd.read_csv(agent_path_file)

# Create Plotly 3D figure
fig = go.Figure()

# Plot track boundaries
fig.add_trace(go.Scatter3d(x=df_track['Center_X'], y=df_track['Center_Y'], z=df_track['Center_Z'], mode='lines', name='Center Line', line=dict(color='blue')))
fig.add_trace(go.Scatter3d(x=df_track['Left_X'], y=df_track['Left_Y'], z=df_track['Left_Z'], mode='lines', name='Left Boundary', line=dict(color='red')))
fig.add_trace(go.Scatter3d(x=df_track['Right_X'], y=df_track['Right_Y'], z=df_track['Right_Z'], mode='lines', name='Right Boundary', line=dict(color='green')))

# Plot track nodes
fig.add_trace(go.Scatter3d(x=df_nodes['Start_X'], y=df_nodes['Start_Y'], z=df_nodes['Start_Z'], mode='markers', name='Track Nodes', marker=dict(color='purple', size=3)))

# Plot agent path with corrected world coordinates
fig.add_trace(go.Scatter3d(x=df_agent['Agent_X'], y=df_agent['Agent_Y'], z=df_agent['Agent_Z'], mode='lines', name='Agent Path', line=dict(color='orange',width=5)))

# Plot vectors from agent to second node
for i in range(len(df_agent)):
    fig.add_trace(go.Scatter3d(
        x=[df_agent.loc[i, 'Agent_X'], df_agent.loc[i, 'Node_X']],
        y=[df_agent.loc[i, 'Agent_Y'], df_agent.loc[i, 'Node_Y']],
        z=[df_agent.loc[i, 'Agent_Z'], df_agent.loc[i, 'Node_Z']],
        mode='lines',
        name=f'Vector {i}',
        
        line=dict(color='cyan', width=1),showlegend=False
    ))

# Layout settings
fig.update_layout(
    title=f'3D Track, Nodes & Agent Path - {track_name}',
    scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
    margin=dict(l=0, r=0, b=0, t=40)
)

# Save plot as PNG
output_image = os.path.join(output_folder, f"{track_name}_track_agent_path_visualization.png")
fig.write_image(output_image)
print(f"Graph saved as {output_image}")

fig.show()
fig.write_html(os.path.join(output_folder, f"{track_name}_track_agent_path_visualization.html"), auto_open=True)
