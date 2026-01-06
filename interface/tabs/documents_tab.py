from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

class DocumentsTab(TabbedPanelItem):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__(**kwargs)
        self.text = "Documents"
        self.yaml_manager = yaml_manager
        self.fields = {}

        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.add_widget(self.layout)

        # Créer un champ pour chaque paramètre documents
        docs_params = [
            "new_bill",
            "new_contract",
            "new_fichinter",
            "new_knowledge",
            "new_order",
            "new_proposal",
            "new_ticket"
        ]

        for param in docs_params:
            box = BoxLayout(size_hint_y=None, height=30, spacing=10)
            label = Label(text=param.replace("_", " ").capitalize(), size_hint_x=0.6)
            input_field = TextInput(multiline=False, size_hint_x=0.4)
            box.add_widget(label)
            box.add_widget(input_field)
            self.layout.add_widget(box)
            self.fields[param] = input_field

    # --- Récupérer les valeurs de l'interface ---
    def collect_values(self):
        if "documents" not in self.yaml_manager.data:
            self.yaml_manager.data["documents"] = {}
        for key, widget in self.fields.items():
            try:
                self.yaml_manager.data["documents"][key] = int(widget.text)
            except ValueError:
                self.yaml_manager.data["documents"][key] = 0  # fallback

    # --- Mettre à jour les champs depuis le YAML ---
    def update_fields(self):
        docs_data = self.yaml_manager.data.get("documents", {})
        for key, widget in self.fields.items():
            widget.text = str(docs_data.get(key, 0))
