import logging
import threading
import time

from PIL import Image
from ws1in44lcd import LCD


class TFT(threading.Thread):
    lcd: LCD.LCD = None
    image: Image = None
    thread_lock: threading.Lock = None
    dirty: bool = False
    logger: logging.Logger = None

    def __init__(self):
        self.logger = logging.getLogger("tinysysinfo.tft")
        self.lcd = LCD.LCD()
        self.lcd.init(LCD.SCAN_DIR_DFT)
        self.image = Image.new("RGB", (self.lcd.width, self.lcd.height))
        self.thread_lock = threading.Lock()
        super().__init__()

    def run(self) -> None:
        thread_process = threading.Thread(target=self.main_loop)
        # run thread as a daemon so it gets cleaned up on exit.
        thread_process.daemon = True
        thread_process.start()

    def main_loop(self):
        while True:
            if self.dirty and self.image:
                self.dirty = False
                self.logger.debug("Writing image to display")
                self.lcd.show_image(self.image)
            time.sleep(0.1)

    def set_image(self, image: Image):
        self.image = image
        self.dirty = True

    def clear(self):
        self.image = Image.new("RGB", (self.lcd.width, self.lcd.height))
        self.dirty = True


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    tft = TFT()
    tft.start()
    tft.clear()
    time.sleep(1)
