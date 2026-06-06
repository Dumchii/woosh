import time
import threading
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, KeyCode

# Config variables
click_delay = 0.5
button = Button.left

# Hotkeys
start_click_key = KeyCode(char='k')
exit_key = KeyCode(char='c')

class AutoClicker(threading.Thread):
    def __init__(self, delay, button):
        super().__init__()
        self.delay = delay
        self.button = button
        self.clicking = False
        self.active = True
        self.mouse = MouseController()

    def start_clicking(self):
        if not self.clicking:
            self.clicking = True
            print("[INFO] Clicker Started.")

    def stop_clicking(self):
        if self.clicking:
            self.clicking = False
            print("[INFO] Clicker Stopped.")

    def exit(self):
        self.stop_clicking()
        self.active = False

    def run(self):
        while self.active:
            while self.clicking:
                self.mouse.click(self.button)
                time.sleep(self.delay)
            time.sleep(0.1)  # Prevents high CPU usage when idle

# Initialize thread
clicker_thread = AutoClicker(click_delay, button)
clicker_thread.start()

def on_press(key):
    # Check if the exact hotkeys were pressed
    if key == start_click_key:
        clicker_thread.start_clicking()
    elif key == exit_key:
        clicker_thread.exit()
        print("[INFO] Exiting script...")
        return False  
    else:
        # Smart Brake: Only cancel if the clicker is actively running
        if clicker_thread.clicking:
            print("[ALERT] Interrupted! Canceling automation.")
            clicker_thread.stop_clicking()

# Start the keyboard listener
with Listener(on_press=on_press) as listener:
    listener.join()