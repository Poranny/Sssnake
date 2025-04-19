from customtkinter import *
from tkinter import filedialog
import tkinter as tk
from typing import Dict, Any

from sssnake.utils.env_config import EnvConfig


class MainView(CTkFrame):

    def __init__(self, master, renderer, env_config: EnvConfig):
        super().__init__(master)
        self.set_config(env_config)
        self.renderer = renderer
        self.observers = []

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.game_frame = CTkFrame(master)
        self.game_frame.grid(row=0, column=0, padx=20, pady=20)

        self.menu_frame = CTkFrame(master)
        self.menu_frame.grid(row=0, column=1, padx=20, pady=20)

        self.btn_play = CTkButton(self.menu_frame, text="Play!",  command=self._toggle_play)
        self.btn_settings = CTkButton(self.menu_frame, text="Settings", command=self.open_settings)
        self.btn_exit = CTkButton(self.menu_frame, text="Quit",  command=lambda: self.notify_observers("Quit"))

        self.btn_play.grid(row=0, column=0, padx=20, pady=20)
        self.btn_settings.grid(row=1, column=0, padx=20, pady=20)
        self.btn_exit.grid(row=2, column=0, padx=20, pady=20)

        self.renderer.set_parent(self.game_frame)

        self.is_playing = False
        self.selected_bitmap_path = ""

    def set_config(self, cfg: EnvConfig):
        self.env_config = cfg

    def _toggle_play(self):
        cmd = "Finish" if self.is_playing else "Play"
        self.notify_observers(cmd)

    def game_started(self):
        self.is_playing = True
        self.btn_play.configure(text="Finish")
        self.btn_settings.configure(state=DISABLED)

    def game_ended(self):
        self.is_playing = False
        self.btn_play.configure(text="Play!")
        self.btn_settings.configure(state=NORMAL)

    def open_settings(self):
        win = CTkToplevel(self)
        win.title("Settings")
        win.attributes("-topmost", True)
        win.lift()

        frm_var = CTkFrame(win)
        frm_var.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        frm_const = CTkFrame(win)
        #frm_const.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        for frm in (frm_var, frm_const):
            frm.grid_columnconfigure(1, weight=0)
            frm.grid_columnconfigure(2, weight=0)

        CTkLabel(frm_var, text="Variables").grid(row=0, column=0, columnspan=3, pady=(0, 10))
        #CTkLabel(frm_const, text="Constants").grid(row=0, column=0, columnspan=3, pady=(0, 10))

        self._settings_widgets: Dict[str, Any] = {}

        def add_row(frame, idx, name, default_val):
            CTkLabel(frame, text=name).grid(row=idx, column=0, sticky="e", padx=5, pady=2)

            if name == "map_bitmap_path":
                def choose_file():
                    fp = filedialog.askopenfilename(
                        filetypes=[("Image Files", "*.png *.bmp *.jpg")]
                    )
                    if fp:
                        btn.configure(text=f"File: {fp}")
                        self.selected_bitmap_path = fp

                btn = CTkButton(frame, text="Select file", command=choose_file)
                btn.grid(row=idx, column=1, padx=10, pady=8)
                return

            if isinstance(default_val, (tuple, list)):
                bg = frame.cget("fg_color")
                sub = tk.Frame(frame, bg=bg[1], bd=0, highlightthickness=0)
                sub.grid(row=idx, column=1, padx=15, pady=4, sticky="w")

                entries = []
                for i, val in enumerate(default_val):
                    entry = CTkEntry(sub, width=60)
                    entry.pack(side="left", padx=(0, 4) if i < len(default_val) - 1 else 0)
                    entry.insert(0, str(val))
                    entries.append(entry)

                self._settings_widgets[name] = tuple(entries)

            else:
                ent = CTkEntry(frame, width=120)
                ent.grid(row=idx, column=1, columnspan=2, padx=15, pady=4, sticky="w")
                ent.insert(0, str(default_val))
                self._settings_widgets[name] = ent

        var_row = const_row = 1
        for name, grp, _type, val in self.env_config.list_params():
            if grp == "var":
                add_row(frm_var, var_row, name, val)
                var_row += 1
            else:
                pass
                #add_row(frm_const, const_row, name, val)
                #const_row += 1

        CTkButton(win, text="Save", command=lambda: self._save(win)).grid(
            row=1, column=0, columnspan=2, pady=10
        )

    def _save(self, window: CTkToplevel):
        env_variable, env_constant = {}, {}

        for name, widget in self._settings_widgets.items():
            if isinstance(widget, tuple):
                values = []
                for w in widget:
                    text = w.get().strip()
                    try:
                        val = float(text)
                    except ValueError:
                        val = text
                    values.append(val)
                value = tuple(values)
            else:
                txt = widget.get().strip()
                try:
                    value = float(txt)
                except ValueError:
                    value = txt

            grp = self.env_config.entry(name).group
            (env_variable if grp == "var" else env_constant)[name] = value

        if not self.selected_bitmap_path:
            env_variable["map_bitmap_path"] = self.env_config.get("map_bitmap_path")
        else:
            env_variable["map_bitmap_path"] = self.selected_bitmap_path

        new_raw = {"env_variable": env_variable, "env_constant": env_constant}

        self.notify_observers(new_raw)

        window.destroy()

    def add_observer(self, cb):
        self.observers.append(cb)

    def notify_observers(self, data=None):
        for cb in self.observers:
            cb(data)
