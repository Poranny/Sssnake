import json

from customtkinter import *

from sssnake.core.game.game_controls import GameControls
from sssnake.core.env_engine.env_engine import EnvEngine
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

        params_path="sssnake/utils/default_params.json"
        with open(params_path, "r") as f :
            self.user_params = json.load(f)

        self.env = EnvEngine()
        self.env.reset_env(self.user_params)

        self.renderer = Renderer(width=600, height=600)
        self.renderer.set_envinfo(self.user_params)

        self.main_menu = MainView(self.app, self.renderer, self.user_params)
        self.main_menu.add_observer(self.on_mainview)

        self.controls = GameControls(self.app)

        self.game_loop = GameLoop(
            app=self.app,
            env_engine=self.env,
            game_controls=self.controls,
            renderer=self.renderer
        )
        self.game_loop.set_params(self.user_params)

    def on_mainview(self, data):

        if isinstance(data, str) :
            if data == "Play" :
                self.game_loop.start_game()
                self.main_menu.game_started()
            elif data == "Finish" :
                self.game_loop.pause_game()
                self.main_menu.game_ended()
            elif data == "Quit" :
                self.lifecycle_manager.quit()
            else :
                print("Mainview command unknown")

        elif isinstance(data, dict) :
            self.user_params = data
            self.game_loop.set_params(data)

            self.env.reset_env(self.user_params)
            self.renderer.set_envinfo(self.user_params)

        else :
            print("Mainview command unknown")

    def run(self):
        self.app.mainloop()