import threading

class GameLoop:
    def __init__(self, master, app, env_engine, game_controls, renderer):

        self.env_config = None
        self.app = app
        self.controls = game_controls
        self.renderer = renderer

        self.master = master

        self.env = env_engine

        self.play_on = False
        self.loop_id = None

        self.fps = 90
        self.frame_ms = int(1000 / self.fps)

    def start_game(self):
        self.end_game_loop()
        self.env.reset(self.env_config)

        self.play_on = True
        self.game_loop()

    def pause_game(self):
        self.end_game_loop()

        self.play_on = False

    def game_loop(self):
        current_action = self.controls.get_action()
        state, reward, terminated, truncated, info = self.env.step(current_action)

        if not (terminated or truncated) :
            threading.Thread(target=self.renderer.async_render, args=(state,), daemon=True).start()
            self.loop_id = self.app.after(self.frame_ms, self.game_loop)
        else :
            self.master.stop_game()

    def end_game_loop(self):
        if self.loop_id is not None:
            self.app.after_cancel(self.loop_id)
            self.loop_id = None

    def set_config (self, env_config):
        self.env_config = env_config
        self.env.reset(env_config)