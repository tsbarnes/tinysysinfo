import logging

from tinysysinfo.tinysysinfo import TinySysInfo


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = TinySysInfo()
    app.run()
