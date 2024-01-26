from pydantic import BaseModel


class MenuCreate(BaseModel):
    title: str
    description: str


class SubmenuCreate(BaseModel):
    title: str
    description: str


class DishCreate(BaseModel):
    title: str
    description: str
    price: str
