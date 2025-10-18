from yh_auth import AuthManager
from yh_auth import AuthConfig
from yh_auth import AuthParameters
from yh_auth import AuthRole
class TestAuthManager:
    config = AuthConfig(
        accessSecretKey="access_secret_key",
        refreshSecretKey="refresh_secret_key",
        accessExpHours=1,
        refreshExpDays=1
    )
    parameters = AuthParameters(
        name="test",
        email="test@test.com",
        userId=1,
        role=AuthRole.USER
    )

    def test_get_access_token(self):
        auth_manager = AuthManager(self.config)
        access_token = auth_manager.getAccessToken(self.parameters)
        assert access_token is not None

    def test_verify_access_token(self):
        auth_manager = AuthManager(self.config)
        access_token = auth_manager.getAccessToken(self.parameters)
        verified_token = auth_manager.verifyAccessToken(access_token)
        assert verified_token is not None

    def test_get_refresh_token(self):
        auth_manager = AuthManager(self.config)
        refresh_token = auth_manager.getRefreshToken(self.parameters)
        assert refresh_token is not None

    def test_verify_refresh_token(self):
        auth_manager = AuthManager(self.config)
        refresh_token = auth_manager.getRefreshToken(self.parameters)
        verified_token = auth_manager.verifyRefreshToken(refresh_token)
        assert verified_token is not None
    def test_refresh_by_refresh_token(self):
        auth_manager = AuthManager(self.config)
        refresh_token = auth_manager.getRefreshToken(self.parameters)
        refreshed_token = auth_manager.refreshByRefreshToken(refresh_token)
        assert refreshed_token is not None