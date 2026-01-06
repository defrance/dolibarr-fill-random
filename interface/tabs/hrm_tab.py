from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

class HRMTab(TabbedPanelItem):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__(**kwargs)
        self.text = "RH"
        self.yaml_manager = yaml_manager
        self.inputs = {}

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        fields = {
            "nb_holiday": "Nb jours de congé",
            "nb_expense_report": "Nb notes de frais",
            "nb_expense_report_line_max": "Max lignes par note"
        }

        for key, label_text in fields.items():
            layout.add_widget(self._create_field(key, label_text))

        self.add_widget(layout)

    def _create_field(self, key, label_text):
        box = BoxLayout(size_hint_y=None, height=40)
        box.add_widget(Label(text=label_text, size_hint_x=0.7))
        ti = TextInput(multiline=False, input_filter="int", size_hint_x=0.3)
        self.inputs[key] = ti
        box.add_widget(ti)
        return box

    def update_fields(self):
        data = self.yaml_manager.get_section("hrm")
        for key, ti in self.inputs.items():
            ti.text = str(data.get(key, 0))

    def collect_values(self):
        data = self.yaml_manager.get_section("hrm")
        for key, ti in self.inputs.items():
            data[key] = int(ti.text) if ti.text else 0
