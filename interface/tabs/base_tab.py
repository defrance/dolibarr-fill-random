from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from widgets.param_field import ParamField



class BaseTab(TabbedPanelItem):
    """Classe de base pour tous les onglets"""
    
    def __init__(self, section_name, yaml_manager, **kwargs):
        super().__init__(**kwargs)
        self.text = section_name.upper()
        self.section_name = section_name
        self.yaml_manager = yaml_manager
        self.param_fields = {}
        
        # Créer le layout
        self.create_layout()
    
    def create_layout(self):
        """Crée le layout de l'onglet"""
        scroll = ScrollView(size_hint=(1, 1))
    
        self.fields_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=20,
            size_hint_y=None
        )
        self.fields_layout.bind(minimum_height=self.fields_layout.setter('height'))
    
    # Récupérer les données de la section
        section_data = self.yaml_manager.get_section(self.section_name)
        print(f"🔍 Section '{self.section_name}': {section_data}")  # ← AJOUTEZ CECI
    
    # Créer les champs
        for param_name, param_value in section_data.items():
            field = ParamField(param_name, param_value)
            self.param_fields[param_name] = field
            self.fields_layout.add_widget(field)
    
        print(f"✓ {len(self.param_fields)} champs créés pour '{self.section_name}'")  # ← ET CECI
    
        scroll.add_widget(self.fields_layout)
        self.add_widget(scroll)
    
    def collect_values(self):
        """Collecte les valeurs et met à jour le YAML manager"""
        section_data = {}
        for param_name, field in self.param_fields.items():
            section_data[param_name] = field.get_value()
        self.yaml_manager.update_section(self.section_name, section_data)
    
    def update_fields(self):
        """Met à jour les champs avec les valeurs du YAML manager"""
        section_data = self.yaml_manager.get_section(self.section_name)
        for param_name, field in self.param_fields.items():
            if param_name in section_data:
                field.set_value(section_data[param_name])
    
    def reset_fields(self):
        """Réinitialise tous les champs à 0"""
        for field in self.param_fields.values():
            field.set_value(0)