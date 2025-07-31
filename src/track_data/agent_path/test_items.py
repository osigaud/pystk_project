import gymnasium as gym
from pystk2_gymnasium.envs import AgentSpec
import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "src")))

# Initialize agent and environment
agent = AgentSpec(name="Player", use_ai=True)
env = gym.make("supertuxkart/full-v0", render_mode="human", agent=agent, track=None)

# Run the environment and print item details
obs, _ = env.reset()

print("=== ITEM TYPES AND POSITIONS TEST ===")

max_steps = 100  # Limit steps to avoid infinite output
step_count = 0

done = False
while not done and step_count < max_steps:
    action = env.action_space.sample()  # Random actions
    obs, _, terminated, truncated, _ = env.step(action)
    
    # Extract item information
    items_type = obs.get('items_type', [])
    items_position = obs.get('items_position', [])

    # Print results
    print(f"Step {step_count + 1}:")
    print(f"  Items Types: {items_type}")
    print(f"  Items Positions: {items_position}")
    print("-" * 40)

    step_count += 1
    done = terminated or truncated

env.close()
print("=== TEST COMPLETED ===")
