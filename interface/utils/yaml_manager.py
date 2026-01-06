import yaml
import copy
import os

class YAMLManager:
    def __init__(self, yaml_path, default_path=None):
        self.yaml_path = yaml_path
        self.default_path = default_path or yaml_path
        self.data = {}
        self.defaults = {}

    def load(self):
        """Charge param.yml et le default si disponible"""
        # Charger le YAML principal
        if not os.path.exists(self.yaml_path):
            print(f"⚠️ param.yml introuvable : {self.yaml_path}")
            return False

        with open(self.yaml_path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f) or {}

        # Charger defaults si fichier disponible
        if os.path.exists(self.default_path):
            with open(self.default_path, "r", encoding="utf-8") as f:
                self.defaults = yaml.safe_load(f) or {}
        else:
            self.defaults = copy.deepcopy(self.data)

        return True

    def save(self):
        try:
            with open(self.yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(self.data, f, sort_keys=False, allow_unicode=True)
            return True
        except Exception as e:
            print("Erreur sauvegarde YAML:", e)
            return False

    def reset_to_default(self):
        self.data = copy.deepcopy(self.defaults)

    def get_section(self, section):
        return self.data.setdefault(section, {})
