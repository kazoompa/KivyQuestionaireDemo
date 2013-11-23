from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class Test(AnchorLayout):
#class Test(BoxLayout):
    lbl = ObjectProperty(Label)
    screens = ObjectProperty()
    footer = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)

    def show(self, h):
        print h

    #def on_touch_down(self, touch):
    #    print self.lbl.height
    #    print self.lbl.texture_size[1]


class TestApp(App):
    def build(self):
        return Test()

if __name__ == '__main__':
    TestApp().run()
