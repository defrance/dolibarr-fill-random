from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
import requests
import os
import yaml
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from translations.get_translation import get_translation


class ConfigScreen(Screen):
    status_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_dir = None
        self.param_file = None
        self.param_sample_file = None

    def set_paths(self, base_dir, param_file, param_sample_file):
        self.base_dir = base_dir
        self.param_file = param_file
        self.param_sample_file = param_sample_file

    def on_enter(self):
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

    def load_config(self):
        params = self.load_params()
        conn = params.get("connection", {})
        others = params.get("others", {})
        self.ids.token_input.text = str(conn.get("apitoken", ""))
        self.ids.version_input.text = str(conn.get("dol_version", ""))
        self.ids.url_input.text = str(conn.get("urlbase", ""))
        self.ids.lang_input.text = str(others.get("lang", "fr_FR"))

    def save_config(self):
        token = self.ids.token_input.text.strip()
        version = self.ids.version_input.text.strip()
        urlbase = self.ids.url_input.text.strip().rstrip("/") + "/"
        lang = self.ids.lang_input.text.strip()

        if not token or not version or not urlbase:
            self.status_text = self.tr("error_fields_required")
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
            self.status_text = self.tr("status_saved")
        except Exception as e:
            self.status_text = f"{self.tr('error_save')} : {e}"

    def reset_config(self):
        self.ids.token_input.text = ""
        self.ids.version_input.text = ""
        self.ids.url_input.text = ""
        self.ids.lang_input.text = "fr_FR"
        self.status_text = self.tr("status_reset")

    def load_default_config(self):
        defaults = self.load_default_params()
        if not defaults:
            self.status_text = self.tr("status_no_defaults")
            return

        conn = defaults.get("connection", {})
        others = defaults.get("others", {})
        self.ids.token_input.text = str(conn.get("apitoken", ""))
        self.ids.version_input.text = str(conn.get("dol_version", ""))
        self.ids.url_input.text = str(conn.get("urlbase", ""))
        self.ids.lang_input.text = str(others.get("lang", "fr_FR"))
        self.status_text = self.tr("status_defaults_loaded")

    def test_connection(self):
        token = self.ids.token_input.text.strip()
        version = self.ids.version_input.text.strip()
        urlbase = self.ids.url_input.text.strip().rstrip("/") + "/"
        lang = self.ids.lang_input.text.strip()

        if not token or not version or not urlbase:
            self.status_text = self.tr("error_fields_required")
            return

        headers = {
            "DOLAPIKEY": token,
            "Accept": "application/json"
        }

        try:
            r = requests.get(f"{urlbase}status", headers=headers, timeout=5)
            if r.status_code == 200:
                self.status_text = self.tr("status_connected")

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

                self.manager.current = "main"

            else:
                self.status_text = f"{self.tr('error_api')} ({r.status_code})"
        except requests.exceptions.RequestException as e:
            self.status_text = f"{self.tr('error_connection')} : {e}"