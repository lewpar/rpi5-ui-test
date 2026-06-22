from kivy.config import Config

Config.set('graphics', 'show_cursor', '0')
Config.set('input', 'mouse', 'mouse')
Config.set('input', 'ads7846', 'hidinput,/dev/input/event9,invert_y=0,min_abs_x=150,max_abs_x=3948,min_abs_y=275,max_abs_y=3975')

from kivy.app import App
from kivy.uix.widget import Widget


class PongGame(Widget):
    pass


class PongApp(App):
    def build(self):
        return PongGame()


if __name__ == '__main__':
    PongApp().run()