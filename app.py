import os
import platform
import time
import logging
from inspect import getframeinfo, currentframe
from pathlib import Path
from socket import AddressFamily

import distro
import psutil
from PIL import Image, ImageDraw, ImageFont

from ws1in44lcd import LCD, keys


class TinySysInfo:
    display = LCD.LCD()
    logger = logging.getLogger("tinysysinfo")

    def __init__(self):
        self.display.init(LCD.SCAN_DIR_DFT)
        keys.init()
        self.display.text = "I have nadmissible."

    def run(self):
        while True:
            image = Image.new("RGB", (128, 128))
            draw = ImageDraw.Draw(image)

            try:
                font = ImageFont.truetype(font="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size=12)
            except OSError as error:
                self.logger.error(error)
                font = None

            filename = getframeinfo(currentframe()).filename
            parent = Path(filename).resolve().parent
            logo = Image.open(os.path.join(parent, 'raspberry-pi.png'))
            image.paste(logo, box=(50, 90))

            with open('/sys/firmware/devicetree/base/model', 'r') as model_file:
                text = model_file.read()

            draw.text((5, 5), text, font=font)
            draw.text((5, 20), distro.name(), font=font)
            temperature = psutil.sensors_temperatures()['cpu_thermal'][0].current
            draw.text((5, 35), "CPU Temp: " + str(round(temperature)) + "°", font=font)
            draw.text((5, 50), "Hostname: " + platform.node(), font=font)
            wifi = None
            for network_interface in psutil.net_if_addrs()['wlan0']:
                if network_interface.family == AddressFamily.AF_INET:
                    wifi = network_interface.address
            if wifi:
                draw.text((5, 65), "Wifi IP:  " + wifi, font=font)

            self.display.show_image(image)

            time.sleep(1)


if __name__ == '__main__':
    app = TinySysInfo()
    app.run()
