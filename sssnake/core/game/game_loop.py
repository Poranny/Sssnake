import threading

class GameLoop:
    def __init__(self, master, app, env_engine, game_controls, renderer):

        self.user_params = None
        self.app = app
        self.controls = game_controls
        self.renderer = renderer

        self.master = master

        self.env = env_engine
        self.env.add_observer(self.on_env)

        self.play_on = False
        self.loop_id = None

        self.fps = 60
        self.frame_ms = int(1000 / self.fps)

    def start_game(self):
        self.end_game_loop()
        self.env.reset_env(self.user_params)

        self.play_on = True
        self.game_loop()

    def pause_game(self):
        self.end_game_loop()
        self.env.reset_env(self.user_params)

        self.play_on = False

    def game_loop(self):
        current_action = self.controls.get_action()
        self.env.step(current_action)

        if self.play_on:
            self.loop_id = self.app.after(self.frame_ms, self.game_loop)

    def end_game_loop(self):
        if self.loop_id is not None:
            self.app.after_cancel(self.loop_id)
            self.loop_id = None

    def on_env(self, data):
        if isinstance(data, dict):
            threading.Thread(target=self.renderer.async_render, args=(data,), daemon=True).start()
        else :
            if data == "Hit" :
                self.master.stop_game()
            else :
                print("Env command unknown")

    def set_params (self, params):
        self.user_params = params