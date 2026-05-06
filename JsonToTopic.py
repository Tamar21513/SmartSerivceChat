import json
import copy

with open("./data/json_templates.json", "r", encoding="utf-8") as f:
    templates = json.load(f)

def get_json(issue):
    json_template = copy.deepcopy(templates[issue])
    return json_template