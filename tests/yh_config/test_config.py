import pytest
from yh_config import ConfigManager
from pytest_mock import MockerFixture

class TestConfigManager:
    def test_load_config_success(self, mocker: MockerFixture):
        """Config 로드 성공 테스트"""
        # Mock YAML 데이터
        mock_config = {
            'database': {
                'mysql': {
                    'main': {
                        'host': 'localhost',
                        'port': 3306,
                        'user': 'testuser',
                        'password': 'testpassword',
                        'database': 'testdb'
                    }
                }
            }
        }
        
        # Mock 파일 읽기
        mock_open = mocker.mock_open(read_data='database:\n  mysql:\n    main:\n      host: localhost')
        mocker.patch("builtins.open", mock_open)
        mocker.patch("yaml.safe_load", return_value=mock_config)
        
        # ConfigManager 생성
        config_manager = ConfigManager("test_config.yaml")
        
        # 검증
        assert config_manager.config == mock_config
        mock_open.assert_called_once_with("test_config.yaml", 'r', encoding='utf-8')

    def test_load_config_file_not_found(self, mocker: MockerFixture):
        """Config 파일이 없을 때 테스트"""
        # 파일이 없을 때 예외 발생
        mocker.patch("builtins.open", side_effect=FileNotFoundError("File not found"))
        
        with pytest.raises(FileNotFoundError):
            ConfigManager("nonexistent.yaml")

    def test_load_config_with_yaml_mock(self, mocker: MockerFixture):
        """YAML Mock을 사용한 테스트"""
        mock_yaml_data = {'test': 'value'}
        mocker.patch("yaml.safe_load", return_value=mock_yaml_data)
        
        # Mock 파일 읽기
        mock_open = mocker.mock_open(read_data='test: value')
        mocker.patch("builtins.open", mock_open)
        
        config_manager = ConfigManager("test.yaml")
        
        assert config_manager.get_config() == mock_yaml_data
        assert config_manager.get_config('test') == 'value'
