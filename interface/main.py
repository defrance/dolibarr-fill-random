from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
import os
import subprocess
import sys

from tabs.categories_tab import CategoriesTab
from tabs.contacts_tab import ContactsTab
from tabs.elements_tab import ElementsTab
from tabs.others_tab import OthersTab
from tabs.project_tab import ProjectTab
from tabs.supplier_tab import SupplierTab
from tabs.configuration_tab import ConfigurationsTab

from utils.yaml_manager import YAMLManager



class MainInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.yaml_manager = YAMLManager('param.yml')
        base_dir = os.path.dirname(os.path.dirname(__file__))
        yaml_path = os.path.join(base_dir, 'param.yml')

        self.yaml_manager = YAMLManager(yaml_path)
        self.yaml_manager.load()

        # Titre
        title = Label(
            text='Dolifaker',
            size_hint=(1, 0.08),
            font_size='24sp',
            bold=True
        )
        self.add_widget(title)
        
         # Panel d'onglets
        self.tab_panel = TabbedPanel(
            do_default_tab=False,
            size_hint=(1, 0.82)
        )
        
        # Créer les onglets
        self.tabs = {
            'categories': CategoriesTab(self.yaml_manager),
            'contacts': ContactsTab(self.yaml_manager),
            'elements': ElementsTab(self.yaml_manager),
            'others': OthersTab(self.yaml_manager),
            'project': ProjectTab(self.yaml_manager),
            'supplier': SupplierTab(self.yaml_manager),
            'configurations': ConfigurationsTab(self.yaml_manager),
        }
        
        # Ajouter les onglets au panel
        for tab in self.tabs.values():
            self.tab_panel.add_widget(tab)
        
        self.add_widget(self.tab_panel)
        
        # Boutons d'action
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=10
        )
        
        btn_save = Button(
            text='Sauvegarder',
            on_press=self.save_all,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        button_layout.add_widget(btn_save)
        
        btn_load = Button(
            text='Charger',
            on_press=self.load_all,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        button_layout.add_widget(btn_load)
        
        btn_reset = Button(
            text='Réinitialiser',
            on_press=self.reset_all,
            background_color=(0.8, 0.4, 0.2, 1)
        )
        button_layout.add_widget(btn_reset)
        
        btn_run = Button(
            text='Exécuter Dolifaker',
            on_press=self.run_script,
            background_color=(0.6, 0.8, 0.2, 1)
            )
        button_layout.add_widget(btn_run)

        self.add_widget(button_layout)
        
        # Charger les valeurs au démarrage
        self.load_all()
    
    def save_all(self, instance=None):
        """Sauvegarde toutes les sections"""
        # Collecter les données de tous les onglets
        for section_name, tab in self.tabs.items():
            tab.collect_values()
        
        # Sauvegarder
        if self.yaml_manager.save():
            print("✓ Fichier param.yml sauvegardé avec succès!")
        else:
            print("✗ Erreur lors de la sauvegarde")
    
    def load_all(self, instance=None):
        """Charge toutes les sections"""
        if self.yaml_manager.load():
            # Mettre à jour tous les onglets
            for tab in self.tabs.values():
                tab.update_fields()
            print("✓ Fichier param.yml chargé avec succès!")
        else:
            print("✗ Erreur lors du chargement (fichier par défaut utilisé)")
    
    def reset_all(self, instance=None):
        """Réinitialise tous les onglets"""
        self.yaml_manager.reset_to_default()
        for tab in self.tabs.values():
            tab.update_fields()
        print("✓ Tous les champs ont été réinitialisés aux valeurs par défaut")

    def run_script(self, instance=None):
        
        # Chemin absolu du script
        base_dir = os.path.dirname(os.path.dirname(__file__))
        script_path = os.path.join(base_dir, 'dolibarr_fill_random.py')

        if not os.path.exists(script_path):
            print(f"✗ Script introuvable : {script_path}")
            return

        print(f"▶ Exécution du script : {script_path}")

        # Avant de lancer, sauvegarder les données YAML à jour
        self.save_all()

        # Exécuter le script dans le même environnement Python
        try:
            subprocess.run([sys.executable, script_path], check=True)
            print("✓ Script exécuté avec succès !")
        except subprocess.CalledProcessError as e:
            print(f"✗ Erreur pendant l'exécution : {e}")

class Main(App):
    def build(self):
        Window.size = (900, 650)
        return MainInterface()

if __name__ == '__main__':
    Main().run()