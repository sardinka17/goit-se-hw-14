from datetime import date

from pydantic import BaseModel, Field


class ContactModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=100)
    email: str = Field(max_length=100)
    phone_number: str = Field(max_length=15)
    birthday_date: date


class ContactCreate(ContactModel):
    pass


class ContactUpdate(ContactModel):
    pass


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday_date: date

    class Config:
        from_attributes = True
