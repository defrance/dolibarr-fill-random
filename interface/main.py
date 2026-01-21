from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

import requests
import os
import yaml

# ========================
# PATHS
# ========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARAM_FILE = os.path.join(BASE_DIR, "param.yml")

KV_DIR = os.path.join(os.path.dirname(__file__), "kv")
Builder.load_file(os.path.join(KV_DIR, "config.kv"))
Builder.load_file(os.path.join(KV_DIR, "main.kv"))


# ========================
# UTILS
# ========================

def load_params():
    if not os.path.exists(PARAM_FILE):
        return {}
    with open(PARAM_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_params(data: dict):
    with open(PARAM_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


# ========================
# CONFIG SCREEN
# ========================

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
                self.status_text = "Connexion réussie ✅"

                # sauvegarde uniquement la section connection
                params = load_params()
                params["connection"] = {
                    "apitoken": token,
                    "dol_version": int(version),
                    "urlbase": urlbase
                }
                save_params(params)

                # passage à l'écran main
                self.manager.current = "main"
            else:
                self.status_text = f"Erreur API ({r.status_code})"
        except requests.exceptions.RequestException as e:
            self.status_text = f"Connexion impossible : {e}"


# ========================
# MAIN SCREEN
# ========================

class MainScreen(Screen):

    def on_enter(self):
        self.load_elements()

    def load_elements(self):
        params = load_params()
        elements = params.get("elements", {})

        for key, widget in self.ids.items():
            if key.startswith("input_"):
                name = key.replace("input_", "")
                widget.text = str(elements.get(name, 0))

    def save_elements(self):
        params = load_params()
        params.setdefault("elements", {})

        for key, widget in self.ids.items():
            if key.startswith("input_"):
                name = key.replace("input_", "")
                try:
                    params["elements"][name] = int(widget.text)
                except ValueError:
                    params["elements"][name] = 0

        save_params(params)


# ========================
# APP
# ========================

class FillRandomApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(ConfigScreen(name="config"))
        sm.add_widget(MainScreen(name="main"))
        return sm


if __name__ == "__main__":
    FillRandomApp().run()
