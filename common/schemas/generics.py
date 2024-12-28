from pydantic import BaseModel


# Generic message
class Message(BaseModel):
    message: str


# Generic Unauthorized
class Unauthorized(BaseModel):
    message: str
    request_id: str
