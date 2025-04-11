from customtkinter import *
import json

class MainView(CTkFrame) :
    def __init__(self, master, game_renderer, user_params) :
        super().__init__(master)

        self.is_playing = False

        self.observers = list()

        self.user_params = user_params

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.game_frame = CTkFrame(master)
        self.game_frame.grid(row=0, column=0, padx=20, pady=20)

        self.menu_frame = CTkFrame(master)
        self.menu_frame.grid(row=0, column=1, padx=20, pady=20)

        self.btn_play = CTkButton(master=self.menu_frame, text='Play!', command=self.play)
        self.btn_settings = CTkButton(master=self.menu_frame, text='Settings', command=self.open_settings)
        self.btn_exit = CTkButton(master=self.menu_frame, text='Quit', command=self.quit)

        self.btn_play.grid(row=0, column=0, padx=20, pady=20)
        self.btn_settings.grid(row=1, column=0, padx=20, pady=20)
        self.btn_exit.grid(row=2, column=0, padx=20, pady=20)

        self.game_renderer = game_renderer
        self.game_renderer.set_parent(self.game_frame)

    def play(self):
        self.notify_observers('Play/finish')

    def quit(self):
        self.notify_observers('Quit')

    def game_started (self) :
        self.is_playing = True
        self.btn_play.configure(text="Finish")
        self.btn_settings.configure(state=DISABLED)

    def game_ended (self) :
        self.is_playing = False
        self.btn_play.configure(text="Play")
        self.btn_settings.configure(state=NORMAL)

    def open_settings(self) :
        self.settings_window = CTkToplevel(self)
        self.settings_window.title("Settings")
        self.settings_window.attributes("-topmost", True)
        self.settings_window.lift()
        self.settings_window.focus()

        self.settings_form_entries = []
        self.settings_current_row = 0

        def add_setting(label_text, default_value=None) :
            label = CTkLabel(self.settings_window, text=label_text)
            label.grid(row=self.settings_current_row, column=0, padx=10, pady=5, sticky="e")

            entry = CTkEntry(self.settings_window)
            entry.grid(row=self.settings_current_row, column=1, padx=10, pady=5)

            if default_value is not None:
                entry.insert(0, str(default_value))

            self.settings_form_entries.append((label_text, entry))
            self.settings_current_row += 1

        for param_name, default_value in self.user_params.items() :
            add_setting(param_name, default_value)

        save_button = CTkButton(master=self.settings_window, text="Save", command=self.save_settings)
        save_button.grid(row=self.settings_current_row, column=1, padx=10, pady=5)

    def save_settings(self) :
        new_user_params = {}

        for (label_text, entry_widget) in self.settings_form_entries :
            value_str = entry_widget.get()

            new_user_params[label_text] = float(value_str)

        self.user_params = new_user_params
        self.notify_observers(self.user_params)
        self.settings_window.destroy()

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data=None):
        for callback in self.observers:
            callback(data)