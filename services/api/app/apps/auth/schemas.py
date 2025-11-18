from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class User(Base):
    id: int
    username: str
    email: str


class UserRegister(Base):
    username: str
    email: str
    password: str


class UserLogin(Base):
    email: str
    password: str


class Token(Base):
    access_token: str
    token_type: str
