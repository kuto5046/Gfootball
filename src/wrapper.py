import gym


class DifficultyWrapper(gym.Wrapper):
  def __init__(self, env, initial_difficulty):
    # Call the parent constructor, so we can access self.env later
    super(DifficultyWrapper, self).__init__(env)
    print(f"Initialized DifficultyWrapper {self.unwrapped._env._config._scenario_cfg.right_team_difficulty}", file=sys.stderr)
    self.difficulty = initial_difficulty

    # FootballEnvCore
    self.footballEnvCore = self.unwrapped._env
    assert(self.footballEnvCore.__class__.__name__ == 'FootballEnvCore')

    # GameEnv
    self.gameEnv = self.footballEnvCore._env
    assert(self.gameEnv.__class__.__name__ == 'GameEnv')

    # Get scenario
    level = self.footballEnvCore._config['level']
    self.scenario = importlib.import_module(f'gfootball.scenarios.{level}')
    print(f'level={level} scenario={self.scenario}', file=sys.stderr)
    self.build_scenario = self.scenario.build_scenario


#   def step(self, action):
#     observation, reward, done, info = self.env.step(action)
#     return observation, reward, done, info

  def reset(self):
    self.raw_reward = 0

    def build_scenario(builder):
      self.build_scenario(builder)
      builder.config().right_team_difficulty = self.difficulty

    self.scenario.build_scenario = build_scenario
    difficulty_prev = self.gameEnv.config.right_team_difficulty
    ret = self.env.reset()
    difficulty_current = self.gameEnv.config.right_team_difficulty
    print(f"[Reset] difficulty from {difficulty_prev} to {difficulty_current}", file=sys.stderr)
    return ret