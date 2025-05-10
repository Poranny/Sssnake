from customtkinter import *
from importlib.resources import files

from sssnake.env.utils.env_helpers import load_config
from sssnake.env.utils.config_def import ResetOptions, RenderConfig
from sssnake.game.controls.game_controls import GameControls
from sssnake.env.core.env_engine import EnvEngine
from sssnake.game.controls.game_loop import GameLoop
from sssnake.game.ui.renderer import Renderer
from sssnake.game.game_config import GAMECONFIG
from sssnake.game.ui.views import MainView
from sssnake.game.lifecycle_manager import AppLifecycleManager

class App:
    def __init__(self, headless=False):
        self.lifecycle_manager = AppLifecycleManager()

        self.app = CTk()
        self.app.title(GAMECONFIG.title)
        self.app.geometry("1280x720")
        self.app.grid_columnconfigure(0, weight=1)

        set_appearance_mode('dark')

        default_json = files("sssnake.env.utils").joinpath("default_params.json")
        self.env_spec, self.reset_options = load_config(jsonpath=default_json)

        if not headless:
            self.main_menu = MainView(self.app, self.reset_options)
            self.main_menu.add_observer(self.on_mainview)

            self.renderer = Renderer(width=600, height=600)
            self.renderer.set_parent(self.main_menu)
            self.renderer.set_render_config(RenderConfig.from_reset(self.reset_options))

        self.env = EnvEngine(self.env_spec)

        self.controls = GameControls(self.app)

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

        elif isinstance(data, ResetOptions) :
            self.reset_options = data

        else :
            print("Mainview command unknown")

    def start_game (self) :
        self.env.reset(options=self.reset_options)
        self.renderer.set_render_config(RenderConfig.from_reset(self.reset_options))

        self.game_loop = GameLoop(
            master=self,
            app=self.app,
            env_engine=self.env,
            game_controls=self.controls,
            renderer=self.renderer
        )

        self.game_loop.start_game()
        self.main_menu.game_started()

    def stop_game(self) :
        self.main_menu.game_ended()
        self.game_loop.pause_game()

    def run(self):
        self.app.mainloop()