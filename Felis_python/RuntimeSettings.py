import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "data/runtime-settings.json")


# Load and return the runtime settings JSON file as a dict
def load_runtime_settings():
    with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)