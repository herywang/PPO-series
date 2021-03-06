from __future__ import division
import numpy as np
from cv2 import resize
from env.GameManager import GameManager
from env.Config import Config


def process_frame(frame):
    frame = resize(frame, (Config.IMAGE_HEIGHT, Config.IMAGE_WIDTH))
    frame = np.expand_dims(frame, axis=0)
    frame = frame.astype(np.float32)
    frame *= 1.0 / 255.0
    return frame


class Environment:
    def __init__(self, display=Config.SHOW_MODE):
        self.game = GameManager(display=display)
        self.previous_state = None
        self.current_state = None
        self.available = None
        self.total_reward = 0
        self.envs_mean = None
        self.envs_std = None
        self.num_steps = 0

        self.state_mean = 0
        self.state_std = 0
        self.alpha = 0.9999
        self.num_steps = 0

    @staticmethod
    def get_env_name():
        return "CHECK_ENVIRONMENT"

    def get_num_actions(self):
        return self.game.get_num_actions()

    def get_num_states(self):
        return self.game.get_num_state()

    def _observation(self, observation):
        self.num_steps += 1
        self.state_mean = self.state_mean * self.alpha + observation.mean() * (1 - self.alpha)
        self.state_std = self.state_std * self.alpha + observation.std() * (1 - self.alpha)

        unbiased_mean = self.state_mean / (1 - pow(self.alpha, self.num_steps))
        unbiased_std = self.state_std / (1 - pow(self.alpha, self.num_steps))

        return (observation - unbiased_mean) / (unbiased_std + 1e-8)

    def reset(self):
        self.total_reward = 0
        observation, available = self.game.reset()
        self.previous_state = self.current_state = None
        self.current_state = process_frame(observation)
        return self.current_state, available

    def step(self, action):
        observation, reward, done, available, envs_mean, envs_std = self.game.step(action)
        self.available = available
        self.total_reward += reward
        self.envs_mean = envs_mean
        self.envs_std = envs_std

        self.previous_state = self.current_state
        self.current_state = process_frame(observation)
        # self.current_state = self._observation(process_frame(observation))

        return self.current_state, reward, done, available, envs_mean, envs_std
