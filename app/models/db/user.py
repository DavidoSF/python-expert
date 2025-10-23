from pydantic import BaseModel, Field
from enum import Enum

class UserRole(str, Enum):
    subscriber = "subscriber"
    administrator = "administrator"

class User(BaseModel):
    id: int
    name: str
    role: UserRole