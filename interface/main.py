from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
import os

from screens import ConfigScreen, MainScreen, LogScreen

# PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARAM_SAMPLE_FILE = os.path.join(BASE_DIR, "param-sample.yml")
PARAM_FILE = os.path.join(BASE_DIR, "param.yml")
KV_DIR = os.path.join(os.path.dirname(__file__), "kv")

# Charger les fichiers KV
Builder.load_file(os.path.join(KV_DIR, "config.kv"))
Builder.load_file(os.path.join(KV_DIR, "main.kv"))
Builder.load_file(os.path.join(KV_DIR, "log.kv"))


class FillRandomApp(App):
    def build(self):
        sm = ScreenManager()
        
        config_screen = ConfigScreen(name="config")
        main_screen = MainScreen(name="main")
        log_screen = LogScreen(name="logs")
        
        config_screen.set_paths(BASE_DIR, PARAM_FILE, PARAM_SAMPLE_FILE)
        main_screen.set_paths(PARAM_FILE, PARAM_SAMPLE_FILE)
        log_screen.set_paths(PARAM_FILE)
        log_screen.set_script_runner(self.execute_main_script)
        
        sm.add_widget(config_screen)
        sm.add_widget(main_screen)
        sm.add_widget(log_screen)
        
        return sm
    
    def execute_main_script(self, log_callback, params):
        import time
        
        log_callback("Initialisation...")
        time.sleep(1)
        
        log_callback("Connexion à l'API...")
        connection = params.get("connection", {})
        log_callback(f"  URL: {connection.get('urlbase', 'N/A')}")
        log_callback(f"  Version: {connection.get('dol_version', 'N/A')}")
        time.sleep(1)
        
        sections = ["elements", "categories", "contacts", "others", 
                   "project", "supplier", "hrm", "products"]
        
        for section in sections:
            if section in params:
                log_callback(f"\nTraitement de la section '{section}'...")
                section_data = params[section]
                
                for key, value in section_data.items():
                    if value > 0:
                        log_callback(f"  - {key}: {value} éléments")
                        time.sleep(0.2)
        
        log_callback("\nTraitement terminé!")


if __name__ == "__main__":
    FillRandomApp().run()
