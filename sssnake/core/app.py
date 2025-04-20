import json

from customtkinter import *

from sssnake.utils.env_config import EnvConfig
from sssnake.core.game.game_controls import GameControls
from sssnake.core.env.env_engine import EnvEngine
from sssnake.core.game.game_loop import GameLoop
from sssnake.core.rendering.renderer import Renderer
from sssnake.utils.config import GAMECONFIG
from sssnake.utils.theme_loader import get_theme_path
from sssnake.ui.views import MainView
from sssnake.core.lifecycle_manager import AppLifecycleManager

class App:
    def __init__(self):

        self.lifecycle_manager = AppLifecycleManager()

        self.app = CTk()
        self.app.title(GAMECONFIG.title)
        self.app.geometry("1280x720")
        self.app.grid_columnconfigure(0, weight=1)

        set_appearance_mode('dark')
        set_default_color_theme(get_theme_path('Cobalt'))

        user_params = self.load_json_params()
        self.env_config = EnvConfig(user_params)


        self.main_menu = MainView(self.app, self.env_config)
        self.main_menu.add_observer(self.on_mainview)

        self.renderer = Renderer(width=600, height=600)
        self.renderer.set_parent(self.main_menu)
        self.renderer.set_render_config(self.env_config)

        self.env = EnvEngine(self.env_config)

        self.controls = GameControls(self.app)

        self.game_loop = GameLoop(
            master=self,
            app=self.app,
            env_engine=self.env,
            game_controls=self.controls,
            renderer=self.renderer
        )

        self.game_loop.set_config(self.env_config)

    def on_mainview(self, data):
        if isinstance(data, str) :
            if data == "Play" :
                self.start_game()
            elif data == "Finish" :
                self.stop_game()
            elif data == "Quit" :
                self.lifecycle_manager.quit()
            else :
                print("Mainview command unknown")

        elif isinstance(data, dict) :
            self.env_config.update(data)
            self.game_loop.set_config(self.env_config)
            self.main_menu.set_config(self.env_config)

            self.renderer.set_render_config(self.env_config)

        else :
            print("Mainview command unknown")

    def start_game (self) :
        self.game_loop.start_game()
        self.main_menu.game_started()

    def stop_game(self) :
        self.main_menu.game_ended()
        self.game_loop.pause_game()

    def run(self):
        self.app.mainloop()

    def load_json_params(self):
        params_path = "sssnake/utils/default_params.json"
        with open(params_path, "r") as f:
            user_params = dict(json.load(f))

        return user_params