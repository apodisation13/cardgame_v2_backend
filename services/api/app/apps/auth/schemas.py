from lib.utils.schemas import Base


class User(Base):
    id: int
    username: str
    email: str


class UserRegisterRequest(Base):
    username: str
    email: str
    password: str


class UserRegisterResponse(Base):
    id: int
    username: str
    email: str


class UserLoginRequest(Base):
    email: str
    password: str


class Token(Base):
    access_token: str
    token_type: str


class UserLoginResponse(Base):
    id: int
    username: str
    email: str
    token: Token


class UserCheckTokenResponse(Base):
    id: int
    email: str
