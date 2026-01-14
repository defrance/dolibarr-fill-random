from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

class SupplierTab(TabbedPanelItem):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__(**kwargs)
        self.text = "Fournisseurs"
        self.yaml_manager = yaml_manager
        self.inputs = {}

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        fields = {
            "create_supplier": "Créer fournisseur (0/1)",
            "nb_supplier_product": "Nb max fournisseur par produit",
            "nb_supplier_product_price": "Nb max prix par fournisseur",
            "new_supplier_bill": "Nouvelles factures fournisseurs",
            "new_supplier_order": "Nouvelles commandes fournisseurs"
        }

        for key, label_text in fields.items():
            layout.add_widget(self._create_field(key, label_text))

        self.add_widget(layout)

    def _create_field(self, key, label_text):
        box = BoxLayout(size_hint_y=None, height=40)
        box.add_widget(Label(text=label_text, size_hint_x=0.7))
        ti = TextInput(multiline=False, size_hint_x=0.3)
        self.inputs[key] = ti
        box.add_widget(ti)
        return box

    def update_fields(self):
        data = self.yaml_manager.get_section("supplier")
        for key, ti in self.inputs.items():
            ti.text = str(data.get(key, 0))

    def collect_values(self):
        data = self.yaml_manager.get_section("supplier")
        for key, ti in self.inputs.items():
            value = ti.text
            if value.isdigit():
                data[key] = int(value)
            elif value.lower() in ("true", "false"):
                data[key] = value.lower() == "true"
            else:
                data[key] = value
