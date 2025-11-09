from pydantic import BaseModel, HttpUrl,Field
from sqlalchemy import Text
from typing import Optional,List
from datetime import datetime



class CartBase(BaseModel):
    title:str
    cover_image:HttpUrl
    source: Optional[List[str]] = []# type: ignore
    category:str 


class NewsCartCreate(BaseModel):
    id:str
    title: str
    cover_image: HttpUrl 
    source: Optional[List[str]] = [] #type: ignore 
    category:str
    time_of_release:datetime




class NewsCartRead(BaseModel):
    id:str
    title: str
    cover_image: HttpUrl
    source:Optional[list[str]] = []
    category: str
    time_of_release: datetime

    class Config:
        orm_mode = True


class DetailCreate(BaseModel):
    description: str
    cart_id: str

    class Config:
        orm_mode = True

class CreateNewsInNepali(BaseModel):
    title: str
    description: str
    cart_id: str



class DetailRead(BaseModel):
    id: int
    description: str


    class Config:
        orm_mode = True