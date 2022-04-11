from PIL import Image, ImageDraw

from tinysysinfo import tinysysinfo


class Screen(tinysysinfo.Screen):
    def draw(self):
        image = Image.new("RGB", (self.app.display.lcd.width, self.app.display.lcd.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.app.display.lcd.width, self.app.display.lcd.height), fill="orange")

        self.app.display.set_image(image)

    def handle_button(self, button):
        pass
