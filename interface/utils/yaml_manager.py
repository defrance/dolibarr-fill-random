import yaml
import os


class YAMLManager:
    """Gestionnaire pour lire/écrire les fichiers YAML"""
    
    def __init__(self, filename='param.yml'):
        self.filename = filename
        self.default_filename = 'param_default.yml'
        self.data = self.load_default_data()
    
    def load_default_data(self):
        """Charge les valeurs par défaut depuis param_default.yml"""
        if os.path.exists(self.default_filename):
            try:
                with open(self.default_filename, 'r', encoding='utf-8') as f:
                    default_data = yaml.safe_load(f)
                    return default_data if default_data else {}
            except Exception as e:
                print(f"✗ Erreur lors du chargement du fichier par défaut: {e}")
        return {}
    
    def reset_to_default(self):
        """Remet toutes les données aux valeurs par défaut"""
        self.data = self.load_default_data()
    
    def load(self):
        """Charge les données depuis le fichier YAML"""
        if not os.path.exists(self.filename):
            print(f"⚠ Fichier {self.filename} introuvable")
            return False
    
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                loaded_data = yaml.safe_load(f)
                print(f"Données chargées: {loaded_data}") 
                if loaded_data:
                    self.data = loaded_data
                    print(f"Sections trouvées: {list(self.data.keys())}") 
                    return True
        except Exception as e:
            print(f"✗ Erreur lors du chargement: {e}")
            return False
    
    def save(self):
        """Sauvegarde les données dans le fichier YAML"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde: {e}")
            return False
    
    def get_section(self, section_name):
        """Récupère une section spécifique"""
        return self.data.get(section_name, {})
    
    def update_section(self, section_name, section_data):
        """Met à jour une section"""
        self.data[section_name] = section_data


