import json
import threading

from customtkinter import *

from sssnake.core.controls.game_controls import GameControls
from sssnake.core.env_engine.env_engine import EnvEngine
from sssnake.core.rendering.game_renderer import GameRenderer
from sssnake.utils.config import GAMECONFIG
from sssnake.utils.theme_loader import get_theme_path
from sssnake.ui.views import MainView
from sssnake.core.lifecycle_manager import AppLifecycleManager

class App:
    def __init__(self):

        self.current_action = None
        self.lifecycle_manager = AppLifecycleManager()
        self.play_on = False
        self.loop_id = None

        self.app = CTk()
        self.app.title(GAMECONFIG.title)
        self.app.geometry("1280x720")
        self.app.grid_columnconfigure(0, weight=1)

        set_appearance_mode('dark')
        set_default_color_theme(get_theme_path('Cobalt'))

        self.env = EnvEngine()
        self.env.add_observer(self.on_env_state_change)

        self.game_renderer = GameRenderer(width=600, height=600)

        params_path="sssnake/utils/default_params.json"
        with open(params_path, "r") as f :
            self.user_params = json.load(f)

        self.env.reset_env(self.user_params)

        self.main_menu = MainView(self.app, self.game_renderer, self.user_params)
        self.main_menu.add_observer(self.on_mainview)

        self.game_renderer.set_envinfo(self.user_params)

        self.controls = GameControls(self.app)


    def run(self):
        self.app.mainloop()

    def on_env_state_change(self, data):
        threading.Thread(target=self.async_render, args=(data,), daemon=True).start()

    def async_render(self, data):
        final_img = self.game_renderer.compute_render(data)

        self.app.after(0, lambda: self.game_renderer.update_canvas(final_img))

    def on_mainview(self, data):

        if isinstance(data, str) :
            if data == "Play" :
                self.play()
            elif data == "Quit" :
                self.lifecycle_manager.quit()
            else :
                print("Mainview command unknown")

        elif isinstance(data, dict) :
            self.user_params = data
            self.env.reset_env(self.user_params)
            self.game_renderer.set_envinfo(self.user_params)

        else :
            print("Mainview command unknown")

    def play (self) :

        if self.loop_id is not None:
            self.app.after_cancel(self.loop_id)
            self.loop_id = None

        self.env.reset_env(self.user_params)
        self.play_on = True
        self.game_loop()

    def game_loop(self):
        self.env.step(self.controls.get_action())

        if self.play_on :
            self.loop_id = self.app.after(17, self.game_loop)
