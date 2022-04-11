import platform
from socket import AddressFamily

import distro
import psutil
from PIL import Image, ImageDraw

from tinysysinfo import tinysysinfo


class Screen(tinysysinfo.Screen):
    def draw(self):
        image = Image.new("RGB", (128, 128))
        draw = ImageDraw.Draw(image)

        image.paste(self.app.logo, box=(50, 90))

        with open('/sys/firmware/devicetree/base/model', 'r') as model_file:
            text = model_file.read()

        draw.text((5, 5), text, font=self.app.font)
        draw.text((5, 20), distro.name(), font=self.app.font)
        temperature = psutil.sensors_temperatures()['cpu_thermal'][0].current
        draw.text((5, 35), "CPU Temp: " + str(round(temperature)) + "°", font=self.app.font)
        draw.text((5, 50), "Hostname: " + platform.node(), font=self.app.font)
        wifi = None
        for network_interface in psutil.net_if_addrs()['wlan0']:
            if network_interface.family == AddressFamily.AF_INET:
                wifi = network_interface.address
        if wifi:
            draw.text((5, 65), "Wifi IP:  " + wifi, font=self.app.font)

        self.app.display.set_image(image)

    def handle_button(self, button):
        pass
