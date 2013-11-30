import os
import re

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.lang import Builder, Parser
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.videoplayer import VideoPlayer


CONTAINER_KVS = os.path.join(os.path.dirname(__file__), 'pages')
CONTAINER_MEDIA = os.path.join(os.path.dirname(__file__), 'media')
CONTAINER_CLASSES = [c[:-3] for c in os.listdir(CONTAINER_KVS) if c.endswith('.kv')]


class AppContainer(BoxLayout):
    def __init__(self, **kwargs):
        super(AppContainer, self).__init__(**kwargs)

    def hex_to_percent(self, number):
        n = int(number, 16)
        return (n >> 16) / 255.0, ((n >> 8) & 255) / 255.0, (n & 255) / 255.0


class WizardButton(Button):
    on_touch_down_handler = None

    def __init__(self, *args, **kwargs):
        super(WizardButton, self).__init__(*args, **kwargs)
        self.on_touch_down_handler = self.on_touch_down

    def hide(self):
        self.opacity = 0

    def show(self):
        self.opacity = 1

    def on_touch_down(self, touch):
        if self.opacity == 1.0:
            return super(WizardButton, self).on_touch_down(touch)
        else:
            return False


class Container(AppContainer):
    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
        parser = Parser(content=file(self.kv_file).read())
        widget = Factory.get(parser.root.name)()
        Builder._apply_rule(widget, parser.root, parser.root)
        self.add_widget(widget)

    def play_sound(self, sound_file):
        sound = SoundLoader.load(os.path.join(CONTAINER_MEDIA, sound_file))
        if sound:
            sound.volume = .5
            sound.play()

    def play_video(self, video_file):
        popup = Popup(title='Test popup', size_hint=(None, None), size=(400, 400))
        popup.add_widget(VideoPlayer(source=os.path.join(CONTAINER_MEDIA, video_file), state='play'))
        popup.open()


    @property
    def kv_file(self):
        '''Get the name of the kv file, a lowercase version of the class
        name.
        '''
        return os.path.join(CONTAINER_KVS, self.__class__.__name__ + '.kv')


class Question(Container):
    dispatcher = None
    answered = False

    def __init__(self, **kwargs):
        super(Question, self).__init__(**kwargs)

    def set_active(self, question, answer):
        if self.answered:
            return
        self.dispatcher.dispatch_answer(question, answer)
        self.answered = True


class AnswerDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_answered')
        super(AnswerDispatcher, self).__init__(**kwargs)

    def dispatch_answer(self, question, answer):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        self.dispatch('on_answered', question.text, answer)

    def on_answered(self, question, answer):
        pass


class CloseAppDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_close')
        super(CloseAppDispatcher, self).__init__(**kwargs)

    def dispatch_close(self):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        self.dispatch('on_close')

    def on_close(self):
        pass

class Result(Container):
    qa = {}

    def __init__(self, **kwargs):
        super(Result, self).__init__(**kwargs)
        self.dispatcher.bind(on_answered=self.answer_handler)

    def answer_handler(self, dispatcher, question, answer):
        self.qa[question] = answer

    def update_result(self, *args):
        paragraph = "\n\n"
        for question in sorted(self.qa.keys()):
            paragraph += question + "\n" + self.qa[question] + "\n\n"
        self.children[0].result_label.text = paragraph


class Questionnaire(AppContainer):
    screens = ObjectProperty()
    footer = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Questionnaire, self).__init__(**kwargs)
        self.close_dispatcher = kwargs['close_dispatcher']


    def show(self):
        self.screens.current = "intro"
        self.footer.start_button.bind(on_press=self.next_screen)
        return self

    def next_screen(self, *args):
        self.screens.current = self.screens.next()
        if self.screens.current_screen.name == 'conclusion':
            self.footer.start_button.unbind(on_press=self.next_screen)
            self.footer.start_button.bind(on_press=self.close)
            self.footer.start_button.show()
            self.footer.start_button.text = "Close X"
        else:
            self.footer.start_button.hide()
            self.footer.start_button.text = "Next >"


    def close(self, *args):
        self.close_dispatcher.dispatch_close()

    def answer_handler(self, *args):
        self.footer.start_button.show()


class QuestionnaireApp(App):
    def __init__(self, **kwargs):
        super(QuestionnaireApp, self).__init__(**kwargs)
        self.answer_dispatcher = AnswerDispatcher()
        self.close_dispatcher = CloseAppDispatcher()
        self.close_dispatcher.bind(on_close=self.close_app)

    def build(self):
        self._register_classes()
        questionnaire = Questionnaire(close_dispatcher=self.close_dispatcher)
        self.answer_dispatcher.bind(on_answered=questionnaire.answer_handler)
        return questionnaire.show()

    def close_app(self, *args):
        exit()

    def _register_classes(self):
        qprog = re.compile("Question", re.IGNORECASE)
        cprog = re.compile("Conclusion", re.IGNORECASE)
        for class_name in CONTAINER_CLASSES:
            if qprog.match(class_name):
                globals()[class_name] = type(class_name, (Question,), {'dispatcher': self.answer_dispatcher})
            elif cprog.match(class_name):
                globals()[class_name] = type(class_name, (Result,), {'dispatcher': self.answer_dispatcher})
            else:
                globals()[class_name] = type(class_name, (Container,), {})


if __name__ == '__main__':
    QuestionnaireApp().run()


