import yaml
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """YAML 설정 파일을 로드합니다."""
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def get_config(self, key: str = None):
        """설정값을 가져옵니다."""
        if key is None:
            return self.config
        return self.config.get(key)
