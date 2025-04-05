from customtkinter import *


class MainMenuView(CTkFrame) :
    def __init__(self, master, lifecycle_manager) :
        super().__init__(master)

        self.lifecycle_manager = lifecycle_manager

        self.frame = CTkFrame(master)
        self.frame.grid(row=0, column=0, padx=20, pady=20)

        self.btn_play = CTkButton(master=self.frame, text='Play!')
        self.btn_settings = CTkButton(master=self.frame, text='Settings')
        self.btn_exit = CTkButton(master=self.frame, text='Quit', command=self.lifecycle_manager.quit)

        self.btn_play.grid(row=0, column=0, padx=20, pady=20)
        self.btn_settings.grid(row=1, column=0, padx=20, pady=20)
        self.btn_exit.grid(row=2, column=0, padx=20, pady=20)