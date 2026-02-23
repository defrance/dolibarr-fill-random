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
            params = self.load_params()
            if not params:
                self.add_log("Erreur: Aucun paramètre trouvé")
                return
            # script_runner est responsable de streamer les logs via add_log
            self.script_runner(self.add_log, params)
        except Exception as e:
            self.add_log(f"\n✗ Erreur lors de l'exécution: {str(e)}")

    def add_log(self, message):
        Clock.schedule_once(lambda dt: self._update_log(message), 0)

    def _update_log(self, message):
        self.log_text += message + "\n"
        if hasattr(self.ids, 'log_scroll'):
            self.ids.log_scroll.scroll_y = 0

    def load_params(self):
        if not self.param_file or not os.path.exists(self.param_file):
            return {}
        with open(self.param_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def go_back(self):
        self.manager.current = "main"

    def clear_logs(self):
        self.log_text = ""