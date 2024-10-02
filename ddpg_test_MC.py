import gym
import torch
import torch.nn as nn
import os
import pygame
import numpy as np

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device: ", device)

env = gym.make(id='MountainCarContinuous-v0', render_mode='rgb_array')

state_dim = env.observation_space.shape[0]
action_dim = env.action_space.shape[0]


# Actor Network
class Actor(nn.Module):
    def __init__(self, hidden_dim=64):
        super(Actor, self).__init__()
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, action_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.tanh(self.fc3(x))  # Pendulum action space is [-2, 2]
        return x


# Function to convert Gym's image to a format Pygame can display
def process_frame(frame):
    frame = np.transpose(frame, (1, 0, 2))
    frame = pygame.surfarray.make_surface(frame)
    return pygame.transform.scale(frame, (width, height))


# TODO-------------------------------------
# Test phase
current_path = os.path.dirname(os.path.realpath(__file__))
model = current_path + '/models/'
actor_path = model + 'mc_ddpg_actor_20240930165504.pth'

actor = Actor().to(device)
actor.load_state_dict(torch.load(actor_path))

# Initialize Pygame
pygame.init()
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# TODO-------------------------------------
num_episodes = 50
for episode_i in range(num_episodes):
    state, others = env.reset()
    episode_reward = 0
    done = False
    count = 0

    for step_i in range(200):
        action = actor(torch.FloatTensor(state).unsqueeze(0).to(device)).detach().cpu().numpy()[0]
        next_state, reward, done, truncation, _ = env.step(action)
        episode_reward += reward
        state = next_state
        count += 1
        print(f"{count}:{reward}")
        print(f"{count}:{action}")

        frame = env.render()  # Get the frame for rendering in rgb_array mode
        frame = process_frame(frame)
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        clock.tick(60)  # FPS


pygame.quit()
env.close()
