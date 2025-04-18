class GameControls:
    left_keys = {"Left", "a"}
    right_keys = {"Right", "d"}
    all_keys = left_keys | right_keys

    def __init__(self, widget):
        self.widget = widget
        self.pressed_keys = set()

        widget.bind("<KeyPress>", self.on_key_press)
        widget.bind("<KeyRelease>", self.on_key_release)

    def on_key_press(self, event):
        if event.keysym in self.all_keys:
            self.pressed_keys.add(event.keysym)

    def on_key_release(self, event):
        self.pressed_keys.discard(event.keysym)

    def get_action(self):
        pressed = self.pressed_keys
        if pressed & self.left_keys and pressed & self.right_keys:
            return "none"
        if pressed & self.left_keys:
            return "left"
        if pressed & self.right_keys:
            return "right"
        return None
