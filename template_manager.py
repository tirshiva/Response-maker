import os
import json

def list_templates(template_dir='templates'):
    """List all template JSON files in the directory."""
    return [f for f in os.listdir(template_dir) if f.endswith('.json')]

def load_template(filename, template_dir='templates'):
    """Load a template JSON file and return its contents as a dict."""
    with open(os.path.join(template_dir, filename), 'r', encoding='utf-8') as f:
        return json.load(f) 