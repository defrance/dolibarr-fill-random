from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
import os
import subprocess
import sys

from screens import ConfigScreen, MainScreen, LogScreen

# PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARAM_SAMPLE_FILE = os.path.join(BASE_DIR, "param-sample.yml")
PARAM_FILE = os.path.join(BASE_DIR, "param.yml")
KV_DIR = os.path.join(os.path.dirname(__file__), "kv")
SCRIPT_PATH = os.path.join(BASE_DIR, "dolibarr_fill_random.py")

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

        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dolibarr_fill_random.py")
        base_dir = os.path.dirname(script_path)

        if not os.path.exists(script_path):
            log_callback(f"Erreur : le script n'existe pas : {script_path}")
            return

        try:
        
            subprocess.Popen([sys.executable, script_path], cwd=base_dir)
            log_callback(f"Script lancé : {script_path}")
        except Exception as e:
            log_callback(f"Erreur lors de l'exécution : {e}")

if __name__ == "__main__":
    FillRandomApp().run()
