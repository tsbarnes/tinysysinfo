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

try:
    from local_settings import FONT
except ImportError:
    FONT = None


class TinySysInfo:
    display = tft.TFT()
    buttons = buttons.Buttons()
    logger = logging.getLogger("tinysysinfo")
    font = None
    logo = None

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

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, *args):
        self.logger.info("tinysysinfo shutting down gracefully...")
        self.display.clear()
        time.sleep(1)
        exit(0)

    def main_screen(self):
        image = Image.new("RGB", (128, 128))
        draw = ImageDraw.Draw(image)

        image.paste(self.logo, box=(50, 90))

        with open('/sys/firmware/devicetree/base/model', 'r') as model_file:
            text = model_file.read()

        draw.text((5, 5), text, font=self.font)
        draw.text((5, 20), distro.name(), font=self.font)
        temperature = psutil.sensors_temperatures()['cpu_thermal'][0].current
        draw.text((5, 35), "CPU Temp: " + str(round(temperature)) + "°", font=self.font)
        draw.text((5, 50), "Hostname: " + platform.node(), font=self.font)
        wifi = None
        for network_interface in psutil.net_if_addrs()['wlan0']:
            if network_interface.family == AddressFamily.AF_INET:
                wifi = network_interface.address
        if wifi:
            draw.text((5, 65), "Wifi IP:  " + wifi, font=self.font)

        self.display.set_image(image)

    def process_buttons(self):
        while not self.buttons.queue_empty():
            for event in self.buttons.get_event():
                self.logger.debug("Button pressed: " + event)
                if event == "KEY_PRESS":
                    self.display.clear()
                if event == "KEY1":
                    image = Image.new("RGB", (self.display.lcd.width, self.display.lcd.height))
                    draw = ImageDraw.Draw(image)
                    draw.rectangle((0, 0, self.display.lcd.width, self.display.lcd.height), fill="orange")
                    self.display.set_image(image)
                if event == "KEY2":
                    pass
                if event == "KEY3":
                    pass

    def run(self):
        while True:
            self.main_screen()
            self.process_buttons()

            time.sleep(0.3)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = TinySysInfo()
    app.run()
