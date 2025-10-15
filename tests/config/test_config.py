import pytest
from config.config_manager import ConfigManager

class TestConfigManager:
    def test_load_config_success(self, mocker):
        """Config 로드 성공 테스트"""
        # Mock YAML 데이터
        mock_yaml_content = """
        database:
          url: mysql://localhost:3306/testdb
        app:
          debug: true
          port: 8000
        """
        
        # Mock 설정
        mock_open = mocker.mock_open(read_data=mock_yaml_content)
        mocker.patch('builtins.open', mock_open)
        
        # 테스트 실행
        config_manager = ConfigManager("test.yaml")
        
        # 검증
        assert config_manager.config is not None
        assert config_manager.config["database"]["url"] == "mysql://localhost:3306/testdb"
        assert config_manager.config["app"]["debug"] == True
        assert config_manager.config["app"]["port"] == 8000
        
        # 함수 호출 확인
        mock_open.assert_called_once_with("test.yaml", 'r')
    
    def test_load_config_file_not_found(self, mocker):
        """파일이 없을 때 테스트"""
        # FileNotFoundError 시뮬레이션
        mocker.patch('builtins.open', side_effect=FileNotFoundError)
        
        # 테스트 실행 및 검증
        with pytest.raises(FileNotFoundError):
            ConfigManager("nonexistent.yaml")
    
    def test_load_config_with_yaml_mock(self, mocker):
        """yaml.safe_load도 함께 모킹"""
        # Mock 설정
        mock_yaml_data = {"database": {"url": "mysql://localhost"}}
        mocker.patch('yaml.safe_load', return_value=mock_yaml_data)
        
        mock_open = mocker.mock_open()
        mocker.patch('builtins.open', mock_open)
        
        # 테스트 실행
        config_manager = ConfigManager("test.yaml")
        
        # 검증
        assert config_manager.config == mock_yaml_data