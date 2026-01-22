from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.clock import Clock
import requests
import os
import yaml

# PATHS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARAM_FILE = os.path.join(BASE_DIR, "param.yml")
KV_DIR = os.path.join(os.path.dirname(__file__), "kv")
Builder.load_file(os.path.join(KV_DIR, "config.kv"))
Builder.load_file(os.path.join(KV_DIR, "main.kv"))

# UTILS

def load_params():
    if not os.path.exists(PARAM_FILE):
        return {}
    with open(PARAM_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_params(data: dict):
    with open(PARAM_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


# CONFIG SCREEN

class ConfigScreen(Screen):
    status_text = StringProperty("")

    def on_enter(self):
        self.load_config()

    def load_config(self):
        params = load_params()
        conn = params.get("connection", {})
        self.ids.token_input.text = conn.get("apitoken", "")
        self.ids.version_input.text = str(conn.get("dol_version", ""))
        self.ids.url_input.text = conn.get("urlbase", "")

    def test_connection(self):
        token = self.ids.token_input.text.strip()
        version = self.ids.version_input.text.strip()
        urlbase = self.ids.url_input.text.strip().rstrip("/") + "/"

        if not token or not version or not urlbase:
            self.status_text = "Tous les champs sont obligatoires"
            return

        headers = {
            "DOLAPIKEY": token,
            "Accept": "application/json"
        }

        try:
            r = requests.get(f"{urlbase}status", headers=headers, timeout=5)
            if r.status_code == 200:
                self.status_text = "Connexion réussie"

                # Sauvegarde config
                params = load_params()
                params["connection"] = {
                    "apitoken": token,
                    "dol_version": int(version),
                    "urlbase": urlbase
                }
                save_params(params)

                # Passage au MainScreen
                self.manager.current = "main"

            else:
                self.status_text = f"Erreur API ({r.status_code})"
        except requests.exceptions.RequestException as e:
            self.status_text = f"Connexion impossible : {e}"

# MAIN SCREEN
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputs = {}

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.build_tabs(), 0.1)

    def build_tabs(self):
        self.ids.main_container.clear_widgets()
        params = load_params()

        tabs = TabbedPanel(do_default_tab=False)
        tabs.background_color = (0.9, 0.9, 0.9, 1)  # fond clair des tabs

        # Elements Tab
        elements_tab = TabbedPanelItem(text="Elements")
        elements_scroll = self.build_scroll_container(params.get("elements", {}))
        elements_tab.add_widget(elements_scroll)
        tabs.add_widget(elements_tab)

        # Categories Tab
        categories_tab = TabbedPanelItem(text="Categories")
        categories_scroll = self.build_scroll_container(params.get("categories", {}))
        categories_tab.add_widget(categories_scroll)
        tabs.add_widget(categories_tab)

        self.ids.main_container.add_widget(tabs)

    def build_scroll_container(self, data_dict):
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(do_scroll_x=False)
        container = GridLayout(cols=3, spacing=5, size_hint_y=None)
        container.bind(minimum_height=container.setter("height"))

        # Fond gris clair
        with container.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.95, 0.95, 0.95, 1)  # gris clair
            rect = Rectangle(pos=container.pos, size=container.size)
        container.bind(pos=lambda inst, val: setattr(rect, 'pos', inst.pos))
        container.bind(size=lambda inst, val: setattr(rect, 'size', inst.size))

        for name, value in data_dict.items():
            lbl = Label(text=name, color=(0, 0, 0, 1), size_hint_y=None, height=30)
            ti = TextInput(text=str(value), multiline=False, input_filter="int", size_hint_y=None, height=30)
            btn = Button(text="Reset", size_hint_y=None, height=30)
            btn.bind(on_release=lambda b, n=name: self.reset_field(n))
            container.add_widget(lbl)
            container.add_widget(ti)
            container.add_widget(btn)
            self.inputs[name] = ti

        scroll.add_widget(container)
        return scroll

    def save_elements(self):
        params = load_params()
        for name, ti in self.inputs.items():
            try:
                if "elements" in params and name in params["elements"]:
                    params["elements"][name] = int(ti.text)
                elif "categories" in params and name in params["categories"]:
                    params["categories"][name] = int(ti.text)
            except ValueError:
                if "elements" in params and name in params["elements"]:
                    params["elements"][name] = 0
                elif "categories" in params and name in params["categories"]:
                    params["categories"][name] = 0
        save_params(params)

    def reset_field(self, name):
        if name in self.inputs:
            self.inputs[name].text = "0"
            self.save_elements()

    def reset_all(self):
        for ti in self.inputs.values():
            ti.text = "0"
        self.save_elements()


# APP

class FillRandomApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ConfigScreen(name="config"))
        sm.add_widget(MainScreen(name="main"))
        return sm

if __name__ == "__main__":
    FillRandomApp().run()
