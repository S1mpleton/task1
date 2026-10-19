from pydantic import BaseModel, Field, EmailStr, ConfigDict


class CreateUser(BaseModel):
    name: str = Field(default="Guest")
    email: EmailStr = Field(...)
    password: str = Field(...)

class ResponseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(default="Guest")
    email: EmailStr = Field(...)

class TokenData(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)

