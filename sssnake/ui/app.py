from customtkinter import *
from sssnake.utils.config import GAMECONFIG
from sssnake.utils.theme_loader import get_theme_path
from sssnake.ui.views import MainMenuView
class App:
    def __init__(self):

        self.app = CTk()
        self.app.title(GAMECONFIG.title)
        self.app.geometry("800x600")
        self.app.grid_columnconfigure(0, weight=1)

        set_appearance_mode('dark')
        set_default_color_theme(get_theme_path('Cobalt'))

        self.main_menu = MainMenuView(self.app)


    def run(self):
        self.app.mainloop()