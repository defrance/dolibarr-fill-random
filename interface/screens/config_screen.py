from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle
import requests
import os
import yaml
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from translations.get_translation import get_translation

AVAILABLE_LANGUAGES = {
    "fr_FR": "Français",
    "en_US": "English",
}


class ConfigScreen(Screen):
    status_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_dir = None
        self.param_file = None
        self.param_sample_file = None
        self._built = False

    def set_paths(self, base_dir, param_file, param_sample_file):
        self.base_dir = base_dir
        self.param_file = param_file
        self.param_sample_file = param_sample_file

    def on_enter(self):
        self.build_ui()
        self.load_config()


    def load_params(self):
        if not self.param_file or not os.path.exists(self.param_file):
            return {}
        with open(self.param_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def save_params(self, data: dict):
        with open(self.param_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)

    def load_default_params(self):
        if not self.param_sample_file or not os.path.exists(self.param_sample_file):
            return {}
        with open(self.param_sample_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def tr(self, key):
        try:
            params = self.load_params()
            lang = params.get("others", {}).get("lang", "fr_FR")
        except Exception:
            lang = "fr_FR"
        return get_translation(key, lang)

    def get_lang_code(self):
        displayed = self.lang_spinner.text
        for code, label in AVAILABLE_LANGUAGES.items():
            if label == displayed:
                return code
        return "fr_FR"

    def set_lang_spinner(self, lang_code):
        self.lang_spinner.text = AVAILABLE_LANGUAGES.get(lang_code, "Français")

    def _invalidate_main_screen_lang(self):
        try:
            main = self.manager.get_screen("main")
            main._current_lang = None
        except Exception:
            pass


    # Construction de l'UI (appelée à chaque on_enter)

    def build_ui(self):
        self.clear_widgets()

        # Fond blanc
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda i, v: setattr(self._bg_rect, 'pos', i.pos))
        self.bind(size=lambda i, v: setattr(self._bg_rect, 'size', i.size))

        root = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Titre
        root.add_widget(Label(
            text=self.tr("config_title"),
            size_hint_y=None, height=50,
            font_size='22sp', bold=True,
            color=(0.2, 0.2, 0.2, 1)
        ))

        # Grille des champs
        grid = GridLayout(
            cols=2, spacing=15,
            size_hint_y=None,
            row_default_height=48,
            row_force_default=True,
            height=48 * 4 + 15 * 3,
            padding=(10, 0)
        )
        grid.bind(minimum_height=grid.setter('height'))

        def make_label(text):
            lbl = Label(
                text=text, size_hint_x=0.3,
                color=(0.3, 0.3, 0.3, 1),
                halign='right', valign='middle'
            )
            lbl.bind(size=lambda i, v: setattr(i, 'text_size', i.size))
            return lbl

        def make_input(input_filter=None, disabled=False):
            ti = TextInput(
                multiline=False, size_hint_x=0.7,
                background_color=(0.92, 0.92, 0.92, 1) if disabled else (0.98, 0.98, 0.98, 1),
                foreground_color=(0.5, 0.5, 0.5, 1) if disabled else (0.2, 0.2, 0.2, 1),
                padding=(10, 10), disabled=disabled
            )
            if input_filter:
                ti.input_filter = input_filter
            return ti

        # Champs
        self.token_input = make_input()
        self.version_input = make_input(input_filter='int')
        self.url_input = make_input()

        self.lang_spinner = Spinner(
            text='Français',
            values=list(AVAILABLE_LANGUAGES.values()),
            size_hint_x=0.7, size_hint_y=None, height=44,
            background_color=(0.4, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )

        grid.add_widget(make_label(self.tr("api_token")))
        grid.add_widget(self.token_input)
        grid.add_widget(make_label(self.tr("dolibarr_version")))
        grid.add_widget(self.version_input)
        grid.add_widget(make_label(self.tr("base_url")))
        grid.add_widget(self.url_input)
        grid.add_widget(make_label(self.tr("language")))
        grid.add_widget(self.lang_spinner)

        root.add_widget(grid)

        # Boutons
        btn_bar = BoxLayout(
            orientation='horizontal', spacing=12,
            size_hint_y=None, height=55, padding=(10, 0)
        )

        def make_btn(text, color, callback):
            btn = Button(
                text=text, background_color=color,
                background_normal='', font_size='14sp', color=(1, 1, 1, 1)
            )
            btn.bind(on_release=lambda b: callback())
            return btn

        btn_bar.add_widget(make_btn(self.tr("btn_defaults"),  (0.4, 0.6, 0.9, 1), self.load_default_config))
        btn_bar.add_widget(make_btn(self.tr("btn_reset"),     (0.9, 0.5, 0.3, 1), self.reset_config))
        btn_bar.add_widget(make_btn(self.tr("btn_save"),      (0.3, 0.7, 0.4, 1), self.save_config))
        btn_bar.add_widget(make_btn(self.tr("btn_connect"),   (0.2, 0.5, 0.8, 1), self.test_connection))

        root.add_widget(btn_bar)

        # Label de statut
        self.status_label = Label(
            text="", size_hint_y=None, height=50,
            color=(0.3, 0.3, 0.3, 1), font_size='13sp'
        )
        root.add_widget(self.status_label)
        root.add_widget(Label())  # spacer

        self.add_widget(root)


    def _set_status(self, text):
        self.status_label.text = text

    def load_config(self):
        params = self.load_params()
        conn = params.get("connection", {})
        others = params.get("others", {})
        self.token_input.text = str(conn.get("apitoken", ""))
        self.version_input.text = str(conn.get("dol_version", ""))
        self.url_input.text = str(conn.get("urlbase", ""))
        self.set_lang_spinner(others.get("lang", "fr_FR"))

    def save_config(self):
        token = self.token_input.text.strip()
        version = self.version_input.text.strip()
        urlbase = self.url_input.text.strip().rstrip("/") + "/"
        lang = self.get_lang_code()

        if not token or not version or not urlbase:
            self._set_status(self.tr("error_fields_required"))
            return

        try:
            params = self.load_params()
            params["connection"] = {
                "apitoken": token,
                "dol_version": int(version),
                "urlbase": urlbase
            }
            if "others" not in params:
                params["others"] = {}
            params["others"]["lang"] = lang
            self.save_params(params)
            self.build_ui()
            self.load_config()
            self._set_status(self.tr("status_saved"))
            self._invalidate_main_screen_lang()
        except Exception as e:
            self._set_status(f"{self.tr('error_save')} : {e}")

    def reset_config(self):
        self.token_input.text = ""
        self.version_input.text = ""
        self.url_input.text = ""
        self.set_lang_spinner("fr_FR")
        self._set_status(self.tr("status_reset"))

    def load_default_config(self):
        defaults = self.load_default_params()
        if not defaults:
            self._set_status(self.tr("status_no_defaults"))
            return

        conn = defaults.get("connection", {})
        others = defaults.get("others", {})
        self.token_input.text = str(conn.get("apitoken", ""))
        self.version_input.text = str(conn.get("dol_version", ""))
        self.url_input.text = str(conn.get("urlbase", ""))
        self.set_lang_spinner(others.get("lang", "fr_FR"))
        self._set_status(self.tr("status_defaults_loaded"))

    def test_connection(self):
        token = self.token_input.text.strip()
        version = self.version_input.text.strip()
        urlbase = self.url_input.text.strip().rstrip("/") + "/"
        lang = self.get_lang_code()

        if not token or not version or not urlbase:
            self._set_status(self.tr("error_fields_required"))
            return

        headers = {"DOLAPIKEY": token, "Accept": "application/json"}

        try:
            r = requests.get(f"{urlbase}status", headers=headers, timeout=5)
            if r.status_code == 200:
                self._set_status(self.tr("status_connected"))

                params = self.load_params()
                params["connection"] = {
                    "apitoken": token,
                    "dol_version": int(version),
                    "urlbase": urlbase
                }
                if "others" not in params:
                    params["others"] = {}
                params["others"]["lang"] = lang
                self.save_params(params)
                self._invalidate_main_screen_lang()
                self.manager.current = "main"

            else:
                self._set_status(f"{self.tr('error_api')} ({r.status_code})")
        except requests.exceptions.RequestException as e:
            self._set_status(f"{self.tr('error_connection')} : {e}")