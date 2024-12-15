from sqlmodel import Field, Relationship, SQLModel


# Generic message
class Message(SQLModel):
    message: str


# Generic Unauthorized
class Unauthorized(SQLModel):
    message: str
    request_id: str
