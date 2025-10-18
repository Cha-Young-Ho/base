# Auth Role Enum
from enum import Enum

class AuthRole(Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"