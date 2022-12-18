import json
from pathlib import Path

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from pyrogram import Client
from pyrogram.errors.exceptions.unauthorized_401 import SessionPasswordNeeded


# number = +79171418765
# api_id = 7640328
# api_hash = e8fecf361251bc064b959f193f04a308


class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)


class Auth(Screen):
    def __init__(self, **kwargs):
        super(Auth, self).__init__(**kwargs)
        self.btn_start = Button(text="Start", font_size=35, size_hint=(.4, .15),
                                pos_hint={"center_x": 0.5, "center_y": 0.4})
        self.btn_start.bind(on_press=self.start)
        self.add_widget(self.btn_start)

    def start(self, event):
        fle = Path('sessions.json')
        fle.touch(exist_ok=True)
        if self.load_js() == "":
            self.auth()
        else:
            self.auth_with_session()

    def auth(self):
        self.clear_widgets()
        self.add_widget(
            Label(text="Авторизация", font_size=40, size_hint=(.45, .1), pos_hint={'center_x': .5, 'y': .85}))
        self.add_widget(Label(text='Number', font_size=21, size_hint=(.45, .1), pos_hint={'x': .05, 'y': .7}))
        self.number = TextInput(multiline=False, size_hint=(.45, .07), pos_hint={'x': .5, 'y': .7})
        self.add_widget(self.number)
        self.add_widget(Label(text='Api_ID', font_size=21, size_hint=(.45, .1), pos_hint={'x': .05, 'y': .55}))
        self.api_id = TextInput(multiline=False, size_hint=(.45, .07), pos_hint={'x': .5, 'y': .55})
        self.add_widget(self.api_id)
        self.add_widget(Label(text='Api_HASH', font_size=21, size_hint=(.45, .1), pos_hint={'x': .05, 'y': .4}))
        self.api_hash = TextInput(multiline=False, size_hint=(.45, .07), pos_hint={'x': .5, 'y': .4})
        self.add_widget(self.api_hash)
        self.btn = Button(text='Authorization', size_hint=(.35, .08), pos_hint={'center_x': .5, 'y': .1})
        self.add_widget(self.btn)
        self.btn.bind(on_press=self.submit)

    def submit(self, event):
        if self.number.text == "" and self.api_id.text == "" and self.api_hash.text == "":
            return 0
        self.remove_widget(self.btn)
        self.add_widget(Label(text="Code", font_size=25, size_hint=(.45, .1), pos_hint={'x': .05, 'y': .25}))
        self.code = TextInput(multiline=False, size_hint=(.2, .05), pos_hint={'center_x': .5, 'y': .28})
        self.add_widget(self.code)
        self.auth = Button(text='Confirm', size_hint=(.24, .05), pos_hint={'center_x': .8, 'y': .28})
        self.auth.bind(on_press=self.confirm_auth)
        self.add_widget(self.auth)
        App.get_running_app().session = Client("1", api_id=self.api_id.text, api_hash=self.api_hash.text)
        App.get_running_app().session.connect()
        self.hash_code = App.get_running_app().session.send_code(self.number.text).phone_code_hash

    def confirm_auth(self, event):
        info = {
            "name": "1",
            "number": self.number.text,
            "api_id": self.api_id.text,
            "api_hash": self.api_hash.text
        }
        with open("sessions.json", "w") as f:
            f.write(json.dumps(info))
        App.get_running_app().json = info
        try:
            App.get_running_app().session.sign_in(self.number.text, self.hash_code, self.code.text)
            App.get_running_app().login()
        except SessionPasswordNeeded as e:
            self.remove_widget(self.auth)
            self.add_widget(Label(text="2Fa Pass", font_size=25, size_hint=(.45, .1), pos_hint={'x': .05, 'y': .1}))
            self.passw = TextInput(multiline=False, size_hint=(.2, .05), pos_hint={'center_x': .5, 'y': .13})
            self.add_widget(self.passw)
            self.log_pass = Button(text='Confirm', size_hint=(.24, .05), pos_hint={'center_x': .8, 'y': .13})
            self.log_pass.bind(on_press=self.confirm_auth_2fa)
            self.add_widget(self.log_pass)

    def confirm_auth_2fa(self, event):
        App.get_running_app().session.check_password(self.passw.text)
        App.get_running_app().session.sign_in(self.number.text, self.hash_code, self.code.text)
        App.get_running_app().login()

    def load_js(self):
        with open("sessions.json", "r") as f:
            lines = f.read()
        if lines == "":
            return ""
        else:
            json_file = json.loads(lines)
            App.get_running_app().json = json_file
            return json_file

    def auth_with_session(self):
        App.get_running_app().auth()
        self.manager.current = "menu"


class Menu(Screen):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.add_widget(
            Label(text="Hi", font_size=40, size_hint=(.45, .1), pos_hint={'center_x': .5, 'y': .85}))
        print(App.get_running_app().session.get_me())

class Settings(Screen):
    pass


class Spam(Screen):
    pass


class Invite(Screen):
    pass


class MainApp(App):
    session = None
    json_file = ""

    def build(self):
        self.screen = ScreenManagement()
        self.screen.add_widget(Auth(name="auth"))
        self.screen.current = "auth"
        return self.screen

    def auth(self):
        with open("sessions.json", "r") as f:
            lines = f.read()
        self.json_file = json.loads(lines)
        name = self.json_file["name"]
        api_id = self.json_file["api_id"]
        api_hash = self.json_file["api_hash"]
        self.session = Client(name=name, api_id=api_id, api_hash=api_hash)
        self.session.start()
        self.screen.add_widget(Menu(name="menu"))
        self.screen.add_widget(Settings(name="sett"))
        self.screen.add_widget(Spam(name="spam"))
        self.screen.add_widget(Invite(name="invite"))

    def login(self):
        self.screen.add_widget(Menu(name="menu"))
        self.screen.add_widget(Settings(name="sett"))
        self.screen.add_widget(Spam(name="spam"))
        self.screen.add_widget(Invite(name="invite"))
        self.screen.current = "menu"

if __name__ == '__main__':
    MainApp().run()
