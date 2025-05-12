from __future__ import annotations

from importlib.resources import files
from typing import Any

from customtkinter import CTk, set_appearance_mode

from sssnake.env.core.env_engine import EnvEngine
from sssnake.env.utils.config_def import RenderConfig, ResetOptions
from sssnake.env.utils.env_helpers import load_config
from sssnake.game.controls.game_controls import GameControls
from sssnake.game.controls.game_loop import GameLoop
from sssnake.game.game_config import GAMECONFIG
from sssnake.game.ui.renderer import Renderer
from sssnake.game.ui.views import MainView


class App:
    def __init__(self, headless: bool = False) -> None:
        self.app: CTk = CTk()
        self.app.title(GAMECONFIG.title)
        self.app.geometry("1280x720")
        self.app.grid_columnconfigure(0, weight=1)

        set_appearance_mode("dark")

        default_json = files("sssnake.env.utils").joinpath("default_params.json")

        self.env_spec, self.reset_options = load_config(jsonpath=str(default_json))

        if not headless:
            self.main_menu: MainView = MainView(self.app, self.reset_options)

            self.main_menu.add_observer(self.on_mainview)  # type: ignore[call-arg]

            self.renderer: Renderer = Renderer(width=600, height=600)
            self.renderer.set_parent(self.main_menu)  # type: ignore[call-arg]
            self.renderer.set_render_config(RenderConfig.from_reset(self.reset_options))

        self.env: EnvEngine = EnvEngine(self.env_spec)
        self.controls: GameControls = GameControls(self.app)  # type: ignore[call-arg]

    def on_mainview(self, data: Any) -> None:
        if isinstance(data, str):
            if data == "Play":
                self.start_game()
            elif data == "Finish":
                self.stop_game()
            else:
                print("Mainview command unknown")

        elif isinstance(data, ResetOptions):
            self.reset_options = data
        else:
            print("Mainview command unknown")

    def start_game(self) -> None:
        self.env.reset(options=self.reset_options)
        self.renderer.set_render_config(RenderConfig.from_reset(self.reset_options))

        self.game_loop: GameLoop = GameLoop(  # type: ignore[call-arg]
            master=self,
            app=self.app,
            env_engine=self.env,
            game_controls=self.controls,
            renderer=self.renderer,
        )
        self.game_loop.start_game()  # type: ignore[call-arg]
        self.main_menu.game_started()  # type: ignore[call-arg]

    def stop_game(self) -> None:
        self.main_menu.game_ended()  # type: ignore[call-arg]
        self.game_loop.pause_game()  # type: ignore[call-arg]

    def run(self) -> None:
        self.app.mainloop()
