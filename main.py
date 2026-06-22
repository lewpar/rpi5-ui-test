from kivy.config import Config

Config.set('graphics', 'show_cursor', '0')
Config.set('input', 'mouse', 'mouse')
Config.set('input', 'ads7846', 'hidinput,/dev/input/event9,invert_y=0,min_abs_x=0,max_abs_x=4096,min_abs_y=0,max_abs_y=4096')

from kivy.app import App
from kivy.uix.widget import Widget


class PongGame(Widget):
    pass


class PongApp(App):
    def build(self):
        return PongGame()


if __name__ == '__main__':
    PongApp().run()