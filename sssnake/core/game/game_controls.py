class GameControls :
    def __init__(self, widget):
        self.widget = widget

        self.pressed_keys = set()

        self.widget.bind("<KeyPress>", self.on_key_press)
        self.widget.bind("<KeyRelease>", self.on_key_release)

    def on_key_press(self, event):
        if event.keysym in ("Left", "Right"):
            self.pressed_keys.add(event.keysym)

    def on_key_release(self, event):
        if event.keysym in ("Left", "Right"):
            self.pressed_keys.discard(event.keysym)

    def get_action(self):

        if "Left" in self.pressed_keys and "Right" in self.pressed_keys:
            return None
        elif "Left" in self.pressed_keys:
            return "left"
        elif "Right" in self.pressed_keys:
            return "right"
        else:
            return None
