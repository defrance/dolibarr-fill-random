from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import yaml
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from translations.get_translation import get_translation


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputs = {}
        self.param_file = None
        self.param_sample_file = None

    def set_paths(self, param_file, param_sample_file):
        self.param_file = param_file
        self.param_sample_file = param_sample_file

    def on_enter(self):
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

    def build_tabs(self):
        self.ids.main_container.clear_widgets()
        params = self.load_params()

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

            ti = TextInput(
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
            columns[col_idx].add_widget(ti)
            columns[col_idx].add_widget(btn)

            self.inputs[name] = ti

        scroll.add_widget(main_container)
        return scroll

    def save_elements(self):
        params = self.load_params()

        for name, ti in self.inputs.items():
            try:
                value = int(ti.text) if ti.text.strip() else 0
            except ValueError:
                value = 0

            for section in ["elements", "categories", "contacts", "others", "project",
                            "supplier", "hrm", "products", "timekeepr"]:
                if section in params and name in params[section]:
                    params[section][name] = value
                    break

        self.save_params(params)

    def reset_field(self, name):
        if name in self.inputs:
            self.inputs[name].text = "0"
            self.save_elements()

    def reset_all(self):
        for ti in self.inputs.values():
            ti.text = "0"
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