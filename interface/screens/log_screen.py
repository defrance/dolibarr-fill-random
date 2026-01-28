from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.clock import Clock
import threading
import os
import yaml

class LogScreen(Screen):
    log_text = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param_file = None
        self.script_runner = None
        
    def set_paths(self, param_file):
        self.param_file = param_file
        
    def set_script_runner(self, script_runner):
        self.script_runner = script_runner
    
    def on_enter(self):
        self.log_text = "Démarrage de l'exécution...\n"
        # Lancer l'exécution du script dans un thread séparé
        Clock.schedule_once(lambda dt: self.start_execution(), 0.5)
    
    def start_execution(self):
        if self.script_runner:
            thread = threading.Thread(target=self.run_script)
            thread.daemon = True
            thread.start()
        else:
            self.add_log("Erreur: Aucun script configuré pour l'exécution")
    
    def run_script(self):
        try:
            self.add_log("Chargement des paramètres...")
            params = self.load_params()
            
            if not params:
                self.add_log("Erreur: Aucun paramètre trouvé")
                return
            
            self.add_log("Paramètres chargés avec succès")
            self.add_log(f"URL: {params.get('connection', {}).get('urlbase', 'Non défini')}")
            
            if self.script_runner:
                self.script_runner(self.add_log, params)
            
            self.add_log("\n✓ Exécution terminée avec succès!")
            
        except Exception as e:
            self.add_log(f"\n✗ Erreur lors de l'exécution: {str(e)}")
    
    def add_log(self, message):
        Clock.schedule_once(lambda dt: self._update_log(message), 0)
    
    def _update_log(self, message):
        self.log_text += message + "\n"
        # Auto-scroll vers le bas
        if hasattr(self.ids, 'log_scroll'):
            self.ids.log_scroll.scroll_y = 0
    
    def load_params(self):
        if not os.path.exists(self.param_file):
            return {}
        with open(self.param_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    
    def go_back(self):
        self.manager.current = "main"
    
    def clear_logs(self):
        self.log_text = ""
