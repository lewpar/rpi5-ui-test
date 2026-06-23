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
Config.set('input', 'ads7846', f'hidinput,{device},invert_y=0')
Config.set('kivy', 'exit_on_escape', 1)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock
from collections import deque


class TouchDebug(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.trails = {}
        self.touch_info = []

    def on_touch_down(self, touch):
        with self.canvas:
            Color(0, 1, 0, 0.8)
            d = 20
            Ellipse(pos=(touch.x - d/2, touch.y - d/2), size=(d, d))
            Color(1, 1, 1, 1)
            d2 = 4
            Ellipse(pos=(touch.x - d2/2, touch.y - d2/2), size=(d2, d2))

        tid = touch.id
        self.trails[tid] = {'points': deque([(touch.x, touch.y)], maxlen=50), 'color': self._random_color(tid)}

        self.touch_info.append((touch.x, touch.y, 'down'))
        self._redraw_info()

    def on_touch_move(self, touch):
        tid = touch.id
        if tid not in self.trails:
            return
        self.trails[tid]['points'].append((touch.x, touch.y))

        pts = list(self.trails[tid]['points'])
        color = self.trails[tid]['color']

        self.canvas.after.clear()
        with self.canvas.after:
            for tid2, trail in self.trails.items():
                c = trail['color']
                Color(*c)
                trail_pts = []
                for p in trail['points']:
                    trail_pts.extend([p[0], p[1]])
                if len(trail_pts) >= 4:
                    Line(points=trail_pts, width=2)

        self.touch_info.append((touch.x, touch.y, 'move'))
        self._redraw_info()

    def on_touch_up(self, touch):
        tid = touch.id
        if tid in self.trails:
            del self.trails[tid]

        self.canvas.after.clear()
        with self.canvas.after:
            for tid2, trail in self.trails.items():
                c = trail['color']
                Color(*c)
                trail_pts = []
                for p in trail['points']:
                    trail_pts.extend([p[0], p[1]])
                if len(trail_pts) >= 4:
                    Line(points=trail_pts, width=2)

        self.touch_info.append((touch.x, touch.y, 'up'))
        self._redraw_info()

    def _random_color(self, seed):
        import hashlib
        h = hashlib.md5(str(seed).encode()).digest()
        r = h[0] / 255.0
        g = h[1] / 255.0
        b = h[2] / 255.0
        return (r, g, b, 0.9)

    def _redraw_info(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0.6)
            from kivy.graphics import Rectangle
            Rectangle(pos=(0, self.height - 30), size=(self.width, 30))
            Color(1, 1, 1, 1)

        if not self.touch_info:
            return
        latest = self.touch_info[-1]
        x, y, evtype = latest
        active = len(self.trails)
        text = f"Touch: ({int(x)}, {int(y)})  event: {evtype}  active touches: {active}"

        from kivy.uix.label import Label
        if hasattr(self, '_info_label'):
            self.remove_widget(self._info_label)
        self._info_label = Label(
            text=text,
            size_hint=(None, None),
            size=(self.width, 30),
            pos=(0, self.height - 30),
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1),
            font_size=16,
        )
        self.add_widget(self._info_label)

    def clear_canvas(self):
        self.canvas.clear()
        self.canvas.after.clear()
        self.trails.clear()
        self.touch_info.clear()
        if hasattr(self, '_info_label'):
            self.remove_widget(self._info_label)
            self._info_label = None


class TouchDebugApp(App):
    def build(self):
        root = TouchDebug()
        from kivy.uix.button import Button
        btn = Button(
            text='Clear',
            size_hint=(None, None),
            size=(80, 40),
            pos=(10, 10),
        )
        btn.bind(on_release=lambda _: root.clear_canvas())
        root.add_widget(btn)
        return root


if __name__ == '__main__':
    TouchDebugApp().run()
