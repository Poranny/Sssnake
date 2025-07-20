import tkinter as tk
from dataclasses import replace
from tkinter import filedialog
from typing import Any, Callable, Dict, List

from customtkinter import DISABLED, NORMAL, CTkButton, CTkEntry, CTkFrame, CTkLabel, CTkToplevel

from sssnake.env.utils.config_def import ResetOptions


class MainView(CTkFrame):
    """
    CustomTkinter UI class.
    """

    def __init__(self, master: Any, reset_options: ResetOptions) -> None:
        super().__init__(master)
        self.env_config: Any = None
        self.game_frame: CTkFrame = CTkFrame(master)
        self.game_frame.grid(row=0, column=0, padx=20, pady=20)

        self.reset_options: ResetOptions = reset_options
        self.observers: List[Callable[[Any], None]] = []

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.menu_frame: CTkFrame = CTkFrame(master)
        self.menu_frame.grid(row=0, column=1, padx=20, pady=20)

        self.btn_play = CTkButton(self.menu_frame, text="Play!", command=self._toggle_play)
        self.btn_settings = CTkButton(self.menu_frame, text="Settings", command=self.open_settings)
        self.btn_exit = CTkButton(
            self.menu_frame, text="Quit", command=lambda: self.notify_observers("Quit")
        )

        self.btn_play.grid(row=0, column=0, padx=20, pady=20)
        self.btn_settings.grid(row=1, column=0, padx=20, pady=20)
        self.btn_exit.grid(row=2, column=0, padx=20, pady=20)

        self.is_playing: bool = False
        self.selected_bitmap_path: str = ""

    def get_render_frame(self) -> CTkFrame:
        return self.game_frame

    def _toggle_play(self) -> None:
        cmd = "Finish" if self.is_playing else "Play"
        self.notify_observers(cmd)

    def game_started(self) -> None:
        self.is_playing = True
        self.btn_play.configure(text="Finish")
        self.btn_settings.configure(state=DISABLED)

    def game_ended(self) -> None:
        self.is_playing = False
        self.btn_play.configure(text="Play!")
        self.btn_settings.configure(state=NORMAL)

    def open_settings(self) -> None:
        win = CTkToplevel(self)
        win.title("Settings")
        win.attributes("-topmost", True)
        win.lift()

        frm_var = CTkFrame(win)
        frm_var.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        frm_const = CTkFrame(win)

        for frm in (frm_var, frm_const):
            frm.grid_columnconfigure(1, weight=0)
            frm.grid_columnconfigure(2, weight=0)

        CTkLabel(frm_var, text="Variables").grid(row=0, column=0, columnspan=3, pady=(0, 10))

        self._settings_widgets: Dict[str, Any] = {}

        def add_row(frame: CTkFrame, idx: int, name: str, default_val: Any) -> None:
            CTkLabel(frame, text=name).grid(row=idx, column=0, sticky="e", padx=5, pady=2)

            if name == "map_bitmap_path":

                def choose_file() -> None:
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

        var_row = 1
        for name, _type, val in self.reset_options.iter():
            add_row(frm_var, var_row, name, val)
            var_row += 1

        CTkButton(win, text="Save", command=lambda: self._save(win)).grid(
            row=1, column=0, columnspan=2, pady=10
        )

    def _save(self, window: CTkToplevel) -> None:
        new_vals: Dict[str, Any] = {}

        for name, widget in self._settings_widgets.items():
            if isinstance(widget, tuple):
                values = []
                for w in widget:
                    txt = w.get().strip()
                    try:
                        val = float(txt)
                    except ValueError:
                        val = txt
                    values.append(val)
                new_vals[name] = tuple(values)
            else:
                txt = widget.get().strip()
                try:
                    new_vals[name] = float(txt)
                except ValueError:
                    new_vals[name] = txt

        if self.selected_bitmap_path:
            new_vals["map_bitmap_path"] = self.selected_bitmap_path

        self.reset_options = replace(self.reset_options, **new_vals)
        self.notify_observers(self.reset_options)
        window.destroy()

    def add_observer(self, cb: Callable[[Any], None]) -> None:
        self.observers.append(cb)

    def notify_observers(self, data: Any = None) -> None:
        for cb in self.observers:
            cb(data)
