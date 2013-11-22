import os
from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder, Parser
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout


CONTAINER_KVS = os.path.join(os.path.dirname(__file__), 'pages')
CONTAINER_CLASSES = [c[:-3] for c in os.listdir(CONTAINER_KVS) if c.endswith('.kv')]



class Container(BoxLayout):
    pass

    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
        parser = Parser(content=file(self.kv_file).read())
        widget = Factory.get(parser.root.name)()
        Builder._apply_rule(widget, parser.root, parser.root)
        self.add_widget(widget)

    @property
    def kv_file(self):
        '''Get the name of the kv file, a lowercase version of the class
        name.
        '''
        return os.path.join(CONTAINER_KVS, self.__class__.__name__ + '.kv')


for class_name in CONTAINER_CLASSES:
    globals()[class_name] = type(class_name, (Container,), {})


class Questionnaire(BoxLayout):
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
    def build(self):
        return Questionnaire().show()


if __name__ == '__main__':
    QuestionnaireApp().run()
