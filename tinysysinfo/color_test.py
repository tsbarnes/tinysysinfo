from PIL import Image, ImageDraw


def draw_screen(app):
    image = Image.new("RGB", (app.display.lcd.width, app.display.lcd.height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, app.display.lcd.width, app.display.lcd.height), fill="orange")

    app.display.set_image(image)
