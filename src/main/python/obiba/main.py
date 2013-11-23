import os
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.factory import Factory
from kivy.lang import Builder, Parser
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.videoplayer import VideoPlayer

CONTAINER_KVS = os.path.join(os.path.dirname(__file__), 'pages')
CONTAINER_MEDIA = os.path.join(os.path.dirname(__file__), 'media')
CONTAINER_CLASSES = [c[:-3] for c in os.listdir(CONTAINER_KVS) if c.endswith('.kv')]


class AppContainer(BoxLayout):
    def __init__(self, **kwargs):
        super(AppContainer, self).__init__(**kwargs)

    def hexToPercent(self, number):
        n = int(number, 16)
        return (n >> 16) / 255.0, ((n >> 8) & 255) / 255.0, (n & 255) / 255.0


class Container(AppContainer):
    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
        parser = Parser(content=file(self.kv_file).read())
        widget = Factory.get(parser.root.name)()
        Builder._apply_rule(widget, parser.root, parser.root)
        self.add_widget(widget)

    def play_sound(self, soundFile):
        sound = SoundLoader.load(os.path.join(CONTAINER_MEDIA, soundFile))
        if sound:
            sound.volume = .5
            sound.play()

    def play_video(self, videoFile):
        popup = Popup(title='Test popup', size_hint=(None, None), size=(400, 400))
        popup.add_widget(VideoPlayer(source=os.path.join(CONTAINER_MEDIA, videoFile), state='play'))
        popup.open()


    @property
    def kv_file(self):
        '''Get the name of the kv file, a lowercase version of the class
        name.
        '''
        return os.path.join(CONTAINER_KVS, self.__class__.__name__ + '.kv')


class Questionnaire(AppContainer):
    screens = ObjectProperty()
    footer = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Questionnaire, self).__init__(**kwargs)
        self._register_screens()

    def show(self):
        self.screens.current = "intro"
        return self

    def nextScreen(self):
        self.screens.current = self.screens.next()

    def _register_screens(self):
        for class_name in CONTAINER_CLASSES:
            globals()[class_name] = type(class_name, (Container,), {})


class QuestionnaireApp(App):
    def __init__(self, **kwargs):
        super(QuestionnaireApp, self).__init__(**kwargs)
        for class_name in CONTAINER_CLASSES:
            globals()[class_name] = type(class_name, (Container,), {})


    def build(self):
        return Questionnaire().show()


if __name__ == '__main__':
    QuestionnaireApp().run()


