import logging
import os
import signal
import time
from inspect import getframeinfo, currentframe
from pathlib import Path

from PIL import ImageFont, Image

from tinysysinfo.tft import TFT
from tinysysinfo.buttons import Buttons

try:
    from local_settings import FONT
except ImportError:
    FONT = None


class Screen:
    app = None

    def __init__(self, app):
        self.app = app

    def draw(self):
        raise NotImplementedError

    def handle_button(self, button):
        raise NotImplementedError


class TinySysInfo:
    display: TFT = None
    buttons: Buttons = None
    logger: logging.Logger = None
    font: ImageFont = None
    logo: Image = None

    screens: dict = None
    active_screen: Screen = None

    def __init__(self):
        from tinysysinfo import main_screen, color_test, resources

        self.screens = {
            "main": main_screen.Screen(self),
            "color_test": color_test.Screen(self),
            "resources": resources.Screen(self),
        }
        self.active_screen = self.screens["main"]

        self.display = TFT()
        self.buttons = Buttons()
        self.logger = logging.getLogger("tinysysinfo")

        self.display.start()
        self.buttons.start()

        if FONT:
            try:
                self.font = ImageFont.truetype(font=FONT, size=8)
            except OSError as error:
                self.logger.error(error)

        filename = getframeinfo(currentframe()).filename
        parent = Path(filename).resolve().parent
        self.logo = Image.open(os.path.join(parent, 'raspberry-pi.png'))

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, *args):
        self.logger.info("tinysysinfo shutting down gracefully...")
        self.display.clear()
        time.sleep(1)
        self.buttons.stop()
        self.display.stop()
        time.sleep(1)
        self.buttons.join()
        self.display.join()
        exit(0)

    def process_buttons(self):
        while not self.buttons.queue_empty():
            for event in self.buttons.get_event():
                self.logger.debug("Button pressed: " + event)
                if event == "KEY_PRESS":
                    self.active_screen = self.screens["main"]
                    self.display.clear()
                elif event == "KEY_UP":
                    self.active_screen = self.screens["color_test"]
                    self.display.clear()
                elif event == "KEY_DOWN":
                    self.active_screen = self.screens["resources"]
                elif event == "KEY_LEFT":
                    # TODO: Network info screen
                    pass
                elif event == "KEY_RIGHT":
                    # TODO: Other info screen
                    pass
                else:
                    self.active_screen.handle_button(event)

    def run(self):
        while True:
            self.active_screen.draw()
            self.process_buttons()

            time.sleep(0.3)
