import json
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIGS_DIR = os.path.join(PROJECT_ROOT, '..', 'configs')


def load_config():
    # Minimal loader — expand as needed
    schema_path = os.path.join(PROJECT_ROOT, '..', 'configs', 'schema.json')
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except FileNotFoundError:
        schema = {}
    return {'CLAIM_SCHEMA': schema}
