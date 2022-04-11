import psutil

from PIL import Image, ImageDraw

from tinysysinfo import tinysysinfo


class Screen(tinysysinfo.Screen):
    def draw(self):
        image = Image.new("RGB", (self.app.display.lcd.width, self.app.display.lcd.height))
        draw = ImageDraw.Draw(image)

        temperature = psutil.sensors_temperatures()['cpu_thermal'][0].current
        draw.text((5, 5), "CPU Temp: " + str(round(temperature)) + "°", font=self.app.font)
        draw.text((5, 15), "CPU Usage: " + str(psutil.cpu_percent()) + "%", font=self.app.font)
        draw.text((5, 25), "RAM Usage: " + str(psutil.virtual_memory().percent) + "%", font=self.app.font)
        draw.text((5, 35), "Swap Usage: " + str(psutil.swap_memory().percent) + "%", font=self.app.font)
        total_disk_space = psutil.disk_usage('/').total / 1024 / 1024 / 1024
        used_disk_space = psutil.disk_usage('/').used / 1024 / 1024 / 1024
        draw.text((5, 45), "Disk Usage: " + str(round(used_disk_space)) + "/" + str(round(total_disk_space)) + " GB", font=self.app.font)

        self.app.display.set_image(image)

    def handle_button(self, button):
        pass
