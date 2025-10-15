import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)

    def load_config(self, config_path: str):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)