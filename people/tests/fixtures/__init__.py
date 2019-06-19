# -*- coding: utf-8 -*-
import json
import os

FIXTURE_DIR_PATH = os.path.dirname(__file__)


def load_json_file_content(path):
    with open(path, "r") as f:
        result = json.load(f)
    return result
