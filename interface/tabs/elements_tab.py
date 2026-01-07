from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView


class ElementsTab(TabbedPanelItem):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__(**kwargs)
        self.text = "Éléments"
        self.yaml_manager = yaml_manager
        self.inputs = {}

        # ScrollView
        scroll = ScrollView()

        # Contenu scrollable
        layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10,
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter("height"))

        # 🔹 Titre
        layout.add_widget(
            Label(
                text="Nombre de nouveaux(elles)",
                bold=True,
                font_size="18sp",
                size_hint_y=None,
                height=40
            )
        )

        fields = {
            "new_user": "Utilisateur(s)",
            "new_bank": "Banque(s)",
            "new_client": "Client(s)",
            "new_warehouse": "Entrepôt(s)",
            "new_bill": "Facture(s)",
            "new_contract": "Contrat(s)",
            "new_fichinter": "Fiche(s) intervention(s)",
            "new_knowledge": "Knowledge",
            "new_order": "Commande(s)",
            "new_proposal": "Proposition(s)",
            "new_ticket": "Ticket(s)",
        }

        for key, label_text in fields.items():
            layout.add_widget(self._create_field(key, label_text))

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def _create_field(self, key, label_text):
        box = BoxLayout(
            size_hint_y=None,
            height=40,
            spacing=10
        )

        box.add_widget(
            Label(
                text=label_text,
                size_hint_x=0.7
            )
        )

        ti = TextInput(
            multiline=False,
            input_filter="int",
            size_hint_x=0.3
        )

        self.inputs[key] = ti
        box.add_widget(ti)
        return box

    # ---------- YAML → UI ----------
    def update_fields(self):
        data = self.yaml_manager.get_section("elements")
        for key, ti in self.inputs.items():
            ti.text = str(data.get(key, 0))

    # ---------- UI → YAML ----------
    def collect_values(self):
        data = self.yaml_manager.get_section("elements")
        for key, ti in self.inputs.items():
            data[key] = int(ti.text) if ti.text else 0
