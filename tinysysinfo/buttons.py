import threading
import logging
import time
import queue

from ws1in44lcd import keys


button_dict = dict(
    KEY_UP=keys.KEY_UP_PIN,
    KEY_DOWN=keys.KEY_DOWN_PIN,
    KEY_LEFT=keys.KEY_LEFT_PIN,
    KEY_RIGHT=keys.KEY_RIGHT_PIN,
    KEY_PRESS=keys.KEY_PRESS_PIN,
    KEY1=keys.KEY1_PIN,
    KEY2=keys.KEY2_PIN,
    KEY3=keys.KEY3_PIN,
)


class Buttons(threading.Thread):
    thread_lock: threading.Lock = None
    logger: logging.Logger = None
    events: queue.Queue = None

    def __init__(self):
        self.logger = logging.getLogger("tinysysinfo.buttons")
        self.thread_lock = threading.Lock()
        self.events = queue.Queue()
        keys.init()
        super().__init__()

    def run(self) -> None:
        thread_process = threading.Thread(target=self.main_loop)
        # run thread as a daemon so it gets cleaned up on exit.
        thread_process.daemon = True
        thread_process.start()

    def main_loop(self):
        button_state = dict()
        for key in button_dict.keys():
            button_state[key] = False
        while True:
            for key in button_dict.keys():
                if not keys.get_input(button_dict[key]):
                    if not button_state[key]:
                        self.events.put(key)
                    button_state[key] = True
                else:
                    button_state[key] = False

    def get_event(self):
        if not self.events.empty():
            yield self.events.get()
        else:
            yield None

    def queue_empty(self):
        return self.events.empty()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    buttons = Buttons()
    buttons.start()
    buttons.logger.info("Press buttons to test")
    while True:
        time.sleep(0.1)
        while not buttons.queue_empty():
            for event in buttons.get_event():
                buttons.logger.info("Button pressed: " + event)
