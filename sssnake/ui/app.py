import json

from customtkinter import *

from sssnake.core.env_engine.env_engine import EnvEngine
from sssnake.core.rendering.game_renderer import GameRenderer
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

        self.env = EnvEngine()
        self.env.add_observer(self.on_env_done)

        self.game_renderer = GameRenderer(width=600, height=600)

        params_path="sssnake/utils/default_params.json"
        with open(params_path, "r") as f:
            self.user_params = json.load(f)

        self.main_menu = MainView(self.app, self.game_renderer, self.lifecycle_manager, self.user_params)
        self.main_menu.add_observer(self.on_mainview_data)

    def run(self):
        self.app.mainloop()

    def on_env_done(self, data):
        print(data)

    def on_mainview_data(self, data):
        print(data)