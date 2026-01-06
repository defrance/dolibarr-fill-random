from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
import os
import subprocess
import sys

# Import YAMLManager et Tabs
from utils.yaml_manager import YAMLManager
from tabs.categories_tab import CategoriesTab
from tabs.contacts_tab import ContactsTab
from tabs.elements_tab import ElementsTab
from tabs.others_tab import OthersTab
from tabs.project_tab import ProjectTab
from tabs.supplier_tab import SupplierTab
from tabs.hrm_tab import HRMTab
from tabs.products_tab import ProductsTab
from tabs.productlots_tab import ProductLotsTab
from tabs.documents_tab import DocumentsTab

# --- Logger pour rediriger stdout/stderr vers TextInput ---
class Logger:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        if message.strip() == "":
            return
        self.text_widget.text += message + "\n"
        # Scroll automatique vers le bas
        self.text_widget.cursor = (0, len(self.text_widget.text))

    def flush(self):
        pass

# --- MainInterface ---
class MainInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 10
        self.padding = 10

        # Chemins relatifs pour YAML
        base_dir = os.path.dirname(os.path.dirname(__file__))  # parent de interface/
        yaml_path = os.path.join(base_dir, "param.yml")
        default_path = os.path.join(base_dir, "param_default.yml")

        self.yaml_manager = YAMLManager(yaml_path, default_path)
        self.yaml_manager.load()

        self._build_ui()
        self.load_all()

        # Redirection stdout/stderr vers TextInput
        sys.stdout = Logger(self.log_output)
        sys.stderr = Logger(self.log_output)

    # --- UI ---
    def _build_ui(self):
        # Titre
        self.add_widget(Label(
            text="fill-random",
            font_size="26sp",
            size_hint_y=0.1,
            bold=True
        ))

        # Onglets
        self.tab_panel = TabbedPanel(do_default_tab=False, size_hint_y=0.6)
        self.tabs = {
            "categories": CategoriesTab(self.yaml_manager),
            "contacts": ContactsTab(self.yaml_manager),
            "elements": ElementsTab(self.yaml_manager),
            "documents": DocumentsTab(self.yaml_manager),
            "project": ProjectTab(self.yaml_manager),
            "supplier": SupplierTab(self.yaml_manager),
            "hrm": HRMTab(self.yaml_manager),
            "products": ProductsTab(self.yaml_manager),
            "productlots": ProductLotsTab(self.yaml_manager),
            "others": OthersTab(self.yaml_manager),
        }

        for tab in self.tabs.values():
            self.tab_panel.add_widget(tab)

        self.add_widget(self.tab_panel)

        # Boutons
        button_layout = BoxLayout(size_hint_y=0.08, spacing=10)

        btn_load = Button(text="Charger", on_press=self.load_all, background_color=(0.2,0.6,0.8,1))
        btn_save = Button(text="Sauvegarder", on_press=self.save_all, background_color=(0.2,0.8,0.2,1))
        btn_reset = Button(text="Réinitialiser", on_press=self.reset_all, background_color=(0.8,0.4,0.2,1))
        btn_run = Button(text="Exécuter", on_press=self.run_script, background_color=(0.6,0.8,0.2,1))
        btn_clear = Button(text="Effacer log", on_press=self.clear_log, background_color=(0.5,0.5,0.5,1))

        for btn in [btn_load, btn_save, btn_reset, btn_run, btn_clear]:
            button_layout.add_widget(btn)

        self.add_widget(button_layout)

        # Zone de logs
        self.log_output = TextInput(
            size_hint_y=0.25,
            readonly=True,
            background_color=(0,0,0,1),
            foreground_color=(1,1,1,1)
        )
        self.add_widget(self.log_output)

    # --- Fonction bouton Effacer log ---
    def clear_log(self, instance):
        self.log_output.text = ""

    # --- Actions ---
    def load_all(self, *args):
        if self.yaml_manager.load():
            for tab in self.tabs.values():
                tab.update_fields()
            print("✓ param.yml chargé avec succès")
        else:
            print("⚠️ Erreur lors du chargement du YAML")

    def save_all(self, *args):
        for tab in self.tabs.values():
            tab.collect_values()
        if self.yaml_manager.save():
            print("✓ param.yml sauvegardé avec succès")
        else:
            print("⚠️ Erreur lors de la sauvegarde du YAML")

    def reset_all(self, *args):
        self.yaml_manager.reset_to_default()
        for tab in self.tabs.values():
            tab.update_fields()
        print("✓ Tous les champs réinitialisés aux valeurs par défaut")

    def run_script(self, *args):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        script_path = os.path.join(base_dir, "dolibarr_fill_random.py")

        self.save_all()

        if not os.path.exists(script_path):
            print(f"✗ Script introuvable : {script_path}")
            return

        try:
            subprocess.run([sys.executable, script_path], check=True)
            print("✓ Script exécuté avec succès !")
        except subprocess.CalledProcessError as e:
            print(f"✗ Erreur pendant l'exécution : {e}")

# --- Application ---
class Main(App):
    def build(self):
        Window.size = (900, 650)
        return MainInterface()

if __name__ == "__main__":
    Main().run()
