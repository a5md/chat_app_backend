from enum import Enum

class User_role(str, Enum):
    USER = "user"
    ADMIN = "admin"