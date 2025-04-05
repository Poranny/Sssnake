import tkinter as tk
from customtkinter import *
from sssnake.utils.config import GAME
from sssnake.utils.theme_loader import get_theme_path
def main():

    app = CTk()
    app.title(GAME.title)
    app.geometry("800x600")
    app.grid_columnconfigure(0, weight=1)

    set_appearance_mode('dark')
    set_default_color_theme(get_theme_path('Obsidian'))
    frame = CTkFrame(app)
    frame.grid(row=0, column=0, padx=20, pady=20)

    btn_play = CTkButton(master=frame, text='Play!')
    btn_settings = CTkButton(master=frame, text='Settings')
    btn_exit = CTkButton(master=frame, text='Quit')

    btn_play.grid(row=0, column=0, padx=20, pady=20)
    btn_settings.grid(row=1, column=0, padx=20, pady=20)
    btn_exit.grid(row=2, column=0, padx=20, pady=20)

    app.mainloop()


if __name__ == '__main__':
    main()
