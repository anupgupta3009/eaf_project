from typing import List,Optional
from pydantic import BaseModel

class ElementsIn(BaseModel):
    name: str
    class Config:
        orm_mode = True

class Elements(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class Commodity(BaseModel):
    id: int
    name: str
    inventory : float
    price : float
    chemical_composition : List[dict]
    class Config:
        orm_mode = True

class CommodityIn(BaseModel):
    name: str
    inventory : float
    price : float
    chemical_composition : List[dict]
    class Config:
        orm_mode = True

class AddComposition(BaseModel):
    commodity_id : int
    element_id: int
    percentage : float
    class Config:
        orm_mode = True

class RemoveComposition(BaseModel):
    commodity_id : int
    element_id: int
    class Config:
        orm_mode = True

class CommodityUpdate(BaseModel):
    id: int
    name: Optional[str]
    inventory : Optional[float]
    price : Optional[float]
    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    name: str
    password: str
    class Config:
        orm_mode = True

class UserIn(BaseModel):
    name: str
    password: str
    class Config:
        orm_mode = True