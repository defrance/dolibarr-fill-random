from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView


class ProductsTab(TabbedPanelItem):
    def __init__(self, yaml_manager, **kwargs):
        super().__init__(**kwargs)
        self.text = "Produits"
        self.yaml_manager = yaml_manager

        self.inputs_products = {}
        self.inputs_productlots = {}

        # ScrollView
        scroll = ScrollView()

        # Contenu scrollable
        layout = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=10,
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter("height"))

        # ===== SECTION 1 : Nouveaux produits =====
        layout.add_widget(self._section_title("Nombre de nouveaux :"))

        self._add_fields(
            layout,
            {
                "new_product": "Produit(s)",
            },
            self.inputs_products
        )

        # ===== SECTION 2 : Paramètres produits =====
        layout.add_widget(self._section_title("Paramètres produits"))

        self._add_fields(
            layout,
            {
                "nb_sale_price_history_max": "Historique max des prix de vente",
                "pourcentage_aug_price_max": "Pourcentage max d’augmentation",
                "new_stock_movement": "Mouvement(s) de stock",
            },
            self.inputs_products
        )

        # ===== SECTION 3 : Paramètres des lots =====
        layout.add_widget(self._section_title("Paramètres des lots"))

        self._add_fields(
            layout,
            {
                "nb_lot_by_product_max": "Lots max par produit",
            },
            self.inputs_productlots
        )

        scroll.add_widget(layout)
        self.add_widget(scroll)

    # ---------- UI helpers ----------
    def _section_title(self, text):
        return Label(
            text=text,
            bold=True,
            font_size="18sp",
            size_hint_y=None,
            height=40
        )

    def _add_fields(self, layout, fields, storage):
        for key, label_text in fields.items():
            layout.add_widget(
                self._create_field(key, label_text, storage)
            )

    def _create_field(self, key, label_text, storage):
        box = BoxLayout(
            size_hint_y=None,
            height=40,
            spacing=10
        )

        box.add_widget(
            Label(text=label_text, size_hint_x=0.7)
        )

        ti = TextInput(
            multiline=False,
            input_filter="int",
            size_hint_x=0.3
        )

        storage[key] = ti
        box.add_widget(ti)
        return box

    # ---------- YAML → UI ----------
    def update_fields(self):
        products = self.yaml_manager.get_section("products")
        for key, ti in self.inputs_products.items():
            ti.text = str(products.get(key, 0))

        productlots = self.yaml_manager.get_section("productlots")
        for key, ti in self.inputs_productlots.items():
            ti.text = str(productlots.get(key, 0))

    # ---------- UI → YAML ----------
    def collect_values(self):
        products = self.yaml_manager.get_section("products")
        for key, ti in self.inputs_products.items():
            products[key] = int(ti.text) if ti.text else 0

        productlots = self.yaml_manager.get_section("productlots")
        for key, ti in self.inputs_productlots.items():
            productlots[key] = int(ti.text) if ti.text else 0
