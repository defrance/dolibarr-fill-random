from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import yaml
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from translations.get_translation import get_translation

# Langues disponibles : code interne -> nom affiché
AVAILABLE_LANGUAGES = {
    "fr_FR": "Français",
    "en_US": "English",
}

# Champs spéciaux qui utilisent un Spinner au lieu d'un TextInput
SPINNER_FIELDS = {
    "lang": {
        "values": list(AVAILABLE_LANGUAGES.values()),
        "to_display": lambda v: AVAILABLE_LANGUAGES.get(str(v), str(v)),
        "to_yaml": lambda displayed: next(
            (code for code, label in AVAILABLE_LANGUAGES.items() if label == displayed),
            "fr_FR"
        ),
    },
    "tests": {
        "values": ["True", "False"],
        "to_display": lambda v: "True" if str(v).lower() in ("true", "1") else "False",
        "to_yaml": lambda displayed: True if displayed == "True" else False,
    },
}


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputs = {}
        self.param_file = None
        self.param_sample_file = None
        self._current_lang = None  # langue au moment du dernier build

    def set_paths(self, param_file, param_sample_file):
        self.param_file = param_file
        self.param_sample_file = param_sample_file

    def on_enter(self):
        # Recharge les tabs seulement si la langue a changé depuis le dernier build
        params = self.load_params()
        lang = params.get("others", {}).get("lang", "fr_FR")
        if lang != self._current_lang:
            Clock.schedule_once(lambda dt: self.build_tabs(), 0.1)
        
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

    # ------------------------------------------------------------------
    # Construction des onglets
    # ------------------------------------------------------------------

    def build_tabs(self):
        self.ids.main_container.clear_widgets()
        self.inputs.clear()
        params = self.load_params()

        # Mémorise la langue utilisée pour ce build
        self._current_lang = params.get("others", {}).get("lang", "fr_FR")

        tabs = TabbedPanel(do_default_tab=False)
        tabs.background_color = (0.9, 0.9, 0.9, 1)

        sections = [
            ("tab_configuration", "others"),
            ("tab_elements", "elements"),
            ("tab_categories", "categories"),
            ("tab_contacts", "contacts"),
            ("tab_project", "project"),
            ("tab_supplier", "supplier"),
            ("tab_hrm", "hrm"),
            ("tab_products", "products"),
            ("tab_timekeepr", "timekeepr"),
        ]

        for tab_name, section_key in sections:
            section_data = params.get(section_key, {})
            if section_data:
                tab = TabbedPanelItem(text=self.tr(tab_name))
                scroll = self.build_scroll_container(section_data)
                tab.add_widget(scroll)
                tabs.add_widget(tab)

        self.ids.main_container.add_widget(tabs)

    def build_scroll_container(self, data_dict):
        scroll = ScrollView(do_scroll_x=False)

        params = self.load_params()
        lang = params.get("others", {}).get("lang", "fr_FR")

        main_container = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None)
        main_container.bind(minimum_height=main_container.setter("height"))

        with main_container.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            rect = Rectangle(pos=main_container.pos, size=main_container.size)
        main_container.bind(pos=lambda inst, val: setattr(rect, 'pos', inst.pos))
        main_container.bind(size=lambda inst, val: setattr(rect, 'size', inst.size))

        nb_col = 2
        columns = []
        for i in range(nb_col):
            column = GridLayout(cols=3, spacing=10, size_hint_y=None, size_hint_x=0.5)
            column.bind(minimum_height=column.setter("height"))
            columns.append(column)
            main_container.add_widget(column)

        row_height = 40
        items = list(data_dict.items())

        for idx, (name, value) in enumerate(items):
            col_idx = idx % nb_col

            translated_name = get_translation(name, lang)

            lbl = Label(
                text=translated_name,
                color=(0, 0, 0, 1),
                size_hint_y=None,
                size_hint_x=0.6,
                halign='right',
                valign='middle',
                text_size=(None, None)
            )
            lbl.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1] + 10))

            # --- Champ spécial : Spinner ---
            if name in SPINNER_FIELDS:
                spec = SPINNER_FIELDS[name]
                displayed_value = spec["to_display"](value)
                widget = Spinner(
                    text=displayed_value,
                    values=spec["values"],
                    size_hint_y=None,
                    height=row_height,
                    size_hint_x=0.15,
                    background_color=(0.4, 0.6, 0.9, 1),
                    color=(1, 1, 1, 1),
                )

            # --- Champ standard : TextInput entier ---
            else:
                widget = TextInput(
                    text=str(value),
                    multiline=False,
                    input_filter="int",
                    size_hint_y=None,
                    height=row_height,
                    size_hint_x=0.15,
                    halign="center"
                )

            btn = Button(
                text=self.tr("btn_field_reset"),
                size_hint_y=None,
                height=row_height,
                size_hint_x=0.25,
                font_size='12sp'
            )
            btn.bind(on_release=lambda b, n=name: self.reset_field(n))

            columns[col_idx].add_widget(lbl)
            columns[col_idx].add_widget(widget)
            columns[col_idx].add_widget(btn)

            self.inputs[name] = widget

        scroll.add_widget(main_container)
        return scroll

    # ------------------------------------------------------------------
    # Sauvegarde / Reset
    # ------------------------------------------------------------------

    def _get_widget_value(self, name, widget):
        """Lit la valeur d'un widget (TextInput ou Spinner) et la convertit."""
        if name in SPINNER_FIELDS:
            spec = SPINNER_FIELDS[name]
            return spec["to_yaml"](widget.text)
        else:
            try:
                return int(widget.text) if widget.text.strip() else 0
            except ValueError:
                return 0

    def save_elements(self):
        params = self.load_params()

        for name, widget in self.inputs.items():
            value = self._get_widget_value(name, widget)

            for section in ["elements", "categories", "contacts", "others", "project",
                            "supplier", "hrm", "products", "timekeepr"]:
                if section in params and name in params[section]:
                    params[section][name] = value
                    break

        self.save_params(params)

    def reset_field(self, name):
        if name not in self.inputs:
            return
        widget = self.inputs[name]
        if name in SPINNER_FIELDS:
            spec = SPINNER_FIELDS[name]
            widget.text = spec["values"][0]
        else:
            widget.text = "0"
        self.save_elements()

    def reset_all(self):
        for name, widget in self.inputs.items():
            if name in SPINNER_FIELDS:
                spec = SPINNER_FIELDS[name]
                widget.text = spec["values"][0]
            else:
                widget.text = "0"
        self.save_elements()

    def load_defaults(self):
        defaults = self.load_default_params()
        if not defaults:
            return

        params = self.load_params()
        connection = params.get("connection", {})

        for section in ["elements", "categories", "contacts", "others", "project",
                        "supplier", "hrm", "products", "timekeepr"]:
            if section in defaults:
                params[section] = defaults[section]

        params["connection"] = connection
        self.save_params(params)

        self.inputs.clear()
        self.build_tabs()

    def execute_script(self):
        self.save_elements()
        self.manager.current = "logs"