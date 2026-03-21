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
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "dolibarr_fill_random.py"
        )
        base_dir = os.path.dirname(script_path)

        if not os.path.exists(script_path):
            log_callback(f"✗ Script introuvable : {script_path}")
            return

        # Variables d'environnement pour forcer le mode unbuffered
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            process = subprocess.Popen(
                [sys.executable, "-u", script_path],
                cwd=base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,              # pas de buffer du tout
                encoding="utf-8",
                errors="replace",
                env=env
            )

            log_callback(f"▶ Script lancé\n")

            for line in iter(process.stdout.readline, ''):
                log_callback(line.rstrip("\n"))

            process.stdout.close()
            process.wait()

            if process.returncode == 0:
                log_callback("\n✓ Exécution terminée avec succès!")
            else:
                log_callback(f"\n✗ Le script s'est terminé avec le code {process.returncode}")

        except Exception as e:
            log_callback(f"\n✗ Erreur lors de l'exécution : {e}")


if __name__ == "__main__":
    FillRandomApp().run()