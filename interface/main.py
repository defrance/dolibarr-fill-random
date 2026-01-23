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
from translations import get_translation

# PATHS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARAM_SAMPLE_FILE = os.path.join(BASE_DIR, "param-sample.yml")
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

def load_default_params():
    if not os.path.exists(PARAM_SAMPLE_FILE):
        return {}
    with open(PARAM_SAMPLE_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# CONFIG SCREEN

class ConfigScreen(Screen):
    status_text = StringProperty("")

    def on_enter(self):
        self.load_config()

    def load_config(self):
        params = load_params()
        conn = params.get("connection", {})
        others = params.get("others", {})
        self.ids.token_input.text = conn.get("apitoken", "")
        self.ids.version_input.text = str(conn.get("dol_version", ""))
        self.ids.url_input.text = conn.get("urlbase", "")
        self.ids.lang_input.text = others.get("lang", "fr_FR")

    def save_config(self):
        """Sauvegarde la configuration sans tester la connexion"""
        token = self.ids.token_input.text.strip()
        version = self.ids.version_input.text.strip()
        urlbase = self.ids.url_input.text.strip().rstrip("/") + "/"
        lang = self.ids.lang_input.text.strip()

        if not token or not version or not urlbase:
            self.status_text = "Tous les champs sont obligatoires"
            return

        try:
            params = load_params()
            params["connection"] = {
                "apitoken": token,
                "dol_version": int(version),
                "urlbase": urlbase
            }
            if "others" not in params:
                params["others"] = {}
            params["others"]["lang"] = lang
            save_params(params)
            self.status_text = "Configuration sauvegardée"
        except Exception as e:
            self.status_text = f"Erreur de sauvegarde : {e}"

    def reset_config(self):
        """Remet à zéro tous les champs de configuration"""
        self.ids.token_input.text = ""
        self.ids.version_input.text = ""
        self.ids.url_input.text = ""
        self.ids.lang_input.text = "fr_FR"
        self.status_text = "Champs réinitialisés"

    def load_default_config(self):
        """Charge les valeurs par défaut depuis param-sample.yml"""
        defaults = load_default_params()
        if not defaults:
            self.status_text = "Aucun fichier de configuration par défaut trouvé"
            return

        conn = defaults.get("connection", {})
        others = defaults.get("others", {})
        self.ids.token_input.text = conn.get("apitoken", "")
        self.ids.version_input.text = str(conn.get("dol_version", ""))
        self.ids.url_input.text = conn.get("urlbase", "")
        self.ids.lang_input.text = others.get("lang", "fr_FR")
        self.status_text = "Valeurs par défaut chargées"

    def test_connection(self):
        token = self.ids.token_input.text.strip()
        version = self.ids.version_input.text.strip()
        urlbase = self.ids.url_input.text.strip().rstrip("/") + "/"
        lang = self.ids.lang_input.text.strip()

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
                if "others" not in params:
                    params["others"] = {}
                params["others"]["lang"] = lang
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

        # Liste des sections à afficher
        sections = [
            ("Elements", "elements"),
            ("Categories", "categories"),
            ("Contacts", "contacts"),
            ("Others", "others"),
            ("Project", "project"),
            ("Supplier", "supplier"),
            ("HRM", "hrm"),
            ("Products", "products")
        ]

        # Créer un onglet pour chaque section
        for tab_name, section_key in sections:
            section_data = params.get(section_key, {})
            if section_data:  # Seulement si la section contient des données
                tab = TabbedPanelItem(text=tab_name)
                scroll = self.build_scroll_container(section_data)
                tab.add_widget(scroll)
                tabs.add_widget(tab)

        self.ids.main_container.add_widget(tabs)

    def build_scroll_container(self, data_dict):
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(do_scroll_x=False)
        
        # Récupérer la langue depuis les paramètres
        params = load_params()
        lang = params.get("others", {}).get("lang", "fr_FR")
        
        # Conteneur principal avec 3 colonnes
        main_container = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None)
        main_container.bind(minimum_height=main_container.setter("height"))
        
        # Fond gris clair
        with main_container.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.95, 0.95, 0.95, 1)  # gris clair
            rect = Rectangle(pos=main_container.pos, size=main_container.size)
        main_container.bind(pos=lambda inst, val: setattr(rect, 'pos', inst.pos))
        main_container.bind(size=lambda inst, val: setattr(rect, 'size', inst.size))

        # Créer 3 colonnes
        columns = []
        for i in range(3):
            column = GridLayout(cols=3, spacing=5, size_hint_y=None, size_hint_x=0.33)
            column.bind(minimum_height=column.setter("height"))
            columns.append(column)
            main_container.add_widget(column)

        # Répartir les éléments sur les 3 colonnes
        row_height = 40
        items = list(data_dict.items())
        for idx, (name, value) in enumerate(items):
            col_idx = idx % 3  # Distribuer de manière équilibrée sur les 3 colonnes
            
            # Utiliser la traduction si disponible
            translated_name = get_translation(name, lang)
            
            lbl = Label(text=translated_name, color=(0, 0, 0, 1), size_hint_y=None, height=30, size_hint_x=0.6, halign='right', valign='middle', text_size=(0, row_height))
            lbl.bind(width=lambda inst, val: setattr(inst, 'text_size', (val, row_height)))

            ti = TextInput(text=str(value), multiline=False, input_filter="int", size_hint_y=None, height=row_height, size_hint_x=0.15, halign = "center")

            btn = Button(text="Reset", size_hint_y=None, height=row_height, size_hint_x=0.25, font_size='12sp')
            btn.bind(on_release=lambda b, n=name: self.reset_field(n))
            
            columns[col_idx].add_widget(lbl)
            columns[col_idx].add_widget(ti)
            columns[col_idx].add_widget(btn)
            
            self.inputs[name] = ti

        scroll.add_widget(main_container)
        return scroll

    # SAVE NEW VALUE IN PARAM.
    def save_elements(self):
        params = load_params()
        
        # Parcourir tous les inputs et les sauvegarder dans la bonne section
        for name, ti in self.inputs.items():
            try:
                value = int(ti.text) if ti.text.strip() else 0
            except ValueError:
                value = 0
            
            # Chercher dans quelle section se trouve ce paramètre
            for section in ["elements", "categories", "contacts", "others", "project", "supplier", "hrm", "products"]:
                if section in params and name in params[section]:
                    params[section][name] = value
                    break
        
        save_params(params)

    # RAZ 
    def reset_field(self, name):
        if name in self.inputs:
            self.inputs[name].text = "0"
            self.save_elements()

    # RAZ ALL
    def reset_all(self):
        for ti in self.inputs.values():
            ti.text = "0"
        self.save_elements()

    # PARAM-DEFAULT

    def load_defaults(self):
        defaults = load_default_params()
        if not defaults:
            return

        params = load_params()

        # Conserver la connexion
        connection = params.get("connection", {})

        # Charger toutes les sections par défaut
        for section in ["elements", "categories", "contacts", "others", "project", "supplier", "hrm", "products", "columngrid"]:
            if section in defaults:
                params[section] = defaults[section]
        
        # Restaurer la connexion
        params["connection"] = connection

        save_params(params)

        self.inputs.clear()
        self.build_tabs()

# APP

class FillRandomApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ConfigScreen(name="config"))
        sm.add_widget(MainScreen(name="main"))
        return sm

if __name__ == "__main__":
    FillRandomApp().run()