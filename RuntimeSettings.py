import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "data/runtime-settings.json")


def load_runtime_settings():
    with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)