from typing import Callable, List

class AppLifecycleManager :
    def __init__(self) :
        self._cleanup_callbacks: List[Callable] = []

    def register_cleanup(self, callback : Callable) :
        self._cleanup_callbacks.append(callback)

    def quit(self):
        self._perform_cleanup()
        self._exit_application()


    def _perform_cleanup(self):
        for callback in self._cleanup_callbacks :
            callback()
        print("Cleanup performed")

    def _exit_application(self):
        exit(0)