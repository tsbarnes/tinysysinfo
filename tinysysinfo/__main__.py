import logging
import os
import platform
import signal
import time
from inspect import getframeinfo, currentframe
from pathlib import Path
from socket import AddressFamily

import distro
import psutil
from PIL import Image, ImageDraw, ImageFont

from . import buttons
from . import tft
from . import color_test
from . import resources

try:
    from local_settings import FONT
except ImportError:
    FONT = None


def main_screen(app):
    image = Image.new("RGB", (128, 128))
    draw = ImageDraw.Draw(image)

    image.paste(app.logo, box=(50, 90))

    with open('/sys/firmware/devicetree/base/model', 'r') as model_file:
        text = model_file.read()

    draw.text((5, 5), text, font=app.font)
    draw.text((5, 20), distro.name(), font=app.font)
    temperature = psutil.sensors_temperatures()['cpu_thermal'][0].current
    draw.text((5, 35), "CPU Temp: " + str(round(temperature)) + "°", font=app.font)
    draw.text((5, 50), "Hostname: " + platform.node(), font=app.font)
    wifi = None
    for network_interface in psutil.net_if_addrs()['wlan0']:
        if network_interface.family == AddressFamily.AF_INET:
            wifi = network_interface.address
    if wifi:
        draw.text((5, 65), "Wifi IP:  " + wifi, font=app.font)

    app.display.set_image(image)


class TinySysInfo:
    display = tft.TFT()
    buttons = buttons.Buttons()
    logger = logging.getLogger("tinysysinfo")
    font = None
    logo = None

    draw_screen = None

    def __init__(self):
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

        self.draw_screen = main_screen

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, *args):
        self.logger.info("tinysysinfo shutting down gracefully...")
        self.display.clear()
        time.sleep(1)
        exit(0)

    def process_buttons(self):
        while not self.buttons.queue_empty():
            for event in self.buttons.get_event():
                self.logger.debug("Button pressed: " + event)
                if event == "KEY_PRESS":
                    self.draw_screen = main_screen
                    self.display.clear()
                elif event == "KEY1":
                    pass
                elif event == "KEY2":
                    pass
                elif event == "KEY3":
                    pass
                elif event == "KEY_UP":
                    self.draw_screen = color_test.draw_screen
                    self.display.clear()
                elif event == "KEY_DOWN":
                    self.draw_screen = resources.draw_screen
                elif event == "KEY_LEFT":
                    pass
                elif event == "KEY_RIGHT":
                    pass

    def run(self):
        while True:
            self.draw_screen(app=self)
            self.process_buttons()

            time.sleep(0.3)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = TinySysInfo()
    app.run()
