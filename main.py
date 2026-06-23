import sys
import os
import glob

def find_ads7846():
    for path in glob.glob('/sys/class/input/event*/device/name'):
        with open(path) as f:
            if f.read().strip() == 'ADS7846 Touchscreen':
                event = os.path.basename(os.path.dirname(os.path.dirname(path)))
                return f'/dev/input/{event}'
    return None

device = find_ads7846()
if device is None:
    print("Error: ADS7846 Touchscreen not found in /sys/class/input.", file=sys.stderr)
    sys.exit(1)

print(f"==> Found ADS7846 Touchscreen at {device}")

from kivy.config import Config

Config.set('graphics', 'show_cursor', '0')
Config.set('input', 'mouse', 'mouse')
Config.set('input', 'ads7846', f'hidinput,{device},invert_y=0')
Config.set('kivy', 'exit_on_escape', 1)

from kivy.app import App
from kivy.uix.widget import Widget


class PongGame(Widget):
    pass


class PongApp(App):
    def build(self):
        return PongGame()


if __name__ == '__main__':
    PongApp().run()