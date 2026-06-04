import json

def save_project(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def load_project(path):
    with open(path, "r") as f:
        return json.load(f)