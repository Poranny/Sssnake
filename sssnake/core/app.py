import json
from customtkinter import *

from sssnake.utils.env_config import EnvSpec, ResetOptions, RenderState, RenderConfig
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

        self.env_spec, self.reset_options = self.load_config(jsonpath="sssnake/utils/default_params.json")

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

    def load_config(self, jsonpath: str):
        with open(jsonpath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        spec = EnvSpec.from_dict(raw["env_spec"])
        opts = ResetOptions.from_dict(raw["reset_options"])
        return spec, opts