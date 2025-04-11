

class GameControls :
    def __init__(self, widget):
        self.current_action = None
        self.widget = widget

        self.widget.bind("<KeyPress>", self.on_key_press)
        self.widget.bind("<KeyRelease>", self.on_key_release)

    def on_key_press(self, event):
        if event.keysym == "Left" :
            self.current_action = "left"
        elif event.keysym == "Right" :
            self.current_action = "right"

    def on_key_release(self, event):
        self.current_action = None


    def get_action(self):
        return self.current_action